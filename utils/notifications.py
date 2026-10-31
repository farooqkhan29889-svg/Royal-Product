"""Store owner notification helpers: WhatsApp direct dispatch alert, Email, Telegram/Webhook."""

import os
import urllib.parse
from utils.ui import WHATSAPP_NUMBER

OWNER_PHONE = os.getenv("OWNER_WHATSAPP", WHATSAPP_NUMBER)
OWNER_NAME = os.getenv("OWNER_NAME", "Mohammad Farooq (Managing Director)")
OWNER_STORE_NAME = "छोटी मकड़ी HONEY — Royal Natural Products"
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "care@royalnaturalhoney.com")
OWNER_ADDRESS = os.getenv(
    "OWNER_ADDRESS",
    "Royal Honey & Dry Fruits Dispatch Center, Saeed Colony, Karond, Bhopal, MP - 462038",
)
OWNER_UPI_ID = os.getenv("OWNER_UPI_ID", "8770465561@upi")


def get_owner_details():
    """Returns official store owner profile details for dashboard display & invoices."""
    return {
        "store_name": OWNER_STORE_NAME,
        "owner_name": OWNER_NAME,
        "phone": OWNER_PHONE,
        "email": OWNER_EMAIL,
        "address": OWNER_ADDRESS,
        "upi_id": OWNER_UPI_ID,
    }


def format_order_summary_text(order):
    """Formats an order into a clean WhatsApp/Telegram text message for the store owner."""
    customer = order.get("customer", {})
    items = order.get("items", [])
    
    items_text = "\n".join(
        f"  • {item['name']} ({item.get('weight', '-')}) × {item['qty']} = ₹{float(item['price']) * int(item['qty']):,.0f}"
        for item in items
    )
    
    msg = (
        f"🚨 *NEW ORDER RECEIVED!* 🚨\n\n"
        f"📦 *Order ID:* #{order['id']}\n"
        f"📅 *Date:* {order.get('date', 'Today')}\n"
        f"💰 *Total Amount:* ₹{float(order['total']):,.0f}\n"
        f"💳 *Payment:* {order.get('payment_method', 'COD')} ({order.get('payment_status', 'Pending')})\n"
        f"🚚 *Fulfillment:* {order.get('fulfillment_status', 'Order Placed')}\n\n"
        f"👤 *Customer:* {customer.get('name', 'N/A')}\n"
        f"📱 *Mobile:* {customer.get('phone', 'N/A')}\n"
        f"📧 *Email:* {customer.get('email') or 'N/A'}\n"
        f"📍 *Shipping Address:*\n{customer.get('address', 'N/A')}\n\n"
        f"🛒 *Items:*\n{items_text}\n"
    )
    if order.get("discount"):
        msg += f"\n🎟️ *Coupon Applied:* {order['discount'].get('coupon')} (-₹{order['discount'].get('amount')})"
    return msg


def get_owner_whatsapp_alert_url(order, owner_phone=OWNER_PHONE):
    """Returns a click-to-notify WhatsApp web/app link to send this order alert directly to the owner."""
    text = format_order_summary_text(order)
    phone_clean = "".join(ch for ch in str(owner_phone) if ch.isdigit())
    if len(phone_clean) == 10:
        phone_clean = "91" + phone_clean
    return f"https://wa.me/{phone_clean}?text={urllib.parse.quote(text)}"


def get_customer_whatsapp_url(order, message_type="confirmed"):
    """Generates a WhatsApp URL from the owner to update the customer regarding their order."""
    customer = order.get("customer", {})
    phone = customer.get("phone", "")
    phone_clean = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(phone_clean) == 10:
        phone_clean = "91" + phone_clean
    if not phone_clean:
        return ""

    name = customer.get("name", "Customer")
    order_id = order.get("id", "")
    total = float(order.get("total", 0))
    status = order.get("payment_status", "Confirmed")

    if message_type == "payment_reminder":
        pay_url = order.get("payment_link", {}).get("url", "")
        text = (
            f"Namaste {name}! 🙏\n\n"
            f"This is from *छोटी मकड़ी HONEY*.\n"
            f"Your Order *#{order_id}* (Total: ₹{total:,.0f}) is pending online payment.\n\n"
            f"👉 Complete your payment safely via Razorpay UPI:\n{pay_url}\n\n"
            f"Once paid, we will package and dispatch your order right away! 🍯"
        )
    elif message_type == "dispatched":
        text = (
            f"Namaste {name}! 🍯🚚\n\n"
            f"Great news! Your order *#{order_id}* has been *DISPATCHED* by *छोटी मकड़ी HONEY*.\n"
            f"💰 Total Amount: ₹{total:,.0f} ({status})\n"
            f"📍 Delivery Address: {customer.get('address', '')}\n\n"
            f"Expected delivery in 2-3 business days. Packaged in shockproof safety jars.\n"
            f"For any queries, contact our helpline: +{WHATSAPP_NUMBER}."
        )
    else:  # confirmed
        text = (
            f"Namaste {name}! 🍯✨\n\n"
            f"Thank you for your order *#{order_id}* at *छोटी मकड़ी HONEY*!\n"
            f"💰 Total: ₹{total:,.0f} · Payment: {status}\n\n"
            f"Our warehouse is preparing your 100% pure raw honey & dry fruits for dispatch.\n"
            f"We will update you as soon as your parcel is on the way!"
        )
    return f"https://wa.me/{phone_clean}?text={urllib.parse.quote(text)}"

