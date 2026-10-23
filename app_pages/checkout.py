import streamlit as st

from utils.store import (
    cart_items,
    cart_original_mrp_total,
    cart_subtotal,
    cart_total,
    clear_cart,
    get_coupon_discount,
    save_order,
)
from utils.ui import apply_store_css, render_announcement_bar

apply_store_css()
render_announcement_bar()

if not st.session_state.cart:
    st.info("Your cart is empty — add natural honey or dry fruits before checking out.", icon=":material/remove_shopping_cart:")
    st.page_link("app_pages/shop.py", label="Return to Shop", icon=":material/storefront:")
    st.stop()

applied_coupon = st.session_state.get("applied_coupon")
subtotal = cart_subtotal()
mrp_total = cart_original_mrp_total()
coupon_discount = get_coupon_discount(applied_coupon, subtotal)
final_total = max(0.0, subtotal - coupon_discount)
savings_total = (mrp_total - subtotal) + coupon_discount

checkout_left, checkout_right = st.columns([1.6, 1.2], gap="large")

with checkout_right:
    with st.container(border=True):
        st.subheader("📦 Your Order Summary")
        for product, qty in cart_items():
            item_cols = st.columns([1, 3, 1.2], vertical_alignment="center")
            with item_cols[0]:
                st.image(product["image"], use_container_width=True)
            with item_cols[1]:
                st.markdown(f"**{product['name']}**")
                st.caption(f"Qty: {qty} × ₹{product['price']:g}")
            with item_cols[2]:
                st.markdown(f"**₹{product['price'] * qty:g}**")

        st.divider()
        st.markdown(f"Subtotal: **₹{subtotal:g}**")
        st.markdown("Delivery Charges: :green[**FREE (All India)**]")

        if applied_coupon and coupon_discount > 0:
            st.markdown(
                f"<div style='background: #ecfdf5; color: #065f46; font-weight: 700; padding: 6px 10px; border-radius: 6px; font-size: 0.85rem; margin: 4px 0;'>"
                f"🎟️ Coupon {applied_coupon}: -₹{coupon_discount:g}</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<div style='display: flex; justify-content: space-between; align-items: center; margin: 10px 0; border-top: 2px dashed #fed7aa; padding-top: 10px;'>"
            f"<span style='font-size: 1.1rem; font-weight: 700;'>Total Amount:</span>"
            f"<span style='font-size: 1.35rem; font-weight: 800; color: #047857;'>₹{final_total:g}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div style='background: #fefce8; border: 1px solid #fef08a; padding: 8px 12px; border-radius: 8px; font-size: 0.84rem; color: #854d0e; text-align: center; margin-bottom: 8px;'>"
            f"🎉 <b>You are saving ₹{savings_total:g} on this order!</b>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="font-size: 0.78rem; color: #64748b; line-height: 1.6; margin-top: 10px;">
                🚚 <b>Estimated Delivery:</b> 2 - 4 Business Days<br>
                🔒 <b>Safe & Secure Checkout:</b> SSL 256-Bit Protection<br>
                🛡️ <b>Purity Guarantee:</b> 100% Raw or Money Back
            </div>
            """,
            unsafe_allow_html=True,
        )

with checkout_left:
    with st.form("checkout_form"):
        st.subheader("📍 1. Delivery Information")
        name = st.text_input("Full Name", placeholder="e.g. Ramesh Kumar")
        email = st.text_input("Email Address", placeholder="e.g. ramesh@example.com (for order tracking)")
        address = st.text_area("Complete Delivery Address", placeholder="House/Flat No., Street, Landmark, City, State, Pincode")
        phone = st.text_input("Phone Number (Optional - for delivery rider updates)", placeholder="e.g. 9876543210")

        st.write("")
        st.subheader("💳 2. Select Payment Method")
        payment_method = st.radio(
            "Payment Method",
            [
                "Cash on Delivery (Pay at Doorstep)",
                "Credit / Debit Card (demo)",
                "UPI / GooglePay / PhonePe (demo)",
            ],
            horizontal=False,
            label_visibility="collapsed",
        )

        if "Card" in payment_method:
            st.text_input(
                "Card Number",
                value="4242 4242 4242 4242",
                help="Demo checkout — never real charge.",
            )

        st.markdown(
            """
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px; border-radius: 8px; font-size: 0.82rem; color: #166534; margin: 10px 0;">
                ✓ <b>No Risk:</b> Inspect your natural honey jar on delivery. Pay only when you are 100% happy!
            </div>
            """,
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button(
            f"Confirm & Place Order (₹{final_total:g})",
            icon=":material/lock:",
            use_container_width=True,
        )

if submitted:
    if not name.strip() or not email.strip() or not address.strip():
        st.error("Please fill in your name, email, and delivery address to proceed.", icon=":material/error:")
    else:
        cust_dict = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "address": address.strip(),
        }
        if phone.strip():
            cust_dict["phone"] = phone.strip()

        order = save_order(
            cust_dict,
            [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "price": p["price"],
                    "qty": q,
                }
                for p, q in cart_items()
            ],
            final_total,
            payment_method,
            discount_info={"coupon": applied_coupon, "amount": coupon_discount} if coupon_discount else None,
        )
        clear_cart()
        st.toast("🎉 Your order has been placed successfully!")
        st.session_state.last_order_id = order["id"]
        st.session_state.orders_email = order["customer"]["email"]
        st.switch_page("app_pages/orders.py")
