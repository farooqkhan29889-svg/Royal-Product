"""Store look & feel: Emergent AI Luxury Dark Green & Amber Honey Aesthetic."""

import urllib.parse
import streamlit as st

WHATSAPP_NUMBER = "918770465561"
WHATSAPP_PHONE_DISPLAY = "+91 87704 65561"
BRAND_NAME_HI = "छोटी मकड़ी"
BRAND_NAME_EN = "HONEY"

STORE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,600&family=Rozha+One&display=swap');

:root {
    --bg-dark: #07150D;
    --card-bg: #0C1F14;
    --card-border: rgba(245, 158, 11, 0.22);
    --gold-primary: #F59E0B;
    --gold-light: #FBBF24;
    --gold-dark: #D97706;
    --wa-green: #25D366;
    --wa-hover: #20ba59;
    --text-white: #FFFFFF;
    --text-muted: #94A3B8;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F8FAFC;
    background-color: var(--bg-dark);
}

/* App Background Overrides */
.stApp {
    background-color: var(--bg-dark);
}

/* Clean Professional UI: Hide Streamlit 3-dots, Deploy button, GitHub ribbon, and footer */
#MainMenu, 
header[data-testid="stHeader"], 
[data-testid="stToolbar"], 
footer, 
[data-testid="stDecoration"], 
[data-testid="stStatusWidget"],
.viewerBadge_container__1QSob,
.viewerBadge_link__1QSob,
[class*="viewerBadge"],
[data-testid="manage-app-button"],
.stDeployButton {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.stApp > header {
    display: none !important;
}
.stMainBlockContainer, .block-container {
    padding-top: 1rem !important;
}

/* Header Navbar */
div[class*="st-key-store_header"] {
    background: #07150D;
    border-bottom: 1px solid rgba(245, 158, 11, 0.18);
    padding: 0.9rem 1.2rem;
    margin: -1.5rem -1rem 1.6rem -1rem;
    position: sticky;
    top: 0;
    z-index: 9999;
    backdrop-filter: blur(12px);
}
.brand-container {
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
}
.brand-bee-icon {
    font-size: 1.85rem;
    line-height: 1;
    filter: drop-shadow(0 2px 8px rgba(245, 158, 11, 0.4));
}
.brand-title-wrap {
    display: flex;
    flex-direction: column;
}
.brand-hi {
    font-family: 'Rozha One', 'Playfair Display', serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: #F59E0B;
    letter-spacing: 0.5px;
    line-height: 1.05;
}
.brand-en {
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 3.5px;
    color: #E2E8F0;
    margin-top: 1px;
}
.header-actions {
    display: flex;
    align-items: center;
    gap: 14px;
}
div[class*="st-key-store_header"] a[data-testid="stPageLink-NavLink"] {
    background: #F59E0B;
    color: #111827 !important;
    border-radius: 25px;
    padding: 10px 16px;
    font-weight: 800;
    text-decoration: none;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
    transition: transform 0.2s ease;
}
div[class*="st-key-store_header"] a[data-testid="stPageLink-NavLink"]:hover {
    background: #FBBF24;
    transform: scale(1.04);
}
.header-wa-btn {
    background: rgba(37, 211, 102, 0.12);
    border: 1px solid #25D366;
    color: #25D366 !important;
    padding: 6px 14px;
    border-radius: 25px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    text-decoration: none;
    transition: all 0.2s ease;
}
.header-wa-btn:hover {
    background: #25D366;
    color: #FFFFFF !important;
    text-decoration: none;
}

/* Marquee / Ticker Ribbon */
.marquee-wrapper {
    background: #F59E0B;
    overflow: hidden;
    white-space: nowrap;
    padding: 9px 0;
    margin: 1.2rem -1rem 1.8rem -1rem;
    box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
}
.marquee-content {
    display: inline-block;
    animation: marquee 25s linear infinite;
    color: #111827;
    font-weight: 800;
    font-size: 0.86rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
@keyframes marquee {
    0%   { transform: translateX(0%); }
    100% { transform: translateX(-50%); }
}

/* Hero Section */
.hero-container {
    background: radial-gradient(circle at 50% 20%, #102d1d 0%, #07150D 75%);
    border: 1px solid rgba(245, 158, 11, 0.16);
    border-radius: 24px;
    padding: 2.4rem 1.8rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
}
.hero-hindi-tag {
    color: #F59E0B;
    font-size: 0.92rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 0.6rem;
    display: block;
    text-transform: uppercase;
}
.hero-main-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.15;
    margin: 0 auto 0.8rem auto;
    max-width: 800px;
}
.hero-main-title .white-text {
    color: #FFFFFF;
    display: block;
}
.hero-main-title .gold-text {
    color: #F59E0B;
    display: block;
}
.hero-sub-italic {
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-size: 1.25rem;
    font-weight: 400;
    color: #FEF08A;
    display: block;
    margin-top: 4px;
}
.hero-body-p {
    color: #CBD5E1;
    font-size: 1.02rem;
    line-height: 1.6;
    max-width: 620px;
    margin: 0.8rem auto 1.5rem auto;
}
.hero-pill-badges {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 1.8rem;
}
.hero-pill {
    background: rgba(12, 31, 20, 0.8);
    border: 1px solid rgba(74, 222, 128, 0.25);
    color: #E2E8F0;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 30px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    backdrop-filter: blur(4px);
}
.hero-cta-group {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
}
.hero-btn-primary {
    background: #F59E0B;
    color: #111827 !important;
    font-weight: 800;
    font-size: 1rem;
    padding: 12px 28px;
    border-radius: 30px;
    text-decoration: none;
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.35);
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}
.hero-btn-primary:hover {
    background: #FBBF24;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.5);
    color: #111827 !important;
    text-decoration: none;
}
.hero-btn-secondary {
    background: rgba(12, 31, 20, 0.9);
    border: 1.5px solid #25D366;
    color: #25D366 !important;
    font-weight: 700;
    font-size: 0.96rem;
    padding: 11px 24px;
    border-radius: 30px;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s ease;
}
.hero-btn-secondary:hover {
    background: #25D366;
    color: #FFFFFF !important;
    text-decoration: none;
}

/* Section Header (Matches Image 1 & 2) */
.section-intro-header {
    margin: 2.2rem 0 1.4rem 0;
    text-align: center;
}
.section-tag-gold {
    color: #F59E0B;
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    display: block;
    margin-bottom: 6px;
}
.section-main-heading {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
.section-sub-heading {
    color: #94A3B8;
    font-size: 0.96rem;
    margin: 0;
}

/* Product Card Styling (Matches Image 2, 4, 5) */
div[class*="st-key-card_"] {
    background: #0C1F14 !important;
    border: 1px solid rgba(245, 158, 11, 0.2) !important;
    border-radius: 20px !important;
    padding: 1.1rem !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
    transition: all 0.25s ease !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
div[class*="st-key-card_"]:hover {
    border-color: rgba(245, 158, 11, 0.5) !important;
    transform: translateY(-4px) !important;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.55) !important;
}
div[class*="st-key-card_"] img {
    border-radius: 14px;
    object-fit: cover;
    max-height: 260px;
    width: 100%;
}

/* Product Card Header Badges */
.card-badge-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 8px 0 10px 0;
}
.badge-gold-pill {
    background: #F59E0B;
    color: #111827;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
}
.badge-save-pill {
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid rgba(245, 158, 11, 0.3);
    color: #FBBF24;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
}

/* Product Titles */
.card-hindi-sub {
    color: #F59E0B;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    margin-top: 6px;
    display: block;
}
.card-product-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 2px 0 6px 0;
    line-height: 1.3;
}
.card-product-desc {
    color: #94A3B8;
    font-size: 0.82rem;
    line-height: 1.45;
    margin-bottom: 12px;
}

