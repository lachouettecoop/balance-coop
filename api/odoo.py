import json
import logging
import os
import re
import ssl
import xmlrpc.client
from datetime import datetime
from typing import Dict, List, AnyStr

from api import config

unp = [re.compile(p, re.IGNORECASE) for p in config.odoo.unp]

CONTEXT = os.getenv("NO_SSL")
DATA_PATH = os.getenv("DATA_PATH", "./data/odoo.json")


class OdooAPI:
    def __init__(self):
        try:
            common_proxy_url = "{}/xmlrpc/2/common".format(config.odoo.url)
            object_proxy_url = "{}/xmlrpc/2/object".format(config.odoo.url)
            context = ssl._create_unverified_context() if CONTEXT else None
            self.common = xmlrpc.client.ServerProxy(
                common_proxy_url,
                context=context,
            )
            self.uid = self.common.authenticate(
                config.odoo.db, config.odoo.user, config.odoo.passwd, {}
            )
            self.models = xmlrpc.client.ServerProxy(
                object_proxy_url,
                context=context,
            )
        except Exception as e:
            logging.error(f"Odoo API connection impossible: {e}")

    def search_read(self, entity, cond=None, fields=None, limit=0, offset=0, order="id ASC"):
        """Main api request, retrieving data according search conditions."""
        fields_and_context = {
            "fields": fields if fields else {},
            "context": {"lang": "fr_FR", "tz": "Europe/Paris"},
            "limit": limit,
            "offset": offset,
            "order": order,
        }

        return self.models.execute_kw(
            config.odoo.db,
            self.uid,
            config.odoo.passwd,
            entity,
            "search_read",
            [cond if cond else []],
            fields_and_context,
        )

    def authenticate(self, login, password):
        return self.common.authenticate(config.odoo.db, login, password, {})


def _load_from_file() -> Dict:
    if not os.path.exists(DATA_PATH):
        return {
            "date": "",
            "products": [],
        }
    with open(DATA_PATH) as json_file:
        return json.load(json_file)


def _save_in_file(products):
    if os.path.exists(DATA_PATH):
        os.remove(DATA_PATH)
    with open(DATA_PATH, "w") as json_file:
        json.dump(products, json_file)


def _consolidate(all_products: List[Dict], category: AnyStr) -> List[Dict]:
    products = []
    for product in all_products:
        products.append(product)
        product["bio"] = product["name"].find(" Bio") >= 0
        product["id"] = int(product["barcode"][3:7])
        product["category"] = category
        name = product["name"]
        for p in unp:
            name = p.sub("", name)
        product["name"] = name.strip()
    logging.info(f"{len(products)} products loaded")
    return products


def variable_weight_products():
    try:
        products = []
        for category, conditions in config.odoo.categories.items():
            odoo_api = OdooAPI()
            _products = odoo_api.search_read(
                "product.product",
                cond=[["sale_ok", "=", True]] + conditions,
                fields=[
                    "barcode",
                    "categ_id",
                    "image_medium",
                    "name",
                    "theoritical_price",
                ],
                order="name ASC",
            )
            logging.info(f"{len(_products)} products found for {category}")
            products += _consolidate(_products, category)
        data = {
            "date": datetime.now().strftime("%d/%m/%y %H:%M"),
            "products": products,
        }
        _save_in_file(data)
        data["synced"] = True
        return data
    except Exception as e:
        logging.error(e)
        data = _load_from_file()
        data["synced"] = False
        return data
