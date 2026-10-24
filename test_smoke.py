import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from streamlit.testing.v1 import AppTest

sys.path.insert(0, ".")

import utils.store as store


def check(label, cond):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        sys.exit(1)


def btn(at, user_key):
    return next(b for b in at.button if b.key == user_key)


def run_checks():
    at = AppTest.from_file("streamlit_app.py", default_timeout=30)
    at.run()
    check("shop renders without exception", not at.exception)
    check("product cards render", at.session_state.cart == {})

    btn(at, "add_chhoti-makhi-honey").click()
    at.run()
    cart_key = "chhoti-makhi-honey::250g"
    check("selected weight added to cart", at.session_state.cart.get(cart_key) == 1)

    at.switch_page("app_pages/cart.py")
    at.run()
    check("cart page ok", not at.exception and len(at.number_input) >= 1)

    at.number_input(key=f"qty_{cart_key}").set_value(2)
    at.run()
    check("variant quantity updates", at.session_state.cart.get(cart_key) == 2)

    btn(at, f"remove_{cart_key}").click()
    at.run()
    check("variant remove works", at.session_state.cart == {})

    at.switch_page("app_pages/shop.py")
    at.run()
    btn(at, "add_chhoti-makhi-honey").click()
    at.run()

    at.switch_page("app_pages/checkout.py")
    at.run()
    check("checkout page ok", not at.exception)

    at.text_input(key="checkout_name").set_value("Test Buyer")
    at.text_input(key="checkout_mobile").set_value("12345")
    at.text_input(key="checkout_email").set_value("buyer@example.com")
    at.text_area(key="checkout_address").set_value("1 Main Street, Springfield")
    at.form_submit_button[0].click()
    at.run()
    check("invalid mobile rejected", bool(at.error))
    check("cart kept after validation error", at.session_state.cart.get(cart_key) == 1)

    at.text_input(key="checkout_mobile").set_value("98765 43210")
    at.form_submit_button[0].click()
    at.run()
    check("no exception after COD checkout", not at.exception)
    check("cart cleared after order", at.session_state.cart == {})

    orders = store.load_orders()
    check("order persisted", len(orders) == 1)
    last = orders[-1]
    check("customer details saved", last["customer"] == {
        "name": "Test Buyer",
        "phone": "9876543210",
        "email": "buyer@example.com",
        "address": "1 Main Street, Springfield",
    })
    check("COD payment saved", last["payment_method"] == "Cash on Delivery (Pay at Doorstep)")
    check(
        "order item includes weight",
        last["items"][0]["id"] == "chhoti-makhi-honey"
        and last["items"][0]["weight"] == "250g"
        and last["items"][0]["qty"] == 1,
    )
    check(
        "order confirmation shown",
        any(last["id"] in element.value for element in at.markdown),
    )

    print("ALL CHECKS PASSED")


original_orders_file = store.ORDERS_FILE
try:
    with TemporaryDirectory() as temp_dir:
        store.ORDERS_FILE = Path(temp_dir) / "orders.json"
        run_checks()
finally:
    store.ORDERS_FILE = original_orders_file