/* Weight Selector Radios Styled as Emergent AI Pills */
div[class*="st-key-weight_"] div[role="radiogroup"] {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0 12px 0;
}
div[class*="st-key-weight_"] div[role="radiogroup"] label {
    background: rgba(7, 21, 13, 0.75);
    border: 1px solid rgba(245, 158, 11, 0.28);
    border-radius: 25px;
    padding: 5px 14px;
    font-size: 0.82rem;
    font-weight: 700;
    color: #E2E8F0;
    cursor: pointer;
    transition: all 0.2s ease;
}
div[class*="st-key-weight_"] div[role="radiogroup"] label:hover {
    border-color: #F59E0B;
    color: #F59E0B;
}

/* Price Row */
.card-price-row {
    display: flex;
    align-items: baseline;
    gap: 10px;
    margin: 8px 0 14px 0;
}
.card-price-current {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #F59E0B;
}
.card-price-mrp {
    font-size: 1rem;
    color: #64748B;
    text-decoration: line-through;
}

/* Button Overrides */
/* Add to Cart Button (Solid Yellow) */
div[class*="st-key-add_"] button,
div[class*="st-key-dialog_add_"] button {
    background: #F59E0B !important;
    color: #111827 !important;
    border: none !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.5px !important;
    border-radius: 25px !important;
    padding: 0.65rem 1rem !important;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.3) !important;
    transition: all 0.2s ease !important;
}
div[class*="st-key-add_"] button:hover,
div[class*="st-key-dialog_add_"] button:hover {
    background: #FBBF24 !important;
    transform: scale(1.02) !important;
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.45) !important;
}

