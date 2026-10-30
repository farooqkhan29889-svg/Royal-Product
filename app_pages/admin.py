"""Admin console: revenue, orders, payments and invoice printing."""

import csv
import io
import os
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from utils.invoice import invoice_bytes, print_invoice_script
from utils.notifications import get_owner_whatsapp_alert_url
from utils.store import load_orders, load_products
from utils.firebase_db import is_firebase_available
from utils.ui import WA_ICON_SVG, apply_store_css

apply_store_css()

st.subheader("🛡️ Admin Console")

if not os.getenv("ADMIN_PASSWORD"):
    st.warning(
        "Default admin password is in use. Set ADMIN_PASSWORD in .env to change it.",
        icon=":material/password:",
    )

if not st.session_state.get("admin_ok"):
    with st.form("admin_login"):
        st.markdown("**Sign in required**")
        entered = st.text_input("Admin password", type="password")
        if st.form_submit_button("Sign in", icon=":material/login:", use_container_width=True):
            if entered == os.getenv("ADMIN_PASSWORD", "admin123"):
                st.session_state.admin_ok = True
                st.rerun()
            st.error("Wrong password.", icon=":material/lock:")
    st.stop()

if st.button("Sign out", icon=":material/logout:"):
    del st.session_state["admin_ok"]
    st.rerun()

orders = load_orders()
products = load_products()
product_lookup = {p["id"]: p for p in products}

if is_firebase_available():
    st.caption(f"{len(orders)} order(s) · 🟢 **Firebase Cloud Firestore Active** (`royal-natural-products`)")
else:
    st.caption(f"{len(orders)} order(s) · 📁 **Local Storage Mode** (`data/orders.json`)")


if not orders:
    st.info("No orders yet. They will appear here as soon as customers check out.")
    st.stop()

STATUS_ALL = "All"
PAY_ALL = "All payments"
RANGE_PRESETS = {
    "All time": None,
    "Today": (date.today(), date.today()),
    "Last 7 days": (date.today() - timedelta(days=7), date.today()),
    "Last 30 days": (date.today() - timedelta(days=30), date.today()),
}


def order_date(order):
    try:
        return date.fromisoformat(order["date"].split()[0])
    except Exception:
        return None


def paid_amount(order):
    return float(order["total"]) if order.get("payment_status") == "Paid" else 0.0


def cod_amount(order):
    return float(order["total"]) if order.get("payment_status") == "Cash on Delivery" else 0.0


filter_col = st.container()
with filter_col:
    search = st.text_input(
        "Search by order ID, name or mobile",
        key="admin_search",
        placeholder="e.g. 9876543210 or #05E13220",
        icon=":material/search:",
    )

left, right = st.columns([1, 2], gap="large")
with left:
    status_choice = st.selectbox(
        "Payment status",
        [STATUS_ALL, "Paid", "Pending payment", "Cash on Delivery"],
        key="admin_status",
    )
with right:
    range_choice = st.selectbox("Period", list(RANGE_PRESETS), key="admin_range")
    pay_choice = st.selectbox(
        "Payment method",
        [PAY_ALL] + sorted({o["payment_method"] for o in orders}),
        key="admin_payment",
    )

terms = search.strip().lower().lstrip("#")
filtered = []
for order in orders:
    if status_choice != STATUS_ALL and order.get("payment_status") != status_choice:
        continue
    if pay_choice != PAY_ALL and order["payment_method"] != pay_choice:
        continue
    span = RANGE_PRESETS[range_choice]
    placed = order_date(order)
    if span and placed and not (span[0] <= placed <= span[1]):
        continue
    if terms:
        customer = order["customer"]
        haystack = " ".join(
            [order["id"], customer.get("name", ""), customer.get("phone", ""), customer.get("email", "")]
        ).lower()
        if terms not in haystack:
            continue
    filtered.append(order)

revenue = sum(float(o["total"]) for o in filtered)
collected = sum(paid_amount(o) for o in filtered)
due_cod = sum(cod_amount(o) for o in filtered)
pending_count = sum(1 for o in filtered if o.get("payment_status") == "Pending payment")
units = sum(int(i["qty"]) for o in filtered for i in o["items"])

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Orders", len(filtered))
m2.metric("Order value", f"₹{revenue:,.0f}")
m3.metric("Collected (UPI)", f"₹{collected:,.0f}")
m4.metric("To collect (COD)", f"₹{due_cod:,.0f}")
m5.metric("Awaiting payment", pending_count)

st.caption(f"Units sold in this view: {units}")

sales = defaultdict(lambda: {"qty": 0, "revenue": 0.0})
for order in filtered:
    for item in order["items"]:
        line = float(item["price"]) * int(item["qty"])
        sales[item["name"]]["qty"] += int(item["qty"])
        sales[item["name"]]["revenue"] += line

