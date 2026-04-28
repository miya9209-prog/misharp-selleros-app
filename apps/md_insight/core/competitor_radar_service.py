import re
from core.naver_api import search_many

TAG_RE = re.compile(r"<[^>]+>")

def clean_html(text):
    if not isinstance(text, str):
        return text
    return TAG_RE.sub("", text)

def _match_mall(mall_name, selected_malls):
    mall_name = (mall_name or "").strip().lower()
    for mall in selected_malls:
        if mall.lower() in mall_name:
            return True
    return False

def collect_competitors_from_naver(keyword, selected_malls, pages=3, sort="sim"):
    raw_items = search_many(query=keyword, pages=pages, display=100, sort=sort)
    filtered = []
    seen = set()

    for item in raw_items:
        mall = item.get("mallName", "")
        if not _match_mall(mall, selected_malls):
            continue

        name = clean_html(item.get("title", ""))
        price = item.get("lprice", "")
        link = item.get("link", "")
        dedupe_key = (mall, name, price, link)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        filtered.append({
            "site": mall,
            "keyword": keyword,
            "name": name,
            "price": price,
            "link": link,
        })
    return filtered
