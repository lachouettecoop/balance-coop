__version__ = "0.1.0"

import os

from dotmap import DotMap
from ruamel.yaml import YAML
from validx import Bool, Dict, List, Str, Any

CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/cfg/config.yml")


SCHEMA = Dict(
    {
        "odoo": Dict(
            {
                "url": Str(),
                "db": Str(),
                "user": Str(),
                "passwd": Str(),
                "categories": Dict(extra=(Str(), List(Any()))),
                "unp": List(Str()),
            }
        ),
        "printer": Dict({"ip": Str()}),
        "scale": Dict({"ip": Str()}),
        "core": Dict(
            {
                "allow_all_origins": Bool(),
                "cors_allowed_origins": Str(),
                "mock_scale": Bool(),
                "mock_printer": Bool(),
            },
            defaults={
                "allow_all_origins": False,
                "cors_allowed_origins": "http://localhost:5000",
                "mock_scale": False,
                "mock_printer": False,
            },
        ),
    },
    defaults={
        "odoo": {},
        "printer": {},
        "scale": {},
        "core": {},
    },
)


def _config():
    yaml = YAML(typ="safe")
    with open(CONFIG_PATH) as f:
        return DotMap(SCHEMA(yaml.load(f)), _dynamic=False)


config = _config()
