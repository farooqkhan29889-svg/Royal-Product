import streamlit as st

from utils.store import load_orders
from utils.ui import (
    WA_ICON_SVG,
    WHATSAPP_PHONE_DISPLAY,
    apply_store_css,
    get_whatsapp_url,
    render_announcement_bar,
)

apply_store_css()
render_announcement_bar()

st.subheader("📦 Your Orders & Live Tracking")

email = st.text_input(
    "Enter your order email address",
    key="orders_email",
    placeholder="e.g. buyer@example.com",
    icon=":material/mail:",
)

if not email:
    st.info(
        "Enter the email address you entered during checkout to track your orders and view invoices.",
        icon=":material/search:",
    )
    st.stop()

orders = [o for o in load_orders() if o["customer"]["email"] == email.strip().lower()]

if not orders:
    st.warning(f"No previous orders found for '{email.strip().lower()}'.", icon=":material/search_off:")
    st.page_link("app_pages/shop.py", label="Explore Royal Natural Shop", icon=":material/storefront:")
    st.stop()

new_order = st.session_state.pop("last_order_id", None)
if new_order and any(o["id"] == new_order for o in orders):
    st.success(
        f"🎉 Congratulations! Order #{new_order} has been placed successfully! Our dispatch team is packaging your jars in shockproof safety boxes.",
        icon=":material/check_circle:",
    )
    st.balloons()

st.caption(f"Found {len(orders)} order(s) for {email.strip().lower()}")

for order in reversed(orders):
    with st.container(border=True):
        head_col, status_col, total_col = st.columns([3, 2, 1.2], vertical_alignment="center")
        with head_col:
            st.markdown(f"### Order #{order['id']}")
            st.caption(
                f"📅 {order['date']} · 💳 {order['payment_method']}<br>"
                f"📍 Deliver to: **{order['customer'].get('name', 'Customer')}**, {order['customer']['address'].splitlines()[0]}",
                unsafe_allow_html=True,
            )
        with status_col:
            st.markdown(
                """
                <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 6px 12px; font-size: 0.82rem; color: #065f46; font-weight: 600;">
                    🟢 Status: <b>Confirmed & Preparing Dispatch</b><br>
                    <span style="font-size: 0.76rem; font-weight: normal; color: #047857;">🚚 Estimated Delivery: 2-3 Days</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with total_col:
            st.metric("Total Paid", f"₹{order['total']:g}")

        st.divider()
        st.markdown("**Ordered Items:**")
        for item in order["items"]:
            st.markdown(f"- 🍯 **{item['name']}** × {item['qty']} — **₹{item['price'] * item['qty']:g}**")

        if order.get("discount"):
            st.caption(f"🎟️ Discount Applied: {order['discount'].get('coupon', '')} (-₹{order['discount'].get('amount', 0):g})")

        wa_order_help = get_whatsapp_url(
            f"Hi Royal Natural Products, I have an inquiry about my Order #{order['id']} placed on {order['date']}."
        )
        st.markdown(
            f"""
            <a href="{wa_order_help}" target="_blank" class="card-wa-btn" style="max-width: 320px; font-size: 0.88rem; padding: 8px 14px; margin-top: 8px;">
                <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                <span>Track / Support on WhatsApp ({WHATSAPP_PHONE_DISPLAY})</span>
            </a>
            """,
            unsafe_allow_html=True,
        )
