"""Shared shop logic: products, weight variants, cart, coupons, and orders."""

import json
import re
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = ROOT / "data" / "products.json"
ORDERS_FILE = ROOT / "data" / "orders.json"

FREE_DELIVERY_THRESHOLD = 499

AVAILABLE_COUPONS = {
    "ROYAL15": {"type": "pct", "val": 15, "desc": "15% OFF entire order"},
    "CHHOTI15": {"type": "pct", "val": 15, "desc": "15% Special Festive Discount"},
    "HONEY50": {"type": "fixed", "val": 50, "desc": "Flat ₹50 OFF"},
    "WELCOME10": {"type": "pct", "val": 10, "desc": "10% Welcome Discount"},
}


@st.cache_data(ttl=300)
def load_products():
    products = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    images_dir = PRODUCTS_FILE.parent / "images"
    for p in products:
        img = p.get("image", "")
        if not img.startswith(("http://", "https://")):
            p["image"] = str(images_dir / img)
    return products


def get_product(product_id):
    if not product_id:
        return None
    base_id = product_id.split("::")[0]
    return next((p for p in load_products() if p["id"] == base_id), None)


def normalize_phone(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]
    return digits


def resolve_variant_data(product, weight=None):
    """Resolve price and mrp for a specific weight variant."""
    if not product:
        return None
    variants = product.get("variants", [])
    selected_weight = weight or product.get("weight", "500g")
    
    # Try exact match or normalized match
    for v in variants:
        if v.get("weight", "").replace(" ", "").lower() == selected_weight.replace(" ", "").lower():
            return {
                "weight": v.get("weight"),
                "price": v.get("price"),
                "mrp": v.get("mrp"),
                "save": v.get("save", ""),
            }
            
    # Default to product top-level fields
    return {
        "weight": product.get("weight", "500g"),
        "price": product.get("price", 0),
        "mrp": product.get("mrp", product.get("price", 0)),
        "save": product.get("discount_badge", ""),
    }


def add_to_cart(product_id, qty=1, weight=None):
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    
    base_product = get_product(product_id)
    default_weight = base_product.get("weight", "") if base_product else ""
    
    # Keep base key if no weight or default weight to preserve test compatibility
    if not weight or weight == default_weight:
        cart_key = product_id.split("::")[0]
    else:
        cart_key = f"{product_id.split('::')[0]}::{weight}"
        
    st.session_state.cart[cart_key] = st.session_state.cart.get(cart_key, 0) + qty


def set_cart_qty(cart_key, qty):
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    qty = max(0, min(int(qty), 99))
    if qty == 0:
        remove_from_cart(cart_key)
    else:
        st.session_state.cart[cart_key] = qty


def remove_from_cart(cart_key):
    if "cart" in st.session_state:
        st.session_state.cart.pop(cart_key, None)


def cart_items():
    if "cart" not in st.session_state:
        return []
    items = []
    for cart_key, qty in list(st.session_state.cart.items()):
        parts = cart_key.split("::")
        pid = parts[0]
        weight_override = parts[1] if len(parts) > 1 else None
        
        base_product = get_product(pid)
        if not base_product:
            continue
            
        variant_data = resolve_variant_data(base_product, weight_override)
        
        # Create a customized item copy
        item_copy = dict(base_product)
        item_copy["cart_key"] = cart_key
        item_copy["selected_weight"] = variant_data["weight"]
        item_copy["weight"] = variant_data["weight"]
        item_copy["price"] = variant_data["price"]
        item_copy["mrp"] = variant_data["mrp"]
        
        items.append((item_copy, qty))
    return items


def cart_count():
    if "cart" not in st.session_state:
        return 0
    return sum(st.session_state.cart.values())


def cart_subtotal():
    return sum(p["price"] * qty for p, qty in cart_items())


def cart_original_mrp_total():
    return sum(p.get("mrp", p["price"]) * qty for p, qty in cart_items())


def get_free_delivery_status(subtotal):
    if subtotal >= FREE_DELIVERY_THRESHOLD:
        return {
            "eligible": True,
            "remaining": 0,
            "progress": 1.0,
            "text": "🎉 You have qualified for <b>FREE All-India Delivery</b>!",
        }
    remaining = FREE_DELIVERY_THRESHOLD - subtotal
    progress = max(0.0, min(1.0, subtotal / FREE_DELIVERY_THRESHOLD))
    return {
        "eligible": False,
        "remaining": remaining,
        "progress": progress,
        "text": f"Add ₹<b>{remaining:g}</b> more to unlock <b>FREE Delivery</b> across India!",
    }


def get_coupon_discount(coupon_code, subtotal):
    if not coupon_code:
        return 0
    code = coupon_code.strip().upper()
    if code in AVAILABLE_COUPONS:
        c = AVAILABLE_COUPONS[code]
        if c["type"] == "pct":
            return round((subtotal * c["val"]) / 100, 2)
        elif c["type"] == "fixed":
            return min(c["val"], subtotal)
    return 0


def cart_total(coupon_code=None):
    sub = cart_subtotal()
    if not coupon_code and "applied_coupon" in st.session_state:
        coupon_code = st.session_state.applied_coupon
    discount = get_coupon_discount(coupon_code, sub)
    return max(0.0, sub - discount)


def clear_cart():
    st.session_state.cart = {}
    if "applied_coupon" in st.session_state:
        del st.session_state["applied_coupon"]


def load_orders():
    if not ORDERS_FILE.exists():
        return []
    try:
        return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def new_order_id():
    return uuid.uuid4().hex[:8].upper()


def save_order(
    customer,
    items,
    total,
    payment_method,
    discount_info=None,
    order_id=None,
    payment_status="Confirmed",
    payment_link=None,
):
    order = {
        "id": order_id or new_order_id(),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "customer": customer,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "items": items,
        "total": round(total, 2),
    }
    if discount_info:
        order["discount"] = discount_info
    if payment_link:
        order["payment_link"] = payment_link
    orders = load_orders()
    orders.append(order)
    ORDERS_FILE.write_text(
        json.dumps(orders, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return order


def mark_order_paid(order_id):
    orders = load_orders()
    for order in orders:
        if order["id"] == order_id:
            order["payment_status"] = "Paid"
            order["paid_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            ORDERS_FILE.write_text(
                json.dumps(orders, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            return order
    return None
