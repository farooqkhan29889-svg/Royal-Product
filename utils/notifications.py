"""Store owner notification helpers: WhatsApp direct dispatch alert, Email, Telegram/Webhook."""

import os
import urllib.parse
from utils.ui import WHATSAPP_NUMBER

OWNER_PHONE = os.getenv("OWNER_WHATSAPP", WHATSAPP_NUMBER)


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
        f"💳 *Payment:* {order.get('payment_method', 'COD')} ({order.get('payment_status', 'Pending')})\n\n"
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
