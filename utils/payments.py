"""Server-side Razorpay Payment Links integration."""

import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
RAZORPAY_API_URL = "https://api.razorpay.com/v1/payment_links"


class PaymentError(Exception):
    pass


def _load_env():
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_env()


def razorpay_configured():
    return bool(os.getenv("RAZORPAY_KEY_ID") and os.getenv("RAZORPAY_KEY_SECRET"))


def _request(method, path="", **kwargs):
    if not razorpay_configured():
        raise PaymentError(
            "Razorpay keys are missing. Add them to .env or choose Cash on Delivery."
        )

    try:
        response = requests.request(
            method,
            f"{RAZORPAY_API_URL}{path}",
            auth=(os.environ["RAZORPAY_KEY_ID"], os.environ["RAZORPAY_KEY_SECRET"]),
            timeout=20,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise PaymentError("Could not connect to Razorpay. Please try again.") from exc

    try:
        data = response.json()
    except ValueError:
        data = {}

    if not response.ok:
        message = data.get("error", {}).get("description") or "Razorpay request failed."
        raise PaymentError(message)
    return data


def create_payment_link(order_id, total, customer):
    customer_details = {
        "name": customer["name"],
        "contact": f"+91{customer['phone']}",
    }
    if customer.get("email"):
        customer_details["email"] = customer["email"]

    data = _request(
        "POST",
        json={
            "amount": int(round(total * 100)),
            "currency": "INR",
            "accept_partial": False,
            "upi_link": False,
            "reference_id": order_id,
            "description": f"Royal Natural Products order {order_id}",
            "customer": customer_details,
            "notify": {"sms": False, "email": False},
            "reminder_enable": False,
        },
    )
    if not data.get("id") or not data.get("short_url"):
        raise PaymentError("Razorpay did not return a payment link.")
    return {"id": data["id"], "url": data["short_url"]}


def verify_payment(order):
    payment_link = order.get("payment_link", {})
    if not payment_link.get("id"):
        raise PaymentError("This order does not have a Razorpay payment link.")

    data = _request("GET", f"/{payment_link['id']}")
    expected_amount = int(round(order["total"] * 100))
    if (
        data.get("reference_id") != order["id"]
        or data.get("amount") != expected_amount
        or data.get("currency", "INR") != "INR"
    ):
        raise PaymentError("Razorpay payment details do not match this order.")

    if data.get("status") == "paid" and data.get("amount_paid", 0) >= expected_amount:
        return True, "Payment verified successfully."
    return False, "Payment is not complete yet. Pay first, then check again."
