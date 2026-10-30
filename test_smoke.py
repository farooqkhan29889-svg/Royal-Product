import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

sys.path.insert(0, ".")

import utils.invoice as invoice
import utils.payments as payments
import utils.store as store


def check(label, cond):
    print(("PASS " if cond else "FAIL ") + label)
    assert cond, f"Check failed: {label}"


def btn(at, user_key):
    try:
        return next(b for b in at.button if b.key == user_key)
    except StopIteration:
        available = [b.key for b in at.button]
        inputs = [(item.key, item.value) for item in at.text_input]
        infos = [item.value for item in at.info]
        warnings = [item.value for item in at.warning]
        raise RuntimeError(
            f"Button {user_key} not found. Available: {available}; "
            f"inputs: {inputs}; info: {infos}; warnings: {warnings}"
        )


def run_checks(payment_state):
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
    at.button[0].click()
    at.run()
    check("invalid mobile rejected", bool(at.error))
    check("cart kept after validation error", at.session_state.cart.get(cart_key) == 1)

    at.text_input(key="checkout_mobile").set_value("98765 43210")
    at.button[0].click()
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

    at.switch_page("app_pages/shop.py")
    at.run()
    btn(at, "add_pure-gold-honey").click()
    at.run()
    at.switch_page("app_pages/checkout.py")
    at.run()
    at.text_input(key="checkout_name").set_value("UPI Test Buyer")
    at.text_input(key="checkout_mobile").set_value("9876543212")
    at.text_area(key="checkout_address").set_value("2 UPI Street, Mumbai")
    at.radio(key="checkout_payment").set_value("UPI / Card via Razorpay")
    at.button[0].click()
    at.run()
    check("online payment needs configuration", bool(at.error))
    check("unconfigured order not saved", len(store.load_orders()) == 1)
    check("cart kept without payment link", sum(at.session_state.cart.values()) == 1)

    payment_state["configured"] = True
    at.button[0].click()
    at.run()
    check("Razorpay order created without exception", not at.exception)
    check("cart cleared after payment link", at.session_state.cart == {})
    online_order = store.load_orders()[-1]
    check("online order starts pending", online_order["payment_status"] == "Pending payment")
    check("payment link attached", online_order["payment_link"]["id"] == "plink_test_123")
    check(
        "hosted payment page shown",
        any(link.url == "https://rzp.io/l/test123" for link in at.get("link_button")),
    )

    at.switch_page("app_pages/orders.py")
    at.run()
    btn(at, f"verify_payment_{online_order['id']}").click()
    at.run()
    check("pending payment not marked paid", store.load_orders()[-1]["payment_status"] == "Pending payment")

    payment_state["paid"] = True
    btn(at, f"verify_payment_{online_order['id']}").click()
    at.run()
    check("verified payment marked paid", store.load_orders()[-1]["payment_status"] == "Paid")
    check(
        "paid confirmation shown",
        any("Payment verified" in element.value for element in at.success),
    )
    check(
        "customer invoice download offered",
        any(b.label == "Download invoice" for b in at.get("download_button")),
    )

    print("ALL CHECKS PASSED")


def run_invoice_checks():
    order = {
        "id": "INV12345",
        "date": "2026-10-25 10:41",
        "customer": {
            "name": "Ali <b>R",
            "phone": "9876543210",
            "email": "ali@example.com",
            "address": "Shop 4, Karond\nIndore 452001",
        },
        "payment_method": "UPI / Card via Razorpay",
        "payment_status": "Paid",
        "items": [
            {"id": "pure-gold-honey", "name": "Pure Gold Honey", "weight": "250g", "price": 299, "qty": 2}
        ],
        "total": 598,
        "discount": {"coupon": "ROYAL15", "amount": 40},
    }
    html_text = invoice.build_invoice_html(order)
    check("invoice carries order id", "INV12345" in html_text)
    check("invoice marks status paid", "PAID" in html_text)
    check("invoice shows grand total", "₹598" in html_text)
    check("invoice lists pack size", "250g" in html_text)
    check("invoice shows coupon", "ROYAL15" in html_text)
    check("invoice breaks multi-line address", "Shop 4, Karond<br>Indore 452001" in html_text)
    check(
        "invoice escapes customer html",
        "Ali <b>R" not in html_text and "Ali &lt;b&gt;R" in html_text,
    )
    check("invoice file is utf-8", invoice.invoice_bytes(order).decode("utf-8") == html_text)

    script = invoice.print_invoice_script(order)
    check("print view uses iframe", "<iframe" in script and "contentWindow.print" in script)
    check("print view embeds invoice", "INV12345" in script)

    pending = {**order, "payment_status": "Pending payment"}
    check("pending invoice label", "PAYMENT PENDING" in invoice.build_invoice_html(pending))
    cod = {**order, "payment_status": "Cash on Delivery"}
    check("cod invoice label", "CASH ON DELIVERY" in invoice.build_invoice_html(cod))


