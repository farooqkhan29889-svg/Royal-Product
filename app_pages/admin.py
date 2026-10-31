"""Admin console: revenue, orders, payment notifications, owner profile, and invoice printing."""

import csv
import io
import os
import urllib.parse
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from utils.firebase_db import is_firebase_available
from utils.invoice import invoice_bytes, print_invoice_script
from utils.notifications import (
    get_customer_whatsapp_url,
    get_owner_details,
    get_owner_whatsapp_alert_url,
)
from utils.payments import PaymentError, razorpay_configured, verify_payment
from utils.store import (
    load_orders,
    load_products,
    update_order_fulfillment,
    update_order_payment,
)
from utils.ui import WA_ICON_SVG, WHATSAPP_NUMBER, apply_store_css

apply_store_css()

st.caption("Live Orders, COD Cash Management, Payment Notifications & Store Profile")

if not os.getenv("ADMIN_PASSWORD"):
    st.warning(
        "Default admin password is in use. Set ADMIN_PASSWORD in .env to change it.",
        icon=":material/password:",
    )

if not st.session_state.get("admin_ok"):
    with st.form("admin_login"):
        st.markdown("**Owner & Admin Sign In**")
        entered = st.text_input("Admin password", type="password")
        if st.form_submit_button("Sign in", icon=":material/login:", use_container_width=True):
            if entered == os.getenv("ADMIN_PASSWORD", "admin123"):
                st.session_state.admin_ok = True
                st.rerun()
            st.error("Wrong password.", icon=":material/lock:")
    st.stop()

top_c1, top_c2 = st.columns([4, 1], vertical_alignment="center")
with top_c1:
    if is_firebase_available():
        st.caption("🟢 **Firebase Cloud Firestore Active** (`royal-natural-products`) · Real-time order sync enabled")
    else:
        st.caption("📁 **Local Storage Mode** (`data/orders.json`) · Offline fallback active")
with top_c2:
    if st.button("Sign out", icon=":material/logout:", use_container_width=True):
        del st.session_state["admin_ok"]
        st.rerun()

orders = load_orders()
products = load_products()
product_lookup = {p["id"]: p for p in products}
owner_info = get_owner_details()

if not orders:
    st.info("No orders yet. Orders will appear here in real-time as customers complete checkout.")
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


# Filter section
filter_col = st.container()
with filter_col:
    search = st.text_input(
        "Search by order ID, name or mobile",
        key="admin_search",
        placeholder="e.g. 9876543210 or #8A1DB689",
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
        customer = order.get("customer", {})
        haystack = " ".join(
            [order.get("id", ""), customer.get("name", ""), customer.get("phone", ""), customer.get("email", "")]
        ).lower()
        if terms not in haystack:
            continue
    filtered.append(order)

revenue = sum(float(o["total"]) for o in filtered)
collected = sum(paid_amount(o) for o in filtered)
due_cod = sum(cod_amount(o) for o in filtered)
pending_count = sum(1 for o in filtered if o.get("payment_status") == "Pending payment")
units = sum(int(i["qty"]) for o in filtered for i in o.get("items", []))

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Orders", len(filtered))
m2.metric("Order value", f"₹{revenue:,.0f}")
m3.metric("Collected (UPI)", f"₹{collected:,.0f}")
m4.metric("To collect (COD)", f"₹{due_cod:,.0f}")
m5.metric("Awaiting payment", pending_count)

# Instant Payment & Dispatch Notifications Banner
cod_unfulfilled = [o for o in filtered if o.get("payment_status") == "Cash on Delivery" and o.get("fulfillment_status") not in ["Delivered", "Cancelled"]]
upi_paid = [o for o in filtered if o.get("payment_status") == "Paid"]
upi_pending = [o for o in filtered if o.get("payment_status") == "Pending payment"]

st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, rgba(201,162,39,0.12), rgba(37,211,102,0.12)); border: 1px solid rgba(201,162,39,0.3); border-radius: 10px; padding: 12px 18px; margin: 15px 0 20px 0;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
                <strong style="color: #f7d070; font-size: 0.95rem;">🔔 Real-Time Order & Payment Notification Center</strong>
                <div style="font-size: 0.83rem; color: #CBD5E1; margin-top: 4px;">
                    • <b>{len(cod_unfulfilled)}</b> COD orders awaiting packaging & cash collection &nbsp;|&nbsp;
                    • <b>{len(upi_paid)}</b> UPI orders confirmed & paid &nbsp;|&nbsp;
                    • <b>{len(upi_pending)}</b> Online payment links awaiting customer completion
                </div>
            </div>
            <div style="font-size: 0.82rem; background: rgba(0,0,0,0.35); padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);">
                👤 Owner: <b>{owner_info['owner_name']}</b> · 📱 <b>+{owner_info['phone']}</b>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tabs navigation
