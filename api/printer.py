import logging
import math
import socket
import time
from datetime import datetime

from escpos.printer import Network
from flask import abort

from api import config

RETRY_NB = 3


# Network close is called on __del__ and could raise OSError
def _close(self):
    """ Close TCP connection """
    if self.device is not None:
        try:
            self.device.shutdown(socket.SHUT_RDWR)
            self.device.close()
        except OSError:
            pass


Network.close = _close


def print_product_label(product, nb, weight, discount=0.0, cut=False, retry=0):
    if config.core.mock_printer:
        logging.info(
            f"{product.get('name')} | nb: {nb} | weight: {weight} "
            f"| discount: {discount} | cut: {cut}"
        )
        return
    if not config.printer.ip:
        abort(400, description="Printer not configured")
    try:
        printer = Network(config.printer.ip, timeout=10)
        printer.set(align="center", bold=True)
        if product and 0 <= weight < 100:
            name = product.get("name")
            bio = product.get("bio", False)
            title = f"{name}{' BIO' if bio else ''} - {weight:.3f} kg"
            if nb > 0:
                title = f"{nb}) {title}"
            printer.textln(title)

            lst_price = product.get("lst_price")
            price = lst_price * weight
            printer.textln(f"{lst_price:.3f} €/kg  / {price:.3f} €  *")

            if discount > 0.0:
                printer.ln()
                printer.set(align="center", bold=True, double_width=True, double_height=True)
                printer.textln(f"Réduction à appliquer: -{discount}%")
                printer.set(align="center", bold=True)

            product_id = product.get("id")
            if product_id:
                # <260><Product ID><Weight><CheckSum> / <3digits><4digits><5digits><1digit>
                cg = math.floor(weight * 1000)  # grams
                barcode = f"{product.get('barcode')[0:7]}{cg:05d}"
                printer.ln()
                printer.barcode(barcode, "EAN13", height=128, width=2)
            else:
                printer.set(align="center", bold=True, double_width=True, double_height=True)
                printer.ln()
                printer.textln(f"Quantité: {weight}")
                printer.set(align="center", bold=True)
                if product.get("barcode"):
                    printer.ln()
                    printer.barcode(product.get("barcode"), "EAN13", height=128, width=2)

            printer.ln()
            printer.textln("---")
            printer.ln()
        if cut:
            printer.image(img_source="logo.jpg")
            printer.textln("* Les prix seront calculés en caisse")
            printer.textln("Seul le poid est encodé sur le code-barres")
            printer.ln()
            printer.textln(datetime.now().strftime("%m/%d/%Y - %H:%M"))
            printer.cut()
        printer.close()
    except Exception as e:
        logging.error(e)
        retry += 1
        if retry < RETRY_NB:
            time.sleep(1)
            print_product_label(product, nb, weight, discount, cut, retry)
        else:
            abort(400, description="Too many retries")
