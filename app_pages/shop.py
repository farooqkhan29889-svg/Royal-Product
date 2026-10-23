import streamlit as st

from utils.store import (
    add_to_cart,
    cart_count,
    get_product,
    load_products,
    resolve_variant_data,
)
from utils.ui import (
    WA_ICON_SVG,
    WHATSAPP_PHONE_DISPLAY,
    apply_store_css,
    discount_pct,
    get_whatsapp_url,
    render_collection_header,
    render_header,
    render_hero_section,
    render_marquee_ticker,
    render_six_superfoods_section,
    stars,
)

apply_store_css()
render_header(cart_count())
render_hero_section()
render_marquee_ticker()
render_collection_header()


def instant_buy(product_id, weight=None):
    add_to_cart(product_id, 1, weight=weight)
    st.switch_page("app_pages/checkout.py")


@st.dialog("Product Purity Details", width="large")
def show_product_dialog(product_id):
    product = get_product(product_id)
    if not product:
        st.error("Product not found.")
        return

    left_col, right_col = st.columns([1.1, 1.4], gap="medium")
    with left_col:
        st.image(product["image"], use_container_width=True)
        st.caption(f"Category: **{product.get('category', 'Honey')}**")
        st.caption(":material/verified: FSSAI Certified · 100% Raw & Natural")

    with right_col:
        st.markdown(f"<span style='color: #F59E0B; font-weight: 700;'>{product.get('hindi_title', '')}</span>", unsafe_allow_html=True)
        st.subheader(product["name"])
        st.markdown(
            f"{stars(product['rating'])} **{product['rating']}** "
            f":gray[({product.get('rating_count', 0):,} verified ratings)]"
        )

        variants = product.get("variants", [])
        if variants:
            st.markdown("**Select Pack Size:**")
            variant_names = [v["weight"] for v in variants]
            chosen_w = st.radio("Pack Size", variant_names, horizontal=True, key=f"dialog_weight_{product_id}", label_visibility="collapsed")
            v_data = resolve_variant_data(product, chosen_w)
            price = v_data["price"]
            mrp = v_data["mrp"]
        else:
            chosen_w = product.get("weight", "500g")
            price = product["price"]
            mrp = product["mrp"]

        pct = discount_pct(price, mrp)
        savings = mrp - price
        st.markdown(
            f"### ₹{price:g} "
            f":gray[~~₹{mrp:g}~~] "
            f":orange[**{pct}% OFF**]"
        )
        st.markdown(
            f"<div style='color: #10B981; font-weight: 600; font-size: 0.88rem; margin-bottom: 8px;'>"
            f"💰 You save ₹{savings:g} on this jar today!</div>",
            unsafe_allow_html=True,
        )

        st.markdown("#### About this superfood")
        st.write(product["description"])

        if product.get("highlights"):
            st.markdown("**Key Highlights & Purity:**")
            for h in product["highlights"]:
                st.markdown(f"- ✅ {h}")

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.button(
                "⚡ Buy Now (1-Click)",
                key=f"dialog_buynow_{product_id}",
                use_container_width=True,
                on_click=instant_buy,
                args=(product_id, chosen_w),
            )
        with btn_col2:
            if st.button(
                "+ Add to Cart",
                key=f"dialog_add_{product_id}",
                use_container_width=True,
                on_click=add_to_cart,
                args=(product_id, 1, chosen_w),
            ):
                st.toast(f"✅ {product['name']} ({chosen_w}) added to cart!")

        wa_product_url = get_whatsapp_url(
            f"Hi Chhoti Makdi Honey, I want to order {product['name']} ({chosen_w}) for ₹{price:g}. Please deliver to my address!"
        )
        st.markdown(
            f"""
            <a href="{wa_product_url}" target="_blank" class="card-wa-btn" style="margin-top: 10px;">
                <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                <span>Order on WhatsApp ({WHATSAPP_PHONE_DISPLAY})</span>
            </a>
            """,
            unsafe_allow_html=True,
        )


# Products & Filters
products = load_products()

search_col, cat_col, sort_col = st.columns([2, 1.8, 1.2], gap="small")
with search_col:
    search = st.text_input(
        "Search products",
        placeholder="🔍 Search pure gold honey, chhoti makhi, dry fruits...",
        label_visibility="collapsed",
    )
with cat_col:
    categories = ["All Products"] + sorted({p["category"] for p in products})
    selected_category = st.radio(
        "Category", categories, horizontal=True, label_visibility="collapsed"
    ) or "All Products"
with sort_col:
    sort_option = st.selectbox(
        "Sort By",
        ["Popularity & Rating", "Price: Low to High", "Price: High to Low", "Biggest Discount"],
        label_visibility="collapsed",
    )

