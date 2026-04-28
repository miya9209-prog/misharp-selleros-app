
from core.catalog import CATEGORY_KEYWORDS
from core.naver_api import search_many
from core.transforms import clean_html, guess_category


def collect_products_by_keyword(keyword, pages=2, sort="sim"):
    items = search_many(keyword, pages=pages, display=50, sort=sort)
    rows, cards = [], []
    for item in items:
        name = clean_html(item.get("title", ""))
        price = item.get("lprice", "")
        mall = item.get("mallName", "")
        link = item.get("link", "")
        image_url = item.get("image", "")
        category = guess_category(name, keyword)
        rows.append(("naver", keyword, category, name, price, mall, link, image_url))
        cards.append({"이미지": image_url, "상품명": name, "카테고리": category, "가격": price, "몰": mall, "링크": link})
    return rows, cards


def discover_hot_categories(pages=1):
    ranking, sample_map = [], {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        keyword = keywords[0]
        try:
            items = search_many(keyword, pages=pages, display=30, sort="sim")
        except Exception:
            items = []
        unique_malls = len(set([i.get("mallName", "") for i in items if i.get("mallName", "")]))
        score = (len(items) * 5) + (unique_malls * 10)
        ranking.append({"카테고리": category, "검색지수": score, "대표키워드": keyword})
        sample_map[category] = [{
            "이미지": item.get("image", ""),
            "상품명": clean_html(item.get("title", "")),
            "가격": item.get("lprice", ""),
            "몰": item.get("mallName", ""),
            "링크": item.get("link", ""),
            "카테고리": category,
        } for item in items[:20]]
    ranking = sorted(ranking, key=lambda x: float(x["검색지수"]), reverse=True)
    return ranking, sample_map
