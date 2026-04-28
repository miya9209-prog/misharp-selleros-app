import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

SITES = [
    ("조아맘", "https://www.joamom.co.kr/product/list.html?cate_no=24"),
    ("캔마트", "https://canmart.co.kr/product/list.html?cate_no=28"),
]

def _safe_text(node):
    return node.get_text(" ", strip=True) if node else ""

def crawl_site(name, url):
    res = requests.get(url, headers=HEADERS, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    items = []
    # 사이트 구조가 달라질 수 있어 대표 셀렉터를 몇 개 시도
    candidates = soup.select(".prdList li, ul.prdList > li, .item_list li")
    for p in candidates:
        try:
            a = p.select_one("a")
            if not a:
                continue
            name_node = p.select_one(".name, .prd_name, .item_name")
            price_node = p.select_one(".price, .spec li span, .item_price")
            name_text = _safe_text(name_node)
            price_text = _safe_text(price_node)
            link = a.get("href", "")
            if link.startswith("/"):
                domain = "/".join(url.split("/")[:3])
                link = domain + link
            if name_text:
                items.append({
                    "site": name,
                    "name": name_text,
                    "price": price_text,
                    "link": link
                })
        except Exception:
            continue
    return items

def run_all_crawlers():
    data = []
    for name, url in SITES:
        try:
            data.extend(crawl_site(name, url))
        except Exception:
            continue
    return data
