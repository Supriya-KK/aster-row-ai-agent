import json
import re
from pathlib import Path

ORDERS_FILE=Path(__file__).resolve().parent.parent/"data"/"orders.json"


def load_orders():
    with open(ORDERS_FILE,"r",encoding="utf-8") as file:
        data=json.load(file)

    return data["orders"]


def normalize_order_id(order_id):
    if not isinstance(order_id,str):
        return None

    order_id=order_id.strip().upper()

    if not re.fullmatch(r"ORD-\d{4}",order_id):
        return None

    return order_id


def lookup_order(order_id):
    normalized_id=normalize_order_id(order_id)

    if normalized_id is None:
        return {
            "found":False,
            "reason":"invalid_order_id"
        }

    orders=load_orders()

    for order in orders:
        if order["order_id"]==normalized_id:

            result={
                "found":True,
                "order_id":order["order_id"],
                "status":order["status"],
                "status_updated_at":order["status_updated_at"],
                "customer_safe_message":order["customer_safe_message"]
            }

            if order["estimated_delivery"] is not None:
                result["estimated_delivery"]=order["estimated_delivery"]

            if order["carrier"] is not None:
                result["carrier"]=order["carrier"]

            if order["tracking_number"] is not None:
                result["tracking_number"]=order["tracking_number"]

            return result

    return {
    "found":False,
    "reason":"order_not_found"
    }