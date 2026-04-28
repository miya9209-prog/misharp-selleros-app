
from datetime import date, timedelta
from core.catalog import TREND_SEED_KEYWORDS, CATEGORY_KEYWORDS
from core.naver_api import request_datalab


def _chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]


def _score_from_result(item):
    rows = item.get("data", []) or []
    if not rows:
        return 0.0
    return float(rows[-1].get("ratio", 0) or 0)


def build_keyword_rankings(period_label="daily"):
    if period_label == "daily":
        time_unit = "date"
        start_date = date.today() - timedelta(days=30)
    elif period_label == "weekly":
        time_unit = "week"
        start_date = date.today() - timedelta(days=120)
    else:
        time_unit = "month"
        start_date = date.today() - timedelta(days=365)

    end_date = date.today()
    scores = {}
    failed_chunks = []

    for chunk in _chunks(TREND_SEED_KEYWORDS[:], 5):
        groups = [{"groupName": kw, "keywords": [kw]} for kw in chunk]
        try:
            data = request_datalab(groups, time_unit=time_unit, start_date=start_date, end_date=end_date)
            for item in data.get("results", []):
                title = item.get("title")
                if not title:
                    continue
                scores[title] = _score_from_result(item)
        except Exception as e:
            failed_chunks.append((chunk, str(e)))
            continue

    return sorted(scores.items(), key=lambda x: x[1], reverse=True), failed_chunks


def analyze_single_keyword(keyword):
    kw = (keyword or "").strip()
    if not kw:
        return {"daily": [], "weekly": [], "monthly": []}

    def _fetch(label, unit, days):
        data = request_datalab(
            [{"groupName": kw, "keywords": [kw]}],
            time_unit=unit,
            start_date=date.today() - timedelta(days=days),
            end_date=date.today(),
        )
        results = data.get("results", [])
        if not results:
            return []
        return results[0].get("data", [])

    return {
        "daily": _fetch("daily", "date", 30),
        "weekly": _fetch("weekly", "week", 120),
        "monthly": _fetch("monthly", "month", 365),
    }


def category_keyword_suggestions():
    result = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        result.append({"카테고리": category, "추천 키워드": ", ".join(keywords[:3])})
    return result
