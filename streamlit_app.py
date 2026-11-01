import streamlit as st
from utils.ui import render_sidebar

st.set_page_config(
    page_title="छोटी मकड़ी HONEY — 100% Pure Raw Honey & Dry Fruits",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "cart" not in st.session_state:
    st.session_state.cart = {}

page = st.navigation(
    [
        st.Page("app_pages/shop.py", title="Shop", icon=":material/storefront:", default=True),
        st.Page("app_pages/cart.py", title="Cart", icon=":material/shopping_cart:"),
        st.Page("app_pages/checkout.py", title="Checkout", icon=":material/credit_card:"),
        st.Page("app_pages/orders.py", title="Orders", icon=":material/receipt_long:"),
        st.Page("app_pages/admin.py", title="Owner Dashboard", icon=":material/shield:"),
    ],
    position="sidebar",
)

# Render sidebar on every page
render_sidebar()

if page.title != "Shop":
    st.title(page.title)

page.run()
