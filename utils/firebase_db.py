"""Firebase Firestore integration for Royal Natural Products store."""

import json
import logging
import os
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = ROOT / "data" / "products.json"
ORDERS_FILE = ROOT / "data" / "orders.json"

_firestore_client = None
_firebase_initialized = False


def _find_service_account_path() -> Path | None:
    # 1. Environment variable
    env_path = os.environ.get("FIREBASE_KEY_PATH") or os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if env_path and Path(env_path).exists():
        return Path(env_path)

    # 2. Look for any firebase-adminsdk json or firebase-key.json in root
    candidates = list(ROOT.glob("*firebase-adminsdk*.json")) + list(ROOT.glob("firebase*.json"))
    if candidates:
        return candidates[0]

    return None


def get_firestore_client():
    """Initializes and returns the Firestore client singleton, or None if credentials are missing."""
    global _firestore_client, _firebase_initialized
    if _firestore_client is not None:
        return _firestore_client

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            key_path = _find_service_account_path()
            if key_path and key_path.exists():
                cred = credentials.Certificate(str(key_path))
                firebase_admin.initialize_app(cred)
                _firebase_initialized = True
            elif hasattr(st, "secrets") and "firebase" in st.secrets:
                # Support deployment on Streamlit Cloud via secrets.toml
                firebase_secrets = dict(st.secrets["firebase"])
                cred = credentials.Certificate(firebase_secrets)
                firebase_admin.initialize_app(cred)
                _firebase_initialized = True
            else:
                return None

        _firestore_client = firestore.client()
        return _firestore_client
    except Exception as e:
        logger.warning(f"Could not initialize Firebase Firestore: {e}")
        return None


def is_firebase_available() -> bool:
    client = get_firestore_client()
    return client is not None


def seed_initial_data_if_needed():
    """Seeds products and existing orders to Firestore if Firestore collections are empty."""
    db = get_firestore_client()
    if not db:
        return

    try:
        # Check products
        prod_docs = list(db.collection("products").limit(1).stream())
        if not prod_docs and PRODUCTS_FILE.exists():
            local_prods = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
            batch = db.batch()
            for p in local_prods:
                pid = p.get("id")
                if pid:
                    doc_ref = db.collection("products").document(pid)
                    batch.set(doc_ref, p)
            batch.commit()
            logger.info(f"Seeded {len(local_prods)} products to Firestore.")

        # Check orders
        order_docs = list(db.collection("orders").limit(1).stream())
        if not order_docs and ORDERS_FILE.exists():
            local_orders = json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
            # Seed up to 50 orders in batch
            batch = db.batch()
            count = 0
            for o in local_orders:
                oid = o.get("id")
                if oid:
                    doc_ref = db.collection("orders").document(oid)
                    batch.set(doc_ref, o)
                    count += 1
                    if count >= 400:  # Firestore batch limit is 500
                        break
            if count > 0:
                batch.commit()
                logger.info(f"Seeded {count} orders to Firestore.")
    except Exception as e:
        logger.warning(f"Error seeding data to Firestore: {e}")


def firestore_load_products():
    """Loads products from Firestore with fallback to local JSON."""
    db = get_firestore_client()
    if db:
        try:
            docs = list(db.collection("products").stream())
            if docs:
                return [d.to_dict() for d in docs]
        except Exception as e:
            logger.warning(f"Failed to fetch products from Firestore: {e}")

    # Fallback to local file
    if PRODUCTS_FILE.exists():
        return json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    return []


def firestore_load_orders():
    """Loads all orders from Firestore with fallback to local JSON."""
    db = get_firestore_client()
    if db:
        try:
            # Query orders ordered by date descending if possible, or simple stream
            docs = list(db.collection("orders").stream())
            if docs:
                orders = [d.to_dict() for d in docs]
                # Sort by date descending
                orders.sort(key=lambda x: x.get("date", ""), reverse=False)
                return orders
        except Exception as e:
            logger.warning(f"Failed to fetch orders from Firestore: {e}")

    if ORDERS_FILE.exists():
        try:
            return json.loads(ORDERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def firestore_save_order(order: dict):
    """Saves or updates an order in Firestore."""
    db = get_firestore_client()
    if db:
        try:
            order_id = order.get("id")
            if order_id:
                db.collection("orders").document(order_id).set(order)
                return True
        except Exception as e:
            logger.warning(f"Failed to save order to Firestore: {e}")
    return False


def firestore_update_order(order_id: str, updates: dict):
    """Updates fields of an existing order in Firestore."""
    db = get_firestore_client()
    if db:
        try:
            db.collection("orders").document(order_id).update(updates)
            return True
        except Exception as e:
            logger.warning(f"Failed to update order {order_id} in Firestore: {e}")
    return False