/* Buy Now Button */
div[class*="st-key-buynow_"] button,
div[class*="st-key-dialog_buynow_"] button {
    background: #10B981 !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    border-radius: 25px !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
}

/* WhatsApp Direct Pill in Card */
.card-wa-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: rgba(7, 21, 13, 0.85);
    border: 1.5px solid #25D366;
    color: #25D366 !important;
    font-weight: 700;
    font-size: 0.92rem;
    padding: 9px 16px;
    border-radius: 25px;
    text-decoration: none !important;
    width: 100%;
    margin-top: 8px;
    box-sizing: border-box;
    transition: all 0.2s ease;
}
.card-wa-btn:hover {
    background: #25D366;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(37, 211, 102, 0.35);
}
.card-wa-btn .wa-icon-svg {
    width: 1.15em;
    height: 1.15em;
    fill: currentColor;
    flex-shrink: 0;
}

/* WhatsApp Consultation Box Button (solid green variant) */
.wa-consult-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    background: #25D366;
    color: #FFFFFF !important;
    font-weight: 800;
    font-size: 1rem;
    padding: 13px 28px;
    border-radius: 30px;
    text-decoration: none !important;
    max-width: 420px;
    margin: 0 auto;
    box-shadow: 0 6px 20px rgba(37, 211, 102, 0.4);
    transition: all 0.2s ease;
}
.wa-consult-btn:hover {
    background: #20ba59;
    color: #FFFFFF !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(37, 211, 102, 0.55);
    text-decoration: none !important;
}
.wa-consult-btn .wa-icon-svg {
    width: 1.3em;
    height: 1.3em;
    fill: #FFFFFF;
    flex-shrink: 0;
}

/* Floating WhatsApp Pulse Button */
.floating-whatsapp {
    position: fixed;
    bottom: 22px;
    right: 22px;
    background: #25D366;
    color: #FFFFFF !important;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.85rem;
    box-shadow: 0 6px 20px rgba(37, 211, 102, 0.5);
    z-index: 999999;
    text-decoration: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    animation: wa-pulse 2s infinite;
}
.floating-whatsapp:hover {
    transform: scale(1.12);
    box-shadow: 0 8px 28px rgba(37, 211, 102, 0.7);
    color: #FFFFFF !important;
}
@keyframes wa-pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.6);
    }
    70% {
        box-shadow: 0 0 0 14px rgba(37, 211, 102, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(37, 211, 102, 0);
    }
}

/* Free Delivery Bar in Cart */
.free-delivery-box {
    background: rgba(12, 31, 20, 0.95);
    border: 1px solid rgba(74, 222, 128, 0.3);
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 1.4rem;
}
.free-delivery-progress {
    height: 8px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    overflow: hidden;
    margin-top: 8px;
}
.free-delivery-fill {
    height: 100%;
    background: linear-gradient(90deg, #F59E0B 0%, #10B981 100%);
    border-radius: 10px;
    transition: width 0.3s ease;
}

/* Checkout Card & Forms */
div[data-testid="stForm"] {
    background: #0C1F14 !important;
    border: 1px solid rgba(245, 158, 11, 0.2) !important;
    border-radius: 18px !important;
    padding: 1.5rem !important;
}
div[data-testid="stForm"] button[kind="primaryFormSubmit"],
.st-key-checkout_form button {
    background: #F59E0B !important;
    color: #111827 !important;
    border: none !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1.4rem !important;
    border-radius: 25px !important;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35) !important;
}

/* Inputs on Dark Mode */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
    background-color: #07150D !important;
    border: 1px solid rgba(245, 158, 11, 0.25) !important;
    color: #F8FAFC !important;
    border-radius: 10px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #F59E0B !important;
    box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
}