# Filter logic
filtered = [
    p
    for p in products
    if (selected_category == "All Products" or p["category"] == selected_category)
    and (
        search.lower() in p["name"].lower()
        or search.lower() in p.get("hindi_title", "").lower()
        or search.lower() in p["description"].lower()
        or search.lower() in p["category"].lower()
    )
]

# Sort logic
if sort_option == "Price: Low to High":
    filtered.sort(key=lambda x: x["price"])
elif sort_option == "Price: High to Low":
    filtered.sort(key=lambda x: x["price"], reverse=True)
elif sort_option == "Biggest Discount":
    filtered.sort(key=lambda x: discount_pct(x["price"], x["mrp"]), reverse=True)
else:
    filtered.sort(key=lambda x: (x.get("rating", 0), x.get("rating_count", 0)), reverse=True)

if not filtered:
    st.info("No products match your search. Try searching for 'Honey' or 'Dry Fruits'.", icon=":material/search_off:")
    st.stop()

# Product Grid (Display 2 or 3 per row depending on width)
cols = st.columns(min(2, len(filtered)), gap="large")

for i, product in enumerate(filtered):
    pid = product["id"]
    with cols[i % len(cols)]:
        with st.container(key=f"card_{pid}"):
            badge_text = product.get("badge", "BESTSELLER")
            save_badge = product.get("discount_badge", "Save 26%")

            st.markdown(
                f"""
                <div class="card-badge-row">
                    <span class="badge-gold-pill">{badge_text}</span>
                    <span class="badge-save-pill">{save_badge}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.image(product["image"], use_container_width=True)

            hindi_label = product.get("hindi_title", "शुद्ध शहद")
            st.markdown(
                f"""
                <span class="card-hindi-sub">{hindi_label}</span>
                <h3 class="card-product-title">{product['name']}</h3>
                <p class="card-product-desc">{product.get('short_desc', product['description'])}</p>
                """,
                unsafe_allow_html=True,
            )

            # Weight Selector Variant Pills
            variants = product.get("variants", [])
            if variants:
                variant_weights = [v["weight"] for v in variants]
                chosen_weight = st.radio(
                    "Select Weight",
                    variant_weights,
                    index=0,
                    horizontal=True,
                    key=f"weight_{pid}",
                    label_visibility="collapsed",
                )
                variant_info = resolve_variant_data(product, chosen_weight)
                curr_price = variant_info["price"]
                curr_mrp = variant_info["mrp"]
            else:
                chosen_weight = product.get("weight", "500g")
                curr_price = product["price"]
                curr_mrp = product["mrp"]

            st.markdown(
                f"""
                <div class="card-price-row">
                    <span class="card-price-current">₹{curr_price:g}</span>
                    <span class="card-price-mrp">₹{curr_mrp:g}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # + ADD TO CART Button
            if st.button(
                "+ ADD TO CART",
                key=f"add_{pid}",
                use_container_width=True,
                on_click=add_to_cart,
                args=(pid, 1),
            ):
                st.toast(f"✅ {product['name']} added to cart!")

            # WhatsApp Direct Order Button
            wa_text = f"Hi Chhoti Makdi Honey, I want to order {product['name']} ({chosen_weight}) for ₹{curr_price:g}. Please confirm availability!"
            wa_href = get_whatsapp_url(wa_text)
            st.markdown(
                f"""
                <a href="{wa_href}" target="_blank" class="card-wa-btn">
                    <span class="wa-icon-svg">{WA_ICON_SVG}</span>
                    <span>WhatsApp</span>
                </a>
                """,
                unsafe_allow_html=True,
            )

            # Details expansion
            with st.expander("🔍 View Purity Details & Reviews", expanded=False):
                st.write(product["description"])
                if product.get("highlights"):
                    for h in product["highlights"]:
                        st.markdown(f"- 🍃 {h}")
                st.caption(f"⭐ Rating: {product['rating']}/5 ({product.get('rating_count', 0)} reviews)")

# Render Six Superfoods Section
render_six_superfoods_section()

# WhatsApp Direct Consultation Box
wa_consult_url = get_whatsapp_url("Hi Chhoti Makdi Honey, I want advice on which raw honey is best for my family.")
st.markdown(
    f"""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem 1.5rem; background: #0C1F14; border-radius: 18px; border: 1px solid rgba(245, 158, 11, 0.25);">
        <h3 style="color: #F59E0B; margin: 0 0 6px 0; font-family: 'Playfair Display', serif;">Need help choosing or want to order directly?</h3>
        <p style="color: #94A3B8; font-size: 0.95rem; margin-bottom: 16px;">
            Our Honey & Superfood Specialists are online on WhatsApp right now at <b>{WHATSAPP_PHONE_DISPLAY}</b>.
        </p>
        <a href="{wa_consult_url}" target="_blank" class="wa-consult-btn">
            <span class="wa-icon-svg">{WA_ICON_SVG}</span>
            <span>Chat on WhatsApp ({WHATSAPP_PHONE_DISPLAY})</span>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)
