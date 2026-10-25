"""Printable HTML tax invoices for orders (no external PDF packages needed)."""

import base64
import html
import io
import json

from PIL import Image

STORE_NAME = "Royal Natural Products"
STORE_TAGLINE = "Chhoti Makdi Honey — 100% Raw Honey & Dry Fruits"
STORE_PHONE = "+91 87704 65561"
STORE_ADDRESS = "Royal Natural Products, India"

BRAND_DARK = "#0b3d2e"
BRAND_GOLD = "#c9a227"

_STATUS_LABELS = {
    "Paid": "PAID",
    "Cash on Delivery": "CASH ON DELIVERY",
    "Pending payment": "PAYMENT PENDING",
}


def _thumb_data_uri(path, size=150):
    try:
        img = Image.open(path)
        img.thumbnail((size, size))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()
    except Exception:
        return ""


def _esc(value):
    return html.escape(str(value or ""))


def _money(value):
    amount = float(value)
    return f"₹{amount:,.0f}" if amount == int(amount) else f"₹{amount:,.2f}"


def _status_label(order):
    return _STATUS_LABELS.get(order.get("payment_status"), order.get("payment_status") or "")


def build_invoice_html(order, product_lookup=None, auto_print=False):
    """Return a self-contained, print-ready HTML invoice for one order."""
    product_lookup = product_lookup or {}
    customer = order.get("customer", {})
    items = order.get("items", [])
    discount = order.get("discount") or {}
    discount_amount = float(discount.get("amount", 0) or 0)
    subtotal = sum(float(i["price"]) * int(i["qty"]) for i in items)
    total = float(order.get("total", subtotal))
    gst_rate = 5.0
    taxable = max(0.0, total / (1 + gst_rate / 100))
    gst_amount = total - taxable

    rows = []
    for index, item in enumerate(items, start=1):
        product = product_lookup.get(item.get("id")) or {}
        thumb = _thumb_data_uri(product.get("image", ""))
        image_cell = (
            f'<img src="{thumb}" alt="" style="width:56px;height:56px;object-fit:cover;border-radius:8px;">'
            if thumb
            else ""
        )
        weight = item.get("weight") or product.get("weight") or "-"
        mrp = item.get("mrp") or product.get("mrp")
        rows.append(
            f"""
            <tr>
              <td class="c">{index}</td>
              <td class="img">{image_cell}</td>
              <td><b>{_esc(item.get('name'))}</b><br><span class="sub">{_esc(weight)}</span></td>
              <td class="c">{_esc(weight)}</td>
              <td class="r">{_money(item['price'])}</td>
              <td class="c">{int(item['qty'])}</td>
              <td class="r"><b>{_money(float(item['price']) * int(item['qty']))}</b></td>
            </tr>
            """
        )

    coupon_row = (
        f'<div class="line"><span>Coupon {_esc(discount.get("coupon"))}</span><span>-{_money(discount_amount)}</span></div>'
        if discount_amount
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Invoice {_esc(order.get('id'))} — {_esc(STORE_NAME)}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Segoe UI", Arial, sans-serif; color: #14251d; margin: 0; padding: 24px; background: #f6f7f5; }}
  .sheet {{ max-width: 780px; margin: auto; background: #fff; border: 1px solid #e2e6e3; border-top: 6px solid {BRAND_DARK}; padding: 26px 30px; }}
  header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; border-bottom: 2px dashed #e3d9b8; padding-bottom: 16px; }}
  .brand h1 {{ margin: 0; font-size: 1.45rem; color: {BRAND_DARK}; letter-spacing: .3px; }}
  .brand p {{ margin: 4px 0 0; font-size: .8rem; color: #5f6f68; }}
  .ttl {{ text-align: right; }}
  .ttl h2 {{ margin: 0; font-size: 1.25rem; color: {BRAND_GOLD}; letter-spacing: 2px; }}
  .ttl div {{ font-size: .82rem; color: #46554e; margin-top: 5px; }}
  .badge {{ display: inline-block; margin-top: 8px; padding: 4px 10px; border-radius: 999px; font-size: .72rem; font-weight: 700; letter-spacing: .5px; }}
  .badge.paid {{ background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }}
  .badge.hold {{ background: #fff7ed; color: #9a3412; border: 1px solid #fed7aa; }}
  .meta {{ display: flex; flex-wrap: wrap; gap: 26px; margin: 18px 0; font-size: .84rem; }}
  .meta h4 {{ margin: 0 0 5px; font-size: .72rem; text-transform: uppercase; letter-spacing: 1px; color: {BRAND_DARK}; }}
  .meta p {{ margin: 2px 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
  thead th {{ background: {BRAND_DARK}; color: #fff; padding: 9px 8px; text-align: left; font-size: .72rem; letter-spacing: .6px; text-transform: uppercase; }}
  thead th.r {{ text-align: right; }}
  thead th.c {{ text-align: center; }}
  tbody td {{ padding: 11px 8px; border-bottom: 1px solid #eef1ef; vertical-align: middle; }}
  tbody td.r {{ text-align: right; }}
  tbody td.c {{ text-align: center; }}
  tbody td.img {{ width: 68px; }}
  .sub {{ color: #6b7c74; font-size: .76rem; }}
  .totals {{ display: flex; justify-content: flex-end; margin-top: 16px; }}
  .totals .box {{ width: 290px; font-size: .85rem; }}
  .line {{ display: flex; justify-content: space-between; padding: 4px 0; }}
  .grand {{ display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 9px; border-top: 2px solid {BRAND_GOLD}; font-weight: 800; font-size: 1rem; color: {BRAND_DARK}; }}
  .note {{ margin-top: 20px; font-size: .76rem; color: #6b7c74; border-top: 1px solid #eef1ef; padding-top: 12px; }}
  .note b {{ color: {BRAND_DARK}; }}
  .thanks {{ text-align: center; margin-top: 18px; font-size: .9rem; color: {BRAND_DARK}; }}
  .toolbar {{ max-width: 780px; margin: 0 auto 16px; text-align: right; }}
  .toolbar button {{ background: {BRAND_DARK}; color: #fff; border: 0; border-radius: 8px; padding: 10px 18px; font-size: .88rem; font-weight: 700; cursor: pointer; }}
  @media print {{
    body {{ background: #fff; padding: 0; }}
    .sheet {{ border: 0; max-width: none; padding: 0; }}
    .toolbar {{ display: none; }}
  }}
</style>
</head>
<body>
  <div class="toolbar"><button onclick="window.print()">Print / Save as PDF</button></div>
  <div class="sheet">
    <header>
      <div class="brand">
        <h1>🐝 {_esc(STORE_NAME)}</h1>
        <p>{_esc(STORE_TAGLINE)}<br>{_esc(STORE_ADDRESS)}<br>WhatsApp: {_esc(STORE_PHONE)}</p>
      </div>
      <div class="ttl">
        <h2>TAX INVOICE</h2>
        <div>Invoice No: <b>{_esc(order.get('id'))}</b><br>Date: {_esc(order.get('date'))}<br>Payment: {_esc(order.get('payment_method'))}</div>
        <span class="badge {'paid' if _status_label(order) in ('PAID', 'CASH ON DELIVERY') else 'hold'}">{_esc(_status_label(order))}</span>
      </div>
    </header>

    <div class="meta">
      <div>
        <h4>Billed To</h4>
        <p><b>{_esc(customer.get('name'))}</b></p>
        <p>{_esc(customer.get('address')).replace(chr(10), '<br>')}</p>
        <p>Mobile: {_esc(customer.get('phone'))}</p>
        {f"<p>Email: {_esc(customer.get('email'))}</p>" if customer.get('email') else ""}
      </div>
      <div>
        <h4>Order Details</h4>
        <p>Order ID: <b>{_esc(order.get('id'))}</b></p>
        <p>Placed: {_esc(order.get('date'))}</p>
        <p>Items: {len(items)}</p>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th class="c">#</th><th>Product</th><th>Description</th><th class="c">Pack</th>
          <th class="r">Unit Price</th><th class="c">Qty</th><th class="r">Amount</th>
        </tr>
      </thead>
      <tbody>{''.join(rows)}</tbody>
    </table>

    <div class="totals">
      <div class="box">
        <div class="line"><span>Subtotal</span><span>{_money(subtotal)}</span></div>
        <div class="line"><span>Delivery</span><span>FREE</span></div>
        {coupon_row}
        <div class="line"><span>GST @ {gst_rate:g}% (incl.)</span><span>{_money(gst_amount)}</span></div>
        <div class="grand"><span>Grand Total</span><span>{_money(total)}</span></div>
      </div>
    </div>

    <p class="thanks">Thank you for choosing purity. 🍯</p>
    <div class="note">
      <b>Terms:</b> 100% raw honey &amp; grade-A dry fruits. Money-back purity guarantee.
      Delivery in 2–4 business days all over India.<br>
      <b>Support:</b> WhatsApp {_esc(STORE_PHONE)} for tracking, bills or product help.
      This is a computer-generated invoice and does not require a signature.
    </div>
  </div>
  <script>if (window.print && {'true' if auto_print else 'sessionStorage.getItem("autoPrint")'}) {{ setTimeout(function () {{ window.print(); }}, 400); }}</script>
</body>
</html>"""


def invoice_bytes(order, product_lookup=None):
    return build_invoice_html(order, product_lookup).encode("utf-8")


def print_invoice_script(order, product_lookup=None):
    """HTML that shows the invoice in an iframe and opens the browser print dialog."""
    payload = json.dumps(build_invoice_html(order, product_lookup))
    return (
        '<iframe style="width:100%;height:360px;border:1px solid #d8e0da;border-radius:10px"></iframe>'
        "<script>(function(){var doc=" + payload + ";"
        "var f=document.previousElementSibling;"
        "f.srcdoc=doc;"
        "f.onload=function(){try{f.contentWindow.focus();f.contentWindow.print();}catch(e){}};"
        "})();</script>"
    )
