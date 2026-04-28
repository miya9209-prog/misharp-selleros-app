from core.naver_api import search_many
from core.transforms import clean_html, guess_category
from core.competitor_sources import COMPETITOR_ALIASES, DEFAULT_KEYWORDS

def _query_for_alias(alias, mall_label, keyword, pages=2, sort="sim"):
    query = f"{alias} {keyword}"
    items = search_many(query, pages=pages, display=50, sort=sort)
    rows, cards, seen = [], [], set()
    for item in items:
        name = clean_html(item.get("title", ""))
        price = item.get("lprice", "")
        link = item.get("link", "")
        image_url = item.get("image", "")
        category = guess_category(name, keyword)
        dedupe = (mall_label, name, price, link)
        if dedupe in seen:
            continue
        seen.add(dedupe)
        rows.append(("competitor_naver", keyword, category, name, price, mall_label, link, image_url))
        cards.append({"이미지": image_url, "몰": mall_label, "상품명": name, "카테고리": category, "가격": price, "키워드": keyword, "링크": link})
    return rows, cards

def collect_by_keyword(keyword, selected_malls, pages=2, sort="sim"):
    merged_rows, merged_cards, seen = [], [], set()
    for mall in selected_malls:
        aliases = COMPETITOR_ALIASES.get(mall, [mall])
        for alias in aliases:
            rows, cards = _query_for_alias(alias=alias, mall_label=mall, keyword=keyword, pages=pages, sort=sort)
            for row, card in zip(rows, cards):
                dedupe = (row[5], row[3], row[4], row[6])
                if dedupe in seen:
                    continue
                seen.add(dedupe)
                merged_rows.append(row)
                merged_cards.append(card)
    return merged_rows, merged_cards

def collect_all_mode(selected_malls, pages=1, sort="sim"):
    merged_rows, merged_cards, seen = [], [], set()
    for keyword in DEFAULT_KEYWORDS:
        rows, cards = collect_by_keyword(keyword=keyword, selected_malls=selected_malls, pages=pages, sort=sort)
        for row, card in zip(rows, cards):
            dedupe = (row[5], row[3], row[4], row[6])
            if dedupe in seen:
                continue
            seen.add(dedupe)
            merged_rows.append(row)
            merged_cards.append(card)
    return merged_rows, merged_cards
