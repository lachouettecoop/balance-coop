import atexit
import logging
import os
from logging.config import dictConfig

from flask import Flask, jsonify, request, send_file
from flask_socketio import SocketIO, emit

from api import config
from api.odoo import variable_weight_products
from api.printer import print_product_label
from api.scale import Scale

STATIC_PATH = os.getenv("STATIC_PATH", "./client/dist/")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(levelname)s] %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)
logging.getLogger("werkzeug").setLevel(logging.WARN)

app = Flask(__name__, static_folder=STATIC_PATH)
socket_io = SocketIO(app, cors_allowed_origins=config.core.cors_allowed_origins)
scale = {
    "clients_nb": 0,
    "scale": None,
}


@app.route("/products")
def products():
    _products = variable_weight_products()
    return jsonify(_products)


@app.route("/print_label", methods=["POST"])
def print_label():
    data = request.json
    weight = data.get("weight", 0.0)
    weight_ok = scale["scale"].check_weight(weight)
    # TODO: pop-up if not weight_ok
    print_product_label(
        data.get("product", {}),
        data.get("nb", 0),
        weight,
        data.get("discount", 0.0),
        data.get("cut", False),
    )
    return jsonify({"print": "ok"})


@app.route("/ping")
def ping():
    return jsonify({"name": "balance-coop", "status": "ok"})


@app.after_request
def allow_all_origins(response):
    if config.core.allow_all_origins:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
    return response


@socket_io.on("connect")
def on_connect():
    logging.info("Connected")
    global scale
    if scale.get("clients_nb", 0) == 0:
        scale["scale"] = Scale(socket_io)
        scale["scale"].start()
        scale["clients_nb"] = 0
    scale["clients_nb"] += 1
    emit(
        "scale_status",
        scale["scale"].status,
    )


@socket_io.on("disconnect")
def on_disconnect():
    logging.info("Disconnected ...")
    global scale
    if scale.get("clients_nb", 0) == 1 and scale.get("scale"):
        scale["scale"].stop()
        scale["scale"] = None
    scale["clients_nb"] -= 1


@atexit.register
def shut_scale_down():
    if scale.get("scale"):
        scale["scale"].stop()
        scale["scale"] = None
    scale["clients_nb"] = 0


@app.route("/")
def web():
    index_path = os.path.join(app.static_folder, "index.html")
    return send_file(index_path)


# Everything not declared before (not a Flask route / API endpoint)...
@app.route("/<path:path>")
def route_frontend(path):
    # ...could be a static file needed by the front end that
    # doesn't use the `static` path (like in `<script src="bundle.js">`)
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    # ...or should be handled by the SPA's "router" in front end
    else:
        index_path = os.path.join(app.static_folder, "index.html")
        return send_file(index_path)


def main():
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
