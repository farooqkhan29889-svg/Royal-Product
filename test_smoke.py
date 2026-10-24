import sys

from streamlit.testing.v1 import AppTest

sys.path.insert(0, ".")


def check(label, cond):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        sys.exit(1)


def btn(at, user_key):
    return next(b for b in at.button if b.key == user_key)


at = AppTest.from_file("streamlit_app.py", default_timeout=30)
at.run()
check("shop renders without exception", not at.exception)
check("product cards render", at.session_state.cart == {})

# add a product to cart (card default weight = first variant)
btn(at, "add_chhoti-makhi-honey").click()
at.run()
cart = at.session_state.cart
check(
    "cart has chhoti makhi qty 1 with weight",
    sum(cart.values()) == 1 and any(k.startswith("chhoti-makhi-honey") for k in cart),
)

# switch to cart page
at.switch_page("app_pages/cart.py")
at.run()
check("cart page ok", not at.exception and len(at.number_input) >= 1)

# switch to checkout, fill form, submit
at.switch_page("app_pages/checkout.py")
at.run()
check("checkout page ok", not at.exception)
at.text_input[0].set_value("Test Buyer")
at.text_input[1].set_value("buyer@example.com")
at.text_area[0].set_value("1 Main Street, Springfield")
submit = [b for b in at.button if "checkout_form" in str(b.key)][0]
submit.click()
at.run()
check("no exception after checkout", not at.exception)
check("cart cleared after order", at.session_state.cart == {})

# orders page should show the order for that email
from utils.store import load_orders

orders = load_orders()
check("order persisted", any(o["customer"]["email"] == "buyer@example.com" for o in orders))
last = orders[-1]
check(
    "order items correct",
    any(i["id"] == "chhoti-makhi-honey" and i["qty"] == 1 for i in last["items"]),
)

print("ALL CHECKS PASSED")
