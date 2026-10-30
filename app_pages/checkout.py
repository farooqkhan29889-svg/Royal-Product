import streamlit as st

from utils.store import (
    cart_items,
    cart_original_mrp_total,
    cart_subtotal,
    cart_total,
    clear_cart,
    get_coupon_discount,
    new_order_id,
    normalize_phone,
    save_order,
)
from utils.payments import PaymentError, create_payment_link, razorpay_configured
from utils.ui import apply_store_css, render_announcement_bar

RAZORPAY_PAYMENT = "UPI / Card via Razorpay"

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
                st.caption(
                    f"{product['selected_weight']} · Qty: {qty} × ₹{product['price']:g}"
                )
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
        st.caption("Name, mobile number and delivery address are required. Email is optional.")
        name = st.text_input(
            "Full Name", placeholder="e.g. Ramesh Kumar", key="checkout_name"
        )
        phone = st.text_input(
            "Mobile Number",
            placeholder="10-digit mobile number",
            key="checkout_mobile",
            max_chars=16,
        )
        email = st.text_input(
            "Email Address (optional)",
            placeholder="e.g. ramesh@example.com",
            key="checkout_email",
        )
        address = st.text_area(
            "Complete Delivery Address",
            placeholder="House/Flat No., Street, Landmark, City, State, Pincode",
            key="checkout_address",
        )

        st.write("")
        st.subheader("💳 2. Select Payment Method")
        payment_method = st.radio(
            "Payment Method",
            [
                "Cash on Delivery (Pay at Doorstep)",
                RAZORPAY_PAYMENT,
            ],
            horizontal=False,
            label_visibility="collapsed",
            key="checkout_payment",
        )
        if razorpay_configured():
            st.caption("UPI and card payments are processed securely by Razorpay.")
        else:
            st.caption("Razorpay needs API keys in .env. Cash on Delivery is available now.")

        st.markdown(
            """
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px; border-radius: 8px; font-size: 0.82rem; color: #166534; margin: 10px 0;">
                ✓ <b>Cash on Delivery:</b> Pay when your order arrives at your doorstep.
            </div>
            """,
            unsafe_allow_html=True,
        )

        submitted = st.form_submit_button(
            f"Confirm & Place Order (₹{final_total:g})",
            icon=":material/lock:",
            use_container_width=True,
        )

def finish_checkout(order):
    clear_cart()
    st.session_state.last_order_id = order["id"]
    st.session_state.orders_lookup = order["customer"]["phone"]
    st.switch_page("app_pages/orders.py")


if submitted:
    mobile = normalize_phone(phone)
    if not name.strip() or not phone.strip() or not address.strip():
        st.error(
            "Please fill in your name, mobile number, and delivery address.",
            icon=":material/error:",
        )
    elif len(mobile) != 10 or mobile[0] not in "6789":
        st.error(
            "Enter a valid 10-digit Indian mobile number.",
            icon=":material/error:",
        )
    else:
        cust_dict = {
            "name": name.strip(),
            "phone": mobile,
            "email": email.strip().lower(),
            "address": address.strip(),
        }
        order_items = [
            {
                "id": p["id"],
                "name": p["name"],
                "weight": p["selected_weight"],
                "price": p["price"],
                "qty": q,
            }
            for p, q in cart_items()
        ]
        discount_info = (
            {"coupon": applied_coupon, "amount": coupon_discount}
            if coupon_discount
            else None
        )

        if payment_method == RAZORPAY_PAYMENT:
            if not razorpay_configured():
                st.error(
                    "Razorpay is not configured yet. Add API keys to .env or choose Cash on Delivery.",
                    icon=":material/error:",
                )
            else:
                order_id = new_order_id()
                try:
                    payment_link = create_payment_link(order_id, final_total, cust_dict)
                except PaymentError as exc:
                    st.error(str(exc), icon=":material/error:")
                else:
                    order = save_order(
                        cust_dict,
                        order_items,
                        final_total,
                        payment_method,
                        discount_info=discount_info,
                        order_id=order_id,
                        payment_status="Pending payment",
                        payment_link=payment_link,
                    )
                    finish_checkout(order)
        else:
            order = save_order(
                cust_dict,
                order_items,
                final_total,
                payment_method,
                discount_info=discount_info,
                payment_status="Cash on Delivery",
            )
            finish_checkout(order)