summary_col, list_col = st.columns([1, 2.2], gap="large")
with summary_col:
    st.markdown("#### 🏆 Top sellers")
    if sales:
        ranked = sorted(sales.items(), key=lambda kv: kv[1]["revenue"], reverse=True)
        st.dataframe(
            pd.DataFrame(ranked, columns=["Product", "Details"])[["Product"]].assign(
                Units=[v["qty"] for _, v in ranked],
                Revenue=[f"₹{v['revenue']:,.0f}" for _, v in ranked],
            ),
            hide_index=True,
            use_container_width=True,
        )
        chart = pd.DataFrame(
            [
                {"Product": name[:18], "Revenue": value["revenue"]}
                for name, value in ranked[:8]
            ]
        )
        st.bar_chart(chart.set_index("Product"), color="#c9a227", height=220)
    else:
        st.info("No sales in this view.")

with list_col:
    st.markdown("#### 📦 Orders")
    for order in reversed(filtered):
        status = order.get("payment_status", "Confirmed")
        dot = {"Paid": "🟢", "Pending payment": "🟠", "Cash on Delivery": "🔵"}.get(status, "⚪")
        with st.container(border=True):
            head, total = st.columns([4, 1], vertical_alignment="center")
            with head:
                st.markdown(f"**{dot} Order #{order['id']}** — {order['customer'].get('name', 'Customer')}")
                st.caption(
                    f"📅 {order['date']} · 💳 {order['payment_method']} · {status} · "
                    f"📱 {order['customer'].get('phone', '-')} · 📧 {order['customer'].get('email') or '-'}"
                )
            with total:
                st.metric("Total", f"₹{float(order['total']):,.0f}")

            detail = st.expander("Full details, address & invoice")
            with detail:
                st.markdown(f"**Ship to:** {order['customer']['address']}")
                for item in order["items"]:
                    weight = f" ({item.get('weight')})" if item.get("weight") else ""
                    st.markdown(
                        f"- {item['name']}{weight} × {item['qty']} — ₹{float(item['price']) * int(item['qty']):,.0f}"
                    )
                if order.get("discount"):
                    st.caption(
                        f"🎟️ Coupon {order['discount'].get('coupon', '-')}: "
                        f"-₹{float(order['discount'].get('amount', 0)):,.0f}"
                    )
                if order.get("payment_link"):
                    st.link_button(
                        "Razorpay payment link",
                        order["payment_link"]["url"],
                        icon=":material/payments:",
                        use_container_width=False,
                    )
                dl, pr, wa = st.columns([1, 1, 1.2])
                with dl:
                    st.download_button(
                        "Download invoice",
                        data=invoice_bytes(order, product_lookup),
                        file_name=f"Invoice-{order['id']}.html",
                        mime="text/html",
                        icon=":material/download:",
                        key=f"admin_dl_{order['id']}",
                        use_container_width=True,
                    )
                with pr:
                    if st.button(
                        "Print invoice",
                        icon=":material/print:",
                        key=f"admin_print_{order['id']}",
                        use_container_width=True,
                    ):
                        st.session_state["admin_print"] = order["id"]
                with wa:
                    wa_alert_link = get_owner_whatsapp_alert_url(order)
                    st.markdown(
                        f"""
                        <a href="{wa_alert_link}" target="_blank" style="background: rgba(37, 211, 102, 0.15); border: 1px solid #25D366; color: #25D366 !important; border-radius: 8px; padding: 7px 12px; font-size: 0.82rem; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 6px; text-decoration: none; height: 38px; box-sizing: border-box;">
                            <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                            <span>Share to WhatsApp</span>
                        </a>
                        """,
                        unsafe_allow_html=True,
                    )
                if st.session_state.get("admin_print") == order["id"]:
                    st.html(print_invoice_script(order, product_lookup))
                    if st.button("Close print view", key=f"admin_close_{order['id']}"):
                        del st.session_state["admin_print"]
                        st.rerun()

buffer = io.StringIO()
writer = csv.writer(buffer)
writer.writerow(["Order ID", "Date", "Customer", "Mobile", "Email", "Items", "Method", "Status", "Total"])
for order in reversed(filtered):
    writer.writerow(
        [
            order["id"],
            order["date"],
            order["customer"].get("name", ""),
            order["customer"].get("phone", ""),
            order["customer"].get("email", ""),
            "; ".join(
                f"{i['name']} ({i.get('weight', '-')}) x{i['qty']}" for i in order["items"]
            ),
            order["payment_method"],
            order.get("payment_status", ""),
            f"{float(order['total']):.2f}",
        ]
    )
st.download_button(
    "Export these orders (CSV)",
    data=buffer.getvalue().encode("utf-8-sig"),
    file_name="royal-orders.csv",
    mime="text/csv",
    icon=":material/table_view:",
    use_container_width=True,
)
