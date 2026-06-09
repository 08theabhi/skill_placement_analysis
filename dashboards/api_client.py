import httpx
import os
import streamlit as st

def get_api_url():
    # Try Streamlit secrets first, then env var, then default
    try:
        if hasattr(st, 'secrets') and "API_URL" in st.secrets:
            return st.secrets["API_URL"]
    except Exception:
        pass
    return os.getenv("API_URL", "http://localhost:8000")

def api_get(endpoint: str, params: dict = None):
    try:
        url = f"{get_api_url()}{endpoint}"
        with httpx.Client(timeout=30) as client:
            r = client.get(url, params=params)
            if r.status_code == 200:
                return r.json()
            return None
    except Exception:
        return None

def api_post(endpoint: str, data: dict = None):
    try:
        url = f"{get_api_url()}{endpoint}"
        with httpx.Client(timeout=60) as client:
            r = client.post(url, json=data or {})
            if r.status_code == 200:
                return r.json()
            return None
    except Exception:
        return None