/* Six Superfoods Feature Section (Matches Image 4) */
.superfood-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
    margin: 1.8rem 0;
}
.superfood-card {
    background: #0C1F14;
    border: 1px solid rgba(245, 158, 11, 0.16);
    border-radius: 14px;
    padding: 18px;
    transition: transform 0.2s ease;
}
.superfood-card:hover {
    transform: translateY(-3px);
    border-color: rgba(245, 158, 11, 0.4);
}
.superfood-icon {
    font-size: 1.8rem;
    margin-bottom: 8px;
}
.superfood-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #F59E0B;
    margin: 0 0 6px 0;
}
.superfood-text {
    font-size: 0.85rem;
    color: #94A3B8;
    line-height: 1.5;
    margin: 0;
}
/* Floating WhatsApp Button */
.floating-whatsapp {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #25D366;
    color: #FFFFFF !important;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 18px rgba(37, 211, 102, 0.45);
    z-index: 999999;
    text-decoration: none;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    animation: pulse-wa 2.2s infinite;
}
.floating-whatsapp:hover {
    transform: scale(1.1) rotate(5deg);
    background: #20ba59;
    box-shadow: 0 6px 24px rgba(37, 211, 102, 0.6);
}
@keyframes pulse-wa {
    0% {
        box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7);
    }
    70% {
        box-shadow: 0 0 0 15px rgba(37, 211, 102, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(37, 211, 102, 0);
    }
}
</style>
"""


def get_whatsapp_url(message="Hi Chhoti Makdi Honey, I want to order pure honey & dry fruits"):
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}"


def render_header(cart_count_val=0):
    """Renders store branding and session-safe cart navigation."""
    with st.container(key="store_header"):
        brand_col, wa_col, cart_col = st.columns(
            [3.2, 1.2, 1.2], vertical_alignment="center"
        )
        with brand_col:
            st.markdown(
                f"""
                <div class="brand-container">
                    <div class="brand-bee-icon">🐝</div>
                    <div class="brand-title-wrap">
                        <span class="brand-hi">{BRAND_NAME_HI}</span>
                        <span class="brand-en">{BRAND_NAME_EN}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with wa_col:
            st.markdown(
                f"""
                <a href="{get_whatsapp_url('Hi Chhoti Makdi Honey, I want to know more about your pure honey products!')}" target="_blank" class="header-wa-btn">
                    <span>💬 WhatsApp</span>
                </a>
                """,
                unsafe_allow_html=True,
            )
        with cart_col:
            st.page_link(
                "app_pages/cart.py",
                label=f"Cart ({cart_count_val})",
                icon=":material/shopping_cart:",
                use_container_width=True,
            )