def run_admin_checks():
    orders_before = store.load_orders()
    admin_order = store.save_order(
        {
            "name": "Admin View Buyer",
            "phone": "9800000000",
            "email": "",
            "address": "Nagda Road, Indore",
        },
        [{"id": "neem-honey", "name": "Royal Neem Honey", "weight": "250g", "price": 249, "qty": 1}],
        249,
        "Cash on Delivery (Pay at Doorstep)",
        payment_status="Cash on Delivery",
    )

    at = AppTest.from_file("streamlit_app.py", default_timeout=30)
    at.run()
    at.switch_page("app_pages/admin.py")
    at.run()
    check("admin renders without exception", not at.exception)
    check("admin asks for password", bool(at.text_input) and not at.metric)

    with patch.dict(os.environ, {"ADMIN_PASSWORD": "s3cret"}):
        at.text_input[0].set_value("wrong-pass")
        at.button[0].click()
        at.run()
        check("wrong password stays locked", bool(at.error) and not at.metric)

        at.text_input[0].set_value("s3cret")
        at.button[0].click()
        at.run()
        check("correct password opens dashboard", not at.exception and bool(at.metric))
        check("admin counts every order", int(at.metric[0].value) == len(store.load_orders()))
        check(
            "admin invoice download present",
            any(b.label == "Download invoice" for b in at.get("download_button")),
        )
        check(
            "admin exports csv",
            any(b.label == "Export these orders (CSV)" for b in at.get("download_button")),
        )

        btn(at, f"admin_print_{admin_order['id']}").click()
        at.run()
        check("admin print view renders invoice pane", bool(at.get("html")) and not at.exception)

        at.selectbox[0].set_value("Pending payment")
        at.run()
        pending_total = sum(
            1 for o in orders_before if o.get("payment_status") == "Pending payment"
        )
        check("admin status filter works", int(at.metric[0].value) == pending_total)


def run_payment_api_checks():
    customer = {
        "name": "API Test",
        "phone": "9876543210",
        "email": "api@example.com",
        "address": "Test address",
    }
    with patch.object(
        payments,
        "_request",
        return_value={"id": "plink_123", "short_url": "https://rzp.io/l/test"},
    ) as request:
        link = payments.create_payment_link("ORDER123", 300, customer)
        payload = request.call_args.kwargs["json"]
        check("payment link response parsed", link["id"] == "plink_123")
        check("Razorpay amount uses paise", payload["amount"] == 30000)
        check("Razorpay reference uses order ID", payload["reference_id"] == "ORDER123")
        check("partial payments disabled", payload["accept_partial"] is False)

    order = {
        "id": "ORDER123",
        "total": 300,
        "payment_link": {"id": "plink_123", "url": "https://rzp.io/l/test"},
    }
    paid_response = {
        "reference_id": "ORDER123",
        "amount": 30000,
        "amount_paid": 30000,
        "currency": "INR",
        "status": "paid",
    }
    with patch.object(payments, "_request", return_value=paid_response):
        paid, _ = payments.verify_payment(order)
        check("paid Razorpay response accepted", paid)

    with patch.object(payments, "_request", return_value={**paid_response, "status": "created", "amount_paid": 0}):
        paid, _ = payments.verify_payment(order)
        check("unpaid Razorpay response rejected", not paid)

    with patch.object(payments, "_request", return_value={**paid_response, "amount": 1}):
        try:
            payments.verify_payment(order)
        except payments.PaymentError:
            check("mismatched amount rejected", True)
        else:
            check("mismatched amount rejected", False)


original_orders_file = store.ORDERS_FILE
payment_state = {"configured": False, "paid": False}


def fake_create_payment_link(order_id, total, customer):
    return {"id": "plink_test_123", "url": "https://rzp.io/l/test123"}


def fake_verify_payment(order):
    if payment_state["paid"]:
        return True, "Payment verified successfully."
    return False, "Payment is not complete yet."


def test_smoke():
    global payment_state
    payment_state = {"configured": False, "paid": False}
    try:
        with TemporaryDirectory() as temp_dir:
            store.ORDERS_FILE = Path(temp_dir) / "orders.json"
            with (
                patch.object(payments, "razorpay_configured", side_effect=lambda: payment_state["configured"]),
                patch.object(payments, "create_payment_link", side_effect=fake_create_payment_link),
                patch.object(payments, "verify_payment", side_effect=fake_verify_payment),
            ):
                run_checks(payment_state)
            run_payment_api_checks()
            run_invoice_checks()
            run_admin_checks()
    finally:
        store.ORDERS_FILE = original_orders_file


if __name__ == "__main__":
    test_smoke()
