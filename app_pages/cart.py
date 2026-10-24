import streamlit as st

from utils.store import (
    AVAILABLE_COUPONS,
    cart_count,
    cart_items,
    cart_original_mrp_total,
    cart_subtotal,
    cart_total,
    get_coupon_discount,
    remove_from_cart,
    set_cart_qty,
)
from utils.ui import (
    WA_ICON_SVG,
    WHATSAPP_PHONE_DISPLAY,
    apply_store_css,
    get_whatsapp_url,
    render_announcement_bar,
)

apply_store_css()
render_announcement_bar()


def update_qty(cart_key):
    set_cart_qty(cart_key, st.session_state[f"qty_{cart_key}"])


if not st.session_state.cart:
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem 1rem; background: #ffffff; border-radius: 16px; border: 1px dashed #fed7aa; margin-top: 1rem;">
            <div style="font-size: 3.5rem; margin-bottom: 0.8rem;">🛒</div>
            <h3 style="color: #78350f; margin-bottom: 0.4rem;">Your Shopping Cart is Empty</h3>
            <p style="color: #64748b; font-size: 0.95rem; max-width: 450px; margin: 0 auto 1.5rem auto;">
                Explore our handpicked collection of 100% raw forest honey and premium dry fruits. Don't miss out on today's festive discounts!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.page_link(
            "app_pages/shop.py",
            label="Explore Royal Superfoods & Deals",
            icon=":material/storefront:",
            use_container_width=True,
        )
    st.stop()

items = cart_items()
subtotal = cart_subtotal()
mrp_total = cart_original_mrp_total()
total_savings = mrp_total - subtotal

# Free delivery banner
st.markdown(
    """
    <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 10px; padding: 12px 18px; margin-bottom: 1.2rem; display: flex; align-items: center; justify-content: space-between;">
        <span style="color: #065f46; font-weight: 700; font-size: 0.92rem;">
            🎉 Congratulations! Your order qualifies for <b>FREE EXPRESS SHIPPING</b>!
        </span>
        <span style="background: #10b981; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.76rem; font-weight: 700;">
            SAVED ₹80
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([2.3, 1.2], gap="large")

with left:
    st.markdown(f"#### Cart Items ({cart_count()} items)")
    for product, qty in items:
        cart_key = product["cart_key"]
        with st.container(border=True):
            img_col, info_col, qty_col, price_col = st.columns(
                [1.2, 2.6, 1.2, 1.2], vertical_alignment="center"
            )
            with img_col:
                st.image(product["image"], use_container_width=True)
            with info_col:
                st.markdown(f"**{product['name']}**")
                st.caption(
                    f"{product['selected_weight']} · Unit: ₹{product['price']:g} "
                    f"(MRP ~~₹{product.get('mrp', product['price']):g}~~)"
                )
                if product.get("stock_left") and product["stock_left"] <= 5:
                    st.markdown(
                        f"<span style='color: #dc2626; font-size: 0.75rem; font-weight: 700;'>⚠️ Only {product['stock_left']} left in stock</span>",
                        unsafe_allow_html=True,
                    )
                st.button(
                    "Remove",
                    key=f"remove_{cart_key}",
                    icon=":material/delete:",
                    on_click=remove_from_cart,
                    args=(cart_key,),
                )
            with qty_col:
                st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=99,
                    value=qty,
                    key=f"qty_{cart_key}",
                    label_visibility="collapsed",
                    on_change=update_qty,
                    args=(cart_key,),
                )
            with price_col:
                st.markdown(f"### ₹{product['price'] * qty:g}")
                if product.get("mrp") and product["mrp"] > product["price"]:
                    item_saved = (product["mrp"] - product["price"]) * qty
                    st.caption(f":green[Saved ₹{item_saved:g}]")

with right:
    with st.container(key="summary_cart"):
        st.subheader("Order Summary")

        # Coupon input
        st.markdown("**Have a Discount Coupon?**")
        coupon_input_col, coupon_btn_col = st.columns([2, 1])
        with coupon_input_col:
            coupon_val = st.text_input(
                "Coupon",
                placeholder="e.g. ROYAL15",
                label_visibility="collapsed",
                key="coupon_text_input",
                value=st.session_state.get("applied_coupon", ""),
            )
        with coupon_btn_col:
            if st.button("Apply", key="apply_coupon_btn", use_container_width=True):
                code = coupon_val.strip().upper()
                if code in AVAILABLE_COUPONS:
                    st.session_state.applied_coupon = code
                    st.toast(f"🎉 Coupon {code} applied!")
                    st.rerun()
                else:
                    st.error("Invalid coupon code.")

        # Quick click coupons
        st.markdown(
            """
            <div style="margin: 6px 0 14px 0; font-size: 0.76rem; color: #64748b;">
                Available coupons: <b style="color: #b45309;">ROYAL15</b> (15% off) | <b style="color: #b45309;">HONEY50</b> (₹50 off)
            </div>
            """,
            unsafe_allow_html=True,
        )

        applied_coupon = st.session_state.get("applied_coupon")
        coupon_discount = get_coupon_discount(applied_coupon, subtotal)
        final_total = max(0.0, subtotal - coupon_discount)

        st.markdown(f"Original Price:&nbsp;&nbsp;**₹{mrp_total:g}**")
        st.markdown(f"Product Discount:&nbsp;&nbsp;:green[-₹{total_savings:g}]")

        if applied_coupon and coupon_discount > 0:
            st.markdown(
                f"<div class='coupon-tag'><span>🎟️ Code: <b>{applied_coupon}</b></span> <span>-₹{coupon_discount:g}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown("Delivery Charges:&nbsp;&nbsp;:green[**FREE**]")
        st.divider()

        st.markdown(
            f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>"
            f"<span style='font-size: 1.15rem; font-weight: 700; color: #1e293b;'>Total Payable:</span>"
            f"<span style='font-size: 1.4rem; font-weight: 800; color: #047857;'>₹{final_total:g}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 8px 12px; font-size: 0.82rem; color: #166534; font-weight: 600; text-align: center; margin-bottom: 14px;'>"
            f"💰 You are saving a total of ₹{(total_savings + coupon_discount):g} on this order!"
            f"</div>",
            unsafe_allow_html=True,
        )

        if st.button(
            "Proceed to Checkout",
            key="proceed_checkout",
            icon=":material/credit_card:",
            use_container_width=True,
        ):
            st.switch_page("app_pages/checkout.py")

        cart_summary_text = " | ".join(
            [f"{p['name']} ({p['selected_weight']}) x{q}" for p, q in items]
        )
        cart_wa_link = get_whatsapp_url(
            f"Hi Royal Natural Products, I want to order my cart items: {cart_summary_text}. Total Payable: ₹{final_total:g}. Please deliver to my address!"
        )
        st.markdown(
            f"""
            <a href="{cart_wa_link}" target="_blank" class="card-wa-btn" style="margin-top: 10px;">
                <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                <span>Order Cart on WhatsApp ({WHATSAPP_PHONE_DISPLAY})</span>
            </a>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="font-size: 0.78rem; color: #64748b; margin-top: 14px; line-height: 1.6;">
                🔒 <b>Safe & Secure Checkout</b><br>
                💵 Cash on Delivery Available<br>
                ⚡ Dispatched in 24 Hours in Shock-proof Jars<br>
                🛡️ 7-Day Money Back Guarantee
            </div>
            """,
            unsafe_allow_html=True,
        )
