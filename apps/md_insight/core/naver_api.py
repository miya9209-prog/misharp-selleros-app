
import os
import requests
import streamlit as st
from datetime import date, timedelta

SHOPPING_URL = "https://openapi.naver.com/v1/search/shop.json"
DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"


def get_naver_credentials():
    client_id = None
    client_secret = None

    try:
        client_id = st.secrets.get("NAVER_CLIENT_ID")
    except Exception:
        pass
    try:
        client_secret = st.secrets.get("NAVER_CLIENT_SECRET")
    except Exception:
        pass

    client_id = client_id or os.getenv("NAVER_CLIENT_ID")
    client_secret = client_secret or os.getenv("NAVER_CLIENT_SECRET")
    return client_id, client_secret


def naver_api_ready():
    client_id, client_secret = get_naver_credentials()
    return bool(client_id and client_secret)


def get_naver_api_error_message():
    client_id, client_secret = get_naver_credentials()
    if not client_id or not client_secret:
        return "네이버 API 설정 필요"
    return None


def _headers():
    client_id, client_secret = get_naver_credentials()
    if not client_id or not client_secret:
        raise RuntimeError("네이버 API 설정 필요")
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }


def search_naver_shopping(query, display=50, start=1, sort="sim"):
    headers = _headers()
    params = {
        "query": query,
        "display": max(1, min(int(display), 100)),
        "start": max(1, min(int(start), 1000)),
        "sort": sort,
    }
    res = requests.get(SHOPPING_URL, headers={k: v for k, v in headers.items() if k != 'Content-Type'}, params=params, timeout=20)
    res.raise_for_status()
    return res.json()


def search_many(query, pages=2, display=50, sort="sim"):
    items = []
    for page in range(pages):
        start = page * display + 1
        data = search_naver_shopping(query=query, display=display, start=start, sort=sort)
        batch = data.get("items", [])
        if not batch:
            break
        items.extend(batch)
        if len(batch) < display:
            break
    return items


def request_datalab(keyword_groups, time_unit="date", start_date=None, end_date=None, device=None, gender=None, ages=None):
    if start_date is None:
        start_date = date.today() - timedelta(days=90)
    if end_date is None:
        end_date = date.today()
    payload = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
    }
    if device:
        payload["device"] = device
    if gender:
        payload["gender"] = gender
    if ages:
        payload["ages"] = ages

    res = requests.post(DATALAB_URL, headers=_headers(), json=payload, timeout=25)
    res.raise_for_status()
    return res.json()
