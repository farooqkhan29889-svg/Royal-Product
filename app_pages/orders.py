import streamlit as st

from utils.payments import PaymentError, verify_payment
from utils.invoice import invoice_bytes, print_invoice_script
from utils.store import load_orders, load_products, mark_order_paid, normalize_phone
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

lookup = st.text_input(
    "Enter your mobile number or email address",
    key="orders_lookup",
    placeholder="e.g. 9876543210",
    icon=":material/search:",
)

if not lookup.strip():
    st.info(
        "Enter the mobile number or email address you used during checkout to track your orders.",
        icon=":material/search:",
    )
    st.stop()

lookup_text = lookup.strip().lower()
lookup_phone = normalize_phone(lookup_text)
orders = [
    order
    for order in load_orders()
    if order["customer"].get("email", "").lower() == lookup_text
    or (
        len(lookup_phone) == 10
        and normalize_phone(order["customer"].get("phone", "")) == lookup_phone
    )
]

if not orders:
    st.warning(f"No previous orders found for '{lookup.strip()}'.", icon=":material/search_off:")
    st.page_link("app_pages/shop.py", label="Explore Royal Natural Shop", icon=":material/storefront:")
    st.stop()

payment_flash = st.session_state.pop("payment_flash", None)
if payment_flash:
    st.success(payment_flash, icon=":material/check_circle:")

new_order = st.session_state.pop("last_order_id", None)
new_order_data = next((order for order in orders if order["id"] == new_order), None)
if new_order_data:
    if new_order_data.get("payment_status") == "Pending payment":
        st.info(
            f"Order #{new_order} is created. Complete the UPI/card payment below, then click Verify payment.",
            icon=":material/payments:",
        )
    else:
        st.success(
            f"🎉 Congratulations! Order #{new_order} has been placed successfully! Our dispatch team is packaging your jars in shockproof safety boxes.",
            icon=":material/check_circle:",
        )
        st.balloons()

st.caption(f"Found {len(orders)} order(s) for {lookup.strip()}")

product_lookup = {p["id"]: p for p in load_products()}

for order in reversed(orders):
    payment_status = order.get("payment_status", "Confirmed")
    with st.container(border=True):
        head_col, status_col, total_col = st.columns([3, 2, 1.2], vertical_alignment="center")
        with head_col:
            st.markdown(f"### Order #{order['id']}")
            st.caption(
                f"📅 {order['date']} · 💳 {order['payment_method']} · {payment_status}<br>"
                f"📍 Deliver to: **{order['customer'].get('name', 'Customer')}**, {order['customer']['address'].splitlines()[0]}<br>"
                f"📱 Mobile: {order['customer'].get('phone', 'Not provided')}",
                unsafe_allow_html=True,
            )
        with status_col:
            if payment_status == "Pending payment":
                status_title = "Payment Pending"
                status_detail = "Complete payment to confirm your order"
                status_bg, status_border, status_color = "#fffbeb", "#fde68a", "#92400e"
            elif payment_status == "Paid":
                status_title = "Paid & Confirmed"
                status_detail = "Preparing dispatch · Delivery in 2-3 days"
                status_bg, status_border, status_color = "#ecfdf5", "#a7f3d0", "#065f46"
            else:
                status_title = "Confirmed & Preparing Dispatch"
                status_detail = "Estimated delivery: 2-3 days"
                status_bg, status_border, status_color = "#ecfdf5", "#a7f3d0", "#065f46"
            st.markdown(
                f"""
                <div style="background: {status_bg}; border: 1px solid {status_border}; border-radius: 8px; padding: 6px 12px; font-size: 0.82rem; color: {status_color}; font-weight: 600;">
                    Status: <b>{status_title}</b><br>
                    <span style="font-size: 0.76rem; font-weight: normal;">{status_detail}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with total_col:
            st.metric("Order Total", f"₹{order['total']:g}")

        if payment_status == "Pending payment" and order.get("payment_link"):
            st.caption("Pay on Razorpay's secure page, return here, then verify your payment.")
            pay_col, verify_col = st.columns(2)
            with pay_col:
                st.link_button(
                    "Pay by UPI / Card",
                    order["payment_link"]["url"],
                    icon=":material/payments:",
                    use_container_width=True,
                )
            with verify_col:
                if st.button(
                    "Verify payment",
                    key=f"verify_payment_{order['id']}",
                    icon=":material/verified:",
                    use_container_width=True,
                ):
                    try:
                        paid, message = verify_payment(order)
                    except PaymentError as exc:
                        st.error(str(exc), icon=":material/error:")
                    else:
                        if paid:
                            mark_order_paid(order["id"])
                            st.session_state.payment_flash = (
                                f"Payment verified! Order #{order['id']} is confirmed."
                            )
                            st.rerun()
                        st.info(message, icon=":material/pending:")

        st.divider()
        st.markdown("**Ordered Items:**")
        for item in order["items"]:
            weight = f" ({item['weight']})" if item.get("weight") else ""
            st.markdown(
                f"- 🍯 **{item['name']}**{weight} × {item['qty']} — **₹{item['price'] * item['qty']:g}**"
            )

        if order.get("discount"):
            st.caption(f"🎟️ Discount Applied: {order['discount'].get('coupon', '')} (-₹{order['discount'].get('amount', 0):g})")

        wa_order_help = get_whatsapp_url(
            f"Hi Royal Natural Products, I have an inquiry about my Order #{order['id']} placed on {order['date']}."
        )
        support_col, invoice_col = st.columns([1.4, 1.4])
        with support_col:
            st.markdown(
                f"""
                <a href="{wa_order_help}" target="_blank" class="card-wa-btn" style="max-width: 320px; font-size: 0.88rem; padding: 8px 14px; margin-top: 8px;">
                    <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                    <span>Track / Support on WhatsApp ({WHATSAPP_PHONE_DISPLAY})</span>
                </a>
                """,
                unsafe_allow_html=True,
            )
        with invoice_col:
            dl_col, pr_col = st.columns(2, gap="small")
            with dl_col:
                st.download_button(
                    "Download invoice",
                    data=invoice_bytes(order, product_lookup),
                    file_name=f"Invoice-{order['id']}.html",
                    mime="text/html",
                    icon=":material/download:",
                    key=f"invoice_dl_{order['id']}",
                    use_container_width=True,
                )
            with pr_col:
                if st.button(
                    "Print invoice",
                    icon=":material/print:",
                    key=f"invoice_print_{order['id']}",
                    use_container_width=True,
                ):
                    st.session_state["print_invoice"] = order["id"]
            if st.session_state.get("print_invoice") == order["id"]:
                st.html(print_invoice_script(order, product_lookup))
                if st.button("Close print view", key=f"close_print_{order['id']}"):
                    del st.session_state["print_invoice"]
                    st.rerun()