def render_marquee_ticker():
    """Renders yellow scrolling ticker bar matching Image 1."""
    text_block = "PURE RAW HONEY  ◆  NO ADDED SUGAR  ◆  100% NATURAL  ◆  DIRECT FROM BEEKEEPERS  ◆  FREE DELIVERY ABOVE ₹499  ◆  NMR TESTED  ◆  SHAHAD KI MITHAS PRAKRITI KE SAATH  ◆  "
    st.markdown(
        f"""
        <div class="marquee-wrapper">
            <div class="marquee-content">
                {text_block * 3}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_section():
    """Renders the luxury hero section matching Image 3."""
    wa_hero_link = get_whatsapp_url("Hi Chhoti Makdi Honey, I want to order Pure Gold Honey & Mix Dry Fruits!")
    st.markdown(
        f"""
        <div class="hero-container">
            <span class="hero-hindi-tag">शहद की मिठास, प्रकृति के साथ</span>
            <h1 class="hero-main-title">
                <span class="white-text">PURE GOLD</span>
                <span class="gold-text">HONEY</span>
                <span class="hero-sub-italic">— Nature's Sweetest Gift</span>
            </h1>
            <p class="hero-body-p">
                Raw forest honey & premium mix dry fruits — no added sugar, no preservatives.
                Pure • Natural • Golden, delivered fresh all over India.
            </p>
            <div class="hero-pill-badges">
                <span class="hero-pill">🍃 100% Natural</span>
                <span class="hero-pill">🛡️ No Added Sugar</span>
                <span class="hero-pill">🚚 All-India Delivery</span>
            </div>
            <div class="hero-cta-group">
                <a href="#collection" class="hero-btn-primary">Shop Now →</a>
                <a href="{wa_hero_link}" target="_blank" class="hero-btn-secondary">
                    <span>💬 Order on WhatsApp</span>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_collection_header():
    """Renders the collection header matching Image 1 & 2."""
    st.markdown(
        """
        <div id="collection" class="section-intro-header">
            <span class="section-tag-gold">हमारे प्रोडक्ट्स — OUR COLLECTION</span>
            <h2 class="section-main-heading">Two jars. One promise of purity.</h2>
            <p class="section-sub-heading">Free all-India delivery on orders above ₹499.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_six_superfoods_section():
    """Renders the Six Superfoods Zero Nonsense section matching Image 4."""
    st.markdown(
        """
        <div style="margin-top: 3rem;">
            <div class="section-intro-header">
                <span class="section-tag-gold">HAR BITE MEIN HEALTH</span>
                <h2 class="section-main-heading">Six superfoods. Zero nonsense.</h2>
                <p class="section-sub-heading">What's inside our jars — and what it does for your body.</p>
            </div>
            <div class="superfood-grid">
                <div class="superfood-card">
                    <div class="superfood-icon">🍯</div>
                    <h3 class="superfood-title">100% Raw & Unheated</h3>
                    <p class="superfood-text">Never boiled or pasteurized. Naturally retains active bee pollen, live enzymes, and organic minerals.</p>
                </div>
                <div class="superfood-card">
                    <div class="superfood-icon">🚫</div>
                    <h3 class="superfood-title">Zero Added Sugar</h3>
                    <p class="superfood-text">No corn syrups, glucose, or artificial sweeteners. Verified pure under stringent NMR lab tests.</p>
                </div>
                <div class="superfood-card">
                    <div class="superfood-icon">🐝</div>
                    <h3 class="superfood-title">Wild Harvested</h3>
                    <p class="superfood-text">Collected straight from wild tribal honeycombs in remote floral forests with ethical beekeeping.</p>
                </div>
                <div class="superfood-card">
                    <div class="superfood-icon">🥜</div>
                    <h3 class="superfood-title">Grade-A Crunchy Nuts</h3>
                    <p class="superfood-text">Whole California almonds, Kashmiri walnuts, Afghan raisins, and nutrient-dense raw pumpkin seeds.</p>
                </div>
                <div class="superfood-card">
                    <div class="superfood-icon">🛡️</div>
                    <h3 class="superfood-title">Ayurvedic Immunity</h3>
                    <p class="superfood-text">Natural defense shield against seasonal cough, sore throat, and morning fatigue. Daily vital strength.</p>
                </div>
                <div class="superfood-card">
                    <div class="superfood-icon">📦</div>
                    <h3 class="superfood-title">Zero Breakage Packaging</h3>
                    <p class="superfood-text">Multi-layered cushion protection ensures your golden glass jars arrive intact at your doorstep.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


WA_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" style="width:1em;height:1em;vertical-align:middle;"><path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.8-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5.1-3.9-10.6-6.6z"/></svg>'


def render_floating_whatsapp():
    """Renders the fixed bottom-right WhatsApp button with real WA icon and pulsing animation."""
    wa_url = get_whatsapp_url("Hi Chhoti Makdi Honey, I am looking at your website and want to place an order!")
    st.markdown(
        f"""
        <a href="{wa_url}" target="_blank" class="floating-whatsapp" title="Chat & Order on WhatsApp ({WHATSAPP_PHONE_DISPLAY})">
            <span style="font-size:1.6rem;display:flex;align-items:center;justify-content:center;">{WA_ICON_SVG}</span>
        </a>
        """,
        unsafe_allow_html=True,
    )


def apply_store_css():
    st.html(STORE_CSS)
    render_floating_whatsapp()

def render_announcement_bar():
    """Placeholder announcement bar – can be customized later."""
    # Simple thin banner for compatibility
    st.markdown("<div style='background:#F59E0B;color:#111827;padding:0.6rem;text-align:center;font-weight:600;'>✨ Welcome to Royal Natural Products – Pure Honey & Dry Fruits ✨</div>", unsafe_allow_html=True)


def discount_pct(price, mrp):
    if not mrp or mrp <= price:
        return 0
    return round((mrp - price) / mrp * 100)


def stars(rating):
    full = min(5, max(0, round(rating)))
    return ":orange[" + "★" * full + "]" + ":gray[" + "☆" * (5 - full) + "]"