tab_orders, tab_analytics, tab_owner = st.tabs(
    [
        "📦 Live Orders & Dispatch Desk",
        "📊 Sales & Product Performance",
        "🏢 Owner Profile & Store Settings",
    ]
)

# -------------------------------------------------------------
# TAB 1: Live Orders & Dispatch Desk
# -------------------------------------------------------------
with tab_orders:
    st.markdown(f"#### 📦 Order Records ({len(filtered)})")
    if not filtered:
        st.info("No orders matched your search or filters.")

    for order in reversed(filtered):
        status = order.get("payment_status", "Confirmed")
        fulfillment = order.get("fulfillment_status", "Order Placed")
        customer = order.get("customer", {})
        cust_phone = customer.get("phone", "")
        clean_phone = "".join(ch for ch in str(cust_phone) if ch.isdigit())

        dot = {"Paid": "🟢", "Pending payment": "🟠", "Cash on Delivery": "🔵"}.get(status, "⚪")
        ful_badge = {
            "Order Placed": "📥 Placed",
            "Packaging": "🎁 Packaging",
            "Dispatched": "🚚 Dispatched",
            "Delivered": "✅ Delivered",
            "Cancelled": "❌ Cancelled",
        }.get(fulfillment, f"📍 {fulfillment}")

        with st.container(border=True):
            # Card Header
            head, badge_col, total_col = st.columns([3, 2, 1.2], vertical_alignment="center")
            with head:
                st.markdown(f"### {dot} Order #{order['id']} — {customer.get('name', 'Customer')}")
                st.caption(f"📅 Placed: {order['date']} · 💳 {order['payment_method']}")
            with badge_col:
                st.markdown(
                    f"""
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        <span style="background: rgba(201,162,39,0.18); border: 1px solid #c9a227; color: #f7d070; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                            {ful_badge}
                        </span>
                        <span style="background: rgba(37,211,102,0.18); border: 1px solid #25D366; color: #4ade80; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                            Payment: {status}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with total_col:
                st.metric("Total", f"₹{float(order['total']):,.0f}")

            st.divider()

            # 3-Column Detailed Information Layout
            col_cust, col_items, col_mgmt = st.columns([1.2, 1.3, 1.5], gap="medium")

            # Column 1: Customer Details
            with col_cust:
                st.markdown("**👤 Customer & Delivery Address**")
                st.markdown(f"**Name:** {customer.get('name', '-')}")
                st.markdown(f"**Phone:** `{cust_phone or '-'}`")
                if customer.get("email"):
                    st.caption(f"📧 {customer['email']}")
                st.markdown(
                    f"""
                    <div style="background: rgba(255,255,255,0.04); border-left: 3px solid #c9a227; padding: 8px 12px; border-radius: 4px; font-size: 0.84rem; margin-top: 6px;">
                        📍 <b>Shipping Address:</b><br>{customer.get('address', 'Not provided')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Quick contact links
                if clean_phone:
                    st.markdown(
                        f"""
                        <div style="margin-top: 8px; display: flex; gap: 10px;">
                            <a href="tel:{clean_phone}" style="font-size: 0.8rem; color: #93c5fd; text-decoration: none;">📞 Direct Call</a>
                            <a href="https://wa.me/91{clean_phone if len(clean_phone) == 10 else clean_phone}" target="_blank" style="font-size: 0.8rem; color: #86efac; text-decoration: none;">💬 WhatsApp Chat</a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Column 2: Items in Order
            with col_items:
                st.markdown("**🛒 Items to Pack**")
                for item in order.get("items", []):
                    weight = f" ({item.get('weight')})" if item.get("weight") else ""
                    line_price = float(item["price"]) * int(item["qty"])
                    st.markdown(
                        f"• **{item['name']}**{weight}<br>"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;Qty: **{item['qty']}** × ₹{float(item['price']):,.0f} = **₹{line_price:,.0f}**",
                        unsafe_allow_html=True,
                    )
                if order.get("discount"):
                    st.caption(
                        f"🎟️ Coupon `{order['discount'].get('coupon')}`: -₹{float(order['discount'].get('amount', 0)):,.0f}"
                    )

            # Column 3: Payment Notification & Status Management
            with col_mgmt:
                st.markdown("**💳 Payment & Order Management**")
                if status == "Cash on Delivery":
                    st.info(f"🔵 **COD:** Collect ₹{float(order['total']):,.0f} upon delivery.")
                    if st.button("Mark Cash Collected / Paid", key=f"admin_mark_cod_{order['id']}", icon=":material/check_circle:"):
                        update_order_payment(order["id"], "Paid")
                        st.success(f"Order #{order['id']} marked as Paid!")
                        st.rerun()
                elif status == "Paid":
                    paid_timestamp = order.get("paid_at", order["date"])
                    st.success(f"🟢 **Verified Paid** (Recorded: {paid_timestamp})", icon=":material/verified:")
                elif status == "Pending payment":
                    st.warning("🟠 **Payment Pending** on Razorpay.", icon=":material/hourglass_top:")
                    if order.get("payment_link"):
                        p_col1, p_col2 = st.columns(2)
                        with p_col1:
                            st.link_button(
                                "Open Pay Link",
                                order["payment_link"]["url"],
                                icon=":material/link:",
                                use_container_width=True,
                            )
                        with p_col2:
                            if st.button("Verify Razorpay", key=f"admin_verify_{order['id']}", icon=":material/sync:", use_container_width=True):
                                try:
                                    paid, msg = verify_payment(order)
                                    if paid:
                                        update_order_payment(order["id"], "Paid")
                                        st.success("Payment verified as PAID!")
                                        st.rerun()
                                    else:
                                        st.info(msg)
                                except PaymentError as err:
                                    st.error(str(err))

                # Fulfillment stage selector
                st.write("")
                st.caption("📦 **Update Fulfillment Stage:**")
                stages = ["Order Placed", "Packaging", "Dispatched", "Delivered", "Cancelled"]
                curr_idx = stages.index(fulfillment) if fulfillment in stages else 0
                selected_stage = st.selectbox(
                    "Fulfillment Stage",
                    stages,
                    index=curr_idx,
                    key=f"admin_ful_{order['id']}",
                    label_visibility="collapsed",
                )
                if selected_stage != fulfillment:
                    update_order_fulfillment(order["id"], selected_stage)
                    st.toast(f"Order #{order['id']} fulfillment updated to {selected_stage}!")
                    st.rerun()

            st.write("")
            # Action Toolbar
            act_col1, act_col2, act_col3, act_col4 = st.columns([1.2, 1.2, 1, 1], gap="small")

            # 1. Dispatch Alert to Warehouse/Owner WhatsApp
            with act_col1:
                wa_dispatch_url = get_owner_whatsapp_alert_url(order)
                st.markdown(
                    f"""
                    <a href="{wa_dispatch_url}" target="_blank" style="background: rgba(37, 211, 102, 0.15); border: 1px solid #25D366; color: #25D366 !important; border-radius: 8px; padding: 7px 12px; font-size: 0.82rem; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 6px; text-decoration: none; height: 38px; box-sizing: border-box;">
                        <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                        <span>Send Dispatch Alert</span>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )

            # 2. WhatsApp Customer Notification
            with act_col2:
                wa_type = "dispatched" if fulfillment == "Dispatched" else ("payment_reminder" if status == "Pending payment" else "confirmed")
                cust_wa_url = get_customer_whatsapp_url(order, message_type=wa_type)
                if cust_wa_url:
                    st.markdown(
                        f"""
                        <a href="{cust_wa_url}" target="_blank" style="background: rgba(59, 130, 246, 0.15); border: 1px solid #3b82f6; color: #93c5fd !important; border-radius: 8px; padding: 7px 12px; font-size: 0.82rem; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 6px; text-decoration: none; height: 38px; box-sizing: border-box;">
                            <span>💬 Notify Customer</span>
                        </a>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.button("No customer mobile", disabled=True, key=f"no_mob_{order['id']}", use_container_width=True)

            # 3. Print Invoice
            with act_col3:
                if st.button("Print invoice", icon=":material/print:", key=f"admin_print_{order['id']}", use_container_width=True):
                    st.session_state["admin_print"] = order["id"]

            # 4. Download Invoice
            with act_col4:
                st.download_button(
                    "Download invoice",
                    data=invoice_bytes(order, product_lookup),
                    file_name=f"Invoice-{order['id']}.html",
                    mime="text/html",
                    icon=":material/download:",
                    key=f"admin_dl_{order['id']}",
                    use_container_width=True,
                )

            # Print view modal/script
            if st.session_state.get("admin_print") == order["id"]:
                st.html(print_invoice_script(order, product_lookup))
                if st.button("Close print view", key=f"admin_close_{order['id']}"):
                    del st.session_state["admin_print"]
                    st.rerun()

# -------------------------------------------------------------
# TAB 2: Sales & Product Analytics
# -------------------------------------------------------------
with tab_analytics:
    st.markdown("#### 🏆 Best-Selling Honey & Dry Fruits")
    sales = defaultdict(lambda: {"qty": 0, "revenue": 0.0})
    for order in filtered:
        for item in order.get("items", []):
            line = float(item["price"]) * int(item["qty"])
            sales[item["name"]]["qty"] += int(item["qty"])
            sales[item["name"]]["revenue"] += line

    col_rank, col_chart = st.columns([1, 1.4], gap="large")
    with col_rank:
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
        else:
            st.info("No sales in this view.")

    with col_chart:
        if sales:
            chart = pd.DataFrame(
                [
                    {"Product": name[:18], "Revenue": value["revenue"]}
                    for name, value in ranked[:8]
                ]
            )
            st.bar_chart(chart.set_index("Product"), color="#c9a227", height=240)

    st.write("")
    st.markdown("#### 📥 Order Data Export")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Order ID", "Date", "Customer", "Mobile", "Email", "Address", "Items", "Method", "Payment Status", "Fulfillment", "Total"])
    for order in reversed(filtered):
        c = order.get("customer", {})
        writer.writerow(
            [
                order.get("id", ""),
                order.get("date", ""),
                c.get("name", ""),
                c.get("phone", ""),
                c.get("email", ""),
                c.get("address", ""),
                "; ".join(f"{i['name']} ({i.get('weight', '-')}) x{i['qty']}" for i in order.get("items", [])),
                order.get("payment_method", ""),
                order.get("payment_status", ""),
                order.get("fulfillment_status", "Order Placed"),
                f"{float(order.get('total', 0)):.2f}",
            ]
        )
    st.download_button(
        "Export these orders (CSV)",
        data=buffer.getvalue().encode("utf-8-sig"),
        file_name="royal-natural-orders.csv",
        mime="text/csv",
        icon=":material/table_view:",
        use_container_width=True,
    )

# -------------------------------------------------------------
# TAB 3: Owner Profile & Store Settings
# -------------------------------------------------------------
with tab_owner:
    st.markdown("#### 🏢 Store Owner & Business Profile")
    st.caption("Manage store identity, dispatch warehouse location, contact helplines, and cloud payment gateways.")

    c_prof1, c_prof2 = st.columns([1.2, 1], gap="large")
    with c_prof1:
        with st.container(border=True):
            st.markdown("##### 📍 Official Store & Warehouse Information")
            st.markdown(f"**Store Brand:** {owner_info['store_name']}")
            st.markdown(f"**Managing Director / Owner:** {owner_info['owner_name']}")
            st.markdown(f"**Owner WhatsApp (Order Alerts):** `+{owner_info['phone']}`")
            st.markdown(f"**Customer Support Email:** `{owner_info['email']}`")
            st.markdown(f"**Business UPI ID:** `{owner_info['upi_id']}`")
            st.markdown(f"**Central Packaging & Dispatch Hub:**<br>{owner_info['address']}", unsafe_allow_html=True)

            st.write("")
            test_alert_msg = (
                f"🔔 *TEST OWNER DISPATCH NOTIFICATION*\n"
                f"Store: {owner_info['store_name']}\n"
                f"Owner: {owner_info['owner_name']}\n"
                f"Alert Phone: +{owner_info['phone']}\n"
                f"Status: System operational & ready to receive new orders!"
            )
            test_url = f"https://wa.me/91{owner_info['phone']}?text={urllib.parse.quote(test_alert_msg)}"
            st.markdown(
                f"""
                <a href="{test_url}" target="_blank" style="background: rgba(37, 211, 102, 0.15); border: 1px solid #25D366; color: #25D366 !important; border-radius: 8px; padding: 7px 12px; font-size: 0.82rem; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; text-decoration: none;">
                    <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                    <span>Test WhatsApp Alert to Owner Phone</span>
                </a>
                """,
                unsafe_allow_html=True,
            )

    with c_prof2:
        with st.container(border=True):
            st.markdown("##### 🔌 Cloud & Payment Gateway Status")
            # Firebase status
            if is_firebase_available():
                st.success("🟢 **Google Firebase Firestore** Connected (`royal-natural-products`)", icon=":material/cloud_done:")
                st.caption("Orders, variants, and product updates are synced securely across cloud servers.")
            else:
                st.warning("📁 **Local Mode:** Storing in `data/orders.json` (Service account JSON not detected).", icon=":material/cloud_off:")

            st.divider()

            # Razorpay status
            if razorpay_configured():
                key_id = os.getenv("RAZORPAY_KEY_ID", "")
                masked_key = key_id[:8] + "..." + key_id[-4:] if len(key_id) > 12 else key_id
                st.success(f"💳 **Razorpay UPI Gateway** Active (`{masked_key}`)", icon=":material/credit_score:")
                st.caption("Instant UPI QR, Google Pay, PhonePe, and Netbanking enabled.")
            else:
                st.info("💳 **Razorpay:** Not configured in `.env`. Cash on Delivery is active.", icon=":material/info:")

            st.divider()

            st.markdown("##### 💡 Owner Quick Workflow")
            st.markdown(
                """
                1. **When customer completes order:** Review payment mode (COD vs Paid UPI).
                2. **Instant Packaging:** Forward the WhatsApp dispatch alert directly to packing team.
                3. **Courier Handover:** Update fulfillment stage to **Dispatched** and notify customer.
                4. **Doorstep Delivery:** For COD orders, collect cash and click **Mark Cash Collected**.
                """
            )
