
import html
import json
import re
from datetime import datetime
from urllib.parse import urljoin

import streamlit as st
import streamlit.components.v1 as components

try:
    import feedparser
except Exception:
    feedparser = None

try:
    import pytz
except Exception:
    pytz = None

try:
    import requests
except Exception:
    requests = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

RELATED_LINKS = [
    ("정책브리핑", "https://www.korea.kr/"),
    ("기업마당", "https://www.bizinfo.go.kr/"),
    ("중소벤처24", "https://www.smes.go.kr/"),
    ("정책지원조회", "https://mybiz.pay.naver.com/subvention/search/"),
    ("한국패션협회", "http://www.koreafashion.org/"),
    ("한국패션뉴스", "https://www.kfashionnews.com/"),
    ("패션엔", "https://www.fashionn.com/"),
    ("패션비즈", "https://fashionbiz.co.kr/"),
    ("한국섬유신문", "http://www.ktnews.com/"),
    ("소비자경제", "https://www.consumernews.co.kr/news/articleList.html?sc_multi_code=S3&view_type=sm"),
    ("통계청", "https://kostat.go.kr/"),
    ("중소벤처기업부", "https://www.mss.go.kr/"),
    ("창조경제혁신센터", "https://ccei.creativekorea.or.kr/"),
    ("DASH", "https://startup.daegu.go.kr/"),
    ("창업진흥원", "https://www.kised.or.kr/index.es?sid=a1"),
    ("스타트업지원센터", "https://www.k-startup.go.kr/onestop"),
]

FASHION_IT_SOURCES = [
    {"type": "html", "name": "한국패션뉴스", "url": "https://www.kfashionnews.com/", "keywords": ["패션", "유통", "브랜드", "트렌드", "소비", "온라인", "커머스", "마케팅"]},
    {"type": "html", "name": "패션엔", "url": "https://www.fashionn.com/board/list_new.php?table=1004", "keywords": ["패션", "브랜드", "트렌드", "유통", "마케팅"]},
    {"type": "html", "name": "패션비즈", "url": "https://fashionbiz.co.kr/", "keywords": ["패션", "브랜드", "유통", "소비", "트렌드"]},
    {"type": "html", "name": "한국섬유신문", "url": "http://www.ktnews.com/", "keywords": ["패션", "섬유", "유통", "브랜드", "트렌드"]},
    {"type": "html", "name": "소비자경제", "url": "https://www.consumernews.co.kr/news/articleList.html?sc_multi_code=S3&view_type=sm", "keywords": ["소비", "유통", "온라인", "플랫폼", "커머스", "마케팅", "트렌드"]},
    {"type": "rss", "name": "전자신문", "url": "https://www.etnews.com/rss/section/0300.xml", "category": "IT"},
    {"type": "html", "name": "블로터", "url": "https://www.bloter.net/", "keywords": ["IT", "AI", "플랫폼", "커머스", "마케팅", "디지털"]},
    {"type": "html", "name": "지디넷코리아", "url": "https://zdnet.co.kr/", "keywords": ["IT", "AI", "플랫폼", "디지털", "커머스"]},
]

ECONOMY_SOURCES = [
    {"type": "html", "name": "정책브리핑", "url": "https://www.korea.kr/news/policyNewsList.do", "keywords": ["경제", "소비", "유통", "물가", "수출", "중소기업"]},
    {"type": "html", "name": "머니투데이", "url": "https://news.mt.co.kr/", "keywords": ["경제", "금리", "증시", "물가", "환율"]},
    {"type": "html", "name": "비즈니스포스트", "url": "https://www.businesspost.co.kr/", "keywords": ["경제", "증시", "금리", "산업"]},
    {"type": "html", "name": "서울파이낸스", "url": "https://www.seoulfn.com/", "keywords": ["경제", "금융", "증시", "물가", "환율"]},
    {"type": "html", "name": "파이낸셜뉴스", "url": "https://www.fnnews.com/", "keywords": ["경제", "금융", "주식", "환율", "부동산"]},
    {"type": "rss", "name": "한겨레", "url": "https://www.hani.co.kr/rss/economy/", "category": "경제"},
    {"type": "rss", "name": "경향신문", "url": "https://www.khan.co.kr/rss/rssdata/economy_news.xml", "category": "경제"},
    {"type": "rss", "name": "매일경제", "url": "https://www.mk.co.kr/rss/30100041/", "category": "경제"},
]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def smart_date(entry):
    for attr in ["published_parsed", "updated_parsed"]:
        value = getattr(entry, attr, None)
        if value:
            try:
                return datetime(*value[:6]).strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
    for attr in ["published", "updated"]:
        value = getattr(entry, attr, None)
        if value:
            return str(value)[:16]
    return ""


def dedupe_items(items):
    seen = set()
    out = []
    for item in items:
        key = (item.get("title", "").strip(), item.get("link", "").strip())
        if not key[0] or not key[1] or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def is_valid_article_url(href: str) -> bool:
    if not href:
        return False
    href = href.strip()
    if href.startswith("javascript:") or href.startswith("#"):
        return False
    return href.startswith("http://") or href.startswith("https://") or href.startswith("/")


def looks_like_article_title(title: str) -> bool:
    title = normalize_text(title)
    if len(title) < 10:
        return False
    bad = ["로그인", "회원가입", "전체보기", "더보기", "구독", "제보", "이전", "다음", "광고문의"]
    return not any(b in title for b in bad)


@st.cache_data(ttl=1800)
def fetch_rss_items(source_name, url, category_tag=None, max_items=8):
    if feedparser is None:
        return []
    items = []
    try:
        parsed = feedparser.parse(url)
        for ent in parsed.entries[:max_items]:
            title = normalize_text(getattr(ent, "title", ""))
            link = normalize_text(getattr(ent, "link", ""))
            if title and link:
                items.append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "date": smart_date(ent),
                    "category": category_tag or "",
                })
    except Exception:
        return []
    return items


@st.cache_data(ttl=1800)
def fetch_html_list_items(source_name, url, base_url=None, category_tag=None, include_keywords=None, max_items=8):
    if requests is None or BeautifulSoup is None:
        return []
    include_keywords = include_keywords or []
    base_url = base_url or url
    found = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href]"):
            href = a.get("href", "").strip()
            title = normalize_text(a.get_text(" ", strip=True))
            if not is_valid_article_url(href) or not looks_like_article_title(title):
                continue
            full = urljoin(base_url, href)
            if include_keywords:
                low = title.lower()
                if not any(k.lower() in low for k in include_keywords):
                    continue
            found.append({
                "title": title,
                "link": full,
                "source": source_name,
                "date": "실시간 수집",
                "category": category_tag or "",
            })
            if len(found) >= max_items:
                break
    except Exception:
        return []
    return found


def collect_news(source_configs, overall_limit=50):
    items = []
    for cfg in source_configs:
        if cfg["type"] == "rss":
            items.extend(fetch_rss_items(cfg["name"], cfg["url"], cfg.get("category"), max_items=8))
        else:
            items.extend(fetch_html_list_items(cfg["name"], cfg["url"], cfg.get("base_url"), cfg.get("category"), cfg.get("keywords", []), max_items=8))
    return dedupe_items(items)[:overall_limit]


@st.cache_data(ttl=1800)
def get_fashion_news():
    return collect_news(FASHION_IT_SOURCES, overall_limit=50)


@st.cache_data(ttl=1800)
def get_economy_news():
    return collect_news(ECONOMY_SOURCES, overall_limit=50)


@st.cache_data(ttl=1800)
def get_seoul_weather():
    if requests is None:
        return {}
    weather_url = (
        "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780"
        "&current=temperature_2m,weather_code,is_day,apparent_temperature,precipitation,cloud_cover"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&timezone=Asia%2FSeoul&forecast_days=1"
    )
    air_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=37.5665&longitude=126.9780"
        "&current=pm10,pm2_5,us_aqi&timezone=Asia%2FSeoul"
    )
    weather = {}
    air = {}
    try:
        weather = requests.get(weather_url, headers=HEADERS, timeout=12).json()
    except Exception:
        pass
    try:
        air = requests.get(air_url, headers=HEADERS, timeout=12).json()
    except Exception:
        pass
    code_map = {0: "맑음", 1: "대체로 맑음", 2: "부분적으로 흐림", 3: "흐림", 45: "안개", 48: "안개", 51: "약한 이슬비", 53: "이슬비", 55: "강한 이슬비", 61: "약한 비", 63: "비", 65: "강한 비", 71: "약한 눈", 73: "눈", 75: "강한 눈", 80: "소나기", 81: "강한 소나기", 82: "매우 강한 소나기", 95: "뇌우"}
    current = weather.get("current", {}) if isinstance(weather, dict) else {}
    daily = weather.get("daily", {}) if isinstance(weather, dict) else {}
    air_current = air.get("current", {}) if isinstance(air, dict) else {}
    aqi = air_current.get("us_aqi")
    if aqi is None:
        air_text = "공기지수 정보 없음"
    elif aqi <= 50:
        air_text = f"공기지수 좋음 ({int(aqi)})"
    elif aqi <= 100:
        air_text = f"공기지수 보통 ({int(aqi)})"
    elif aqi <= 150:
        air_text = f"공기지수 민감군 주의 ({int(aqi)})"
    else:
        air_text = f"공기지수 나쁨 ({int(aqi)})"
    return {
        "temp": current.get("temperature_2m"),
        "feel": current.get("apparent_temperature"),
        "code_text": code_map.get(current.get("weather_code"), "날씨 정보 확인 중"),
        "rain_prob": (daily.get("precipitation_probability_max") or [None])[0],
        "min": (daily.get("temperature_2m_min") or [None])[0],
        "max": (daily.get("temperature_2m_max") or [None])[0],
        "air": air_text,
    }


def fmt_temp(v):
    try:
        return f"{float(v):.1f}°C"
    except Exception:
        return "-"


def build_news_digest(items, section_name):
    lines = []
    for item in items[:12]:
        if isinstance(item, dict):
            source = item.get('source', '')
            title = item.get('title', '')
        else:
            try:
                title, source = item
            except Exception:
                source = ''
                title = str(item)
        lines.append(f"- [{source}] {title}")
    return f"{section_name}\n" + "\n".join(lines)


@st.cache_data(ttl=1800, show_spinner=False)
def generate_misharp_insight_cached(fashion_items, economy_items, api_key):
    if not api_key:
        return "API 키 설정 필요"
    if OpenAI is None:
        return "openai 패키지가 설치되지 않아 AI 인사이트를 생성할 수 없습니다."
    prompt = f"""
당신은 4050 여성 타깃 여성의류 브랜드 미샵(MISHARP)의 실무형 MD이자 마케팅 전략가입니다.
아래 오늘의 뉴스 브리핑을 바탕으로, 오늘 미샵에 실제로 도움이 되는 인사이트를 한국어로 작성하세요.

반드시 아래 형식으로 작성하세요.
1. 오늘 체크할 시장 흐름 3가지
2. 미샵에 바로 적용할 상품/콘텐츠/광고 아이디어 3가지
3. 오늘의 한줄 실행 제안

조건:
- 추상적인 말 말고 실무형으로 작성
- 4050 여성 패션몰 관점 반영
- 온라인 쇼핑몰, 콘텐츠, 광고, 재고, 가격, 프로모션 관점 포함
- 각 항목은 짧고 명확하게 작성

[패션·IT·유통·온라인마케팅 뉴스]
{build_news_digest(fashion_items, '패션/IT/유통/온라인마케팅 뉴스')}

[경제 뉴스]
{build_news_digest(economy_items, '경제 뉴스')}
"""
    try:
        client = OpenAI(api_key=api_key)
        res = client.responses.create(model="gpt-4.1-mini", input=prompt)
        return (res.output_text or "인사이트 생성 결과가 비어 있습니다.").strip()
    except Exception as e:
        return f"AI 인사이트 생성 중 오류가 발생했습니다: {e}"


def clean_multiline_text(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def text_to_html_blocks(text: str) -> str:
    cleaned = clean_multiline_text(text)
    if not cleaned:
        return ""
    paragraphs = []
    for block in cleaned.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        lines = [html.escape(line.strip()) for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        paragraphs.append(f'<div class="news-post-formatted-block">{"<br>".join(lines)}</div>')
    return "".join(paragraphs)


def render_copy_button(text: str, key: str):
    safe_text = json.dumps(clean_multiline_text(text), ensure_ascii=False)
    button_id = f"copy_btn_{key}"
    msg_id = f"{button_id}_msg"
    html_block = """
    <div style="margin-top:10px; margin-bottom:2px;">
      <button id="__BUTTON_ID__" style="border-radius:12px;font-weight:700;padding:9px 14px;cursor:pointer;">내용 전체 복사</button>
      <span id="__MSG_ID__" style="margin-left:8px;font-size:13px;"></span>
    </div>
    <script>
    const btn = document.getElementById(__BUTTON_ID_JSON__);
    const msg = document.getElementById(__MSG_ID_JSON__);
    btn.onclick = async () => {
      try {
        await navigator.clipboard.writeText(__SAFE_TEXT__);
        msg.textContent = '복사되었습니다.';
        setTimeout(() => msg.textContent = '', 2200);
      } catch (e) {
        msg.textContent = '복사에 실패했습니다.';
      }
    };
    </script>
    """
    html_block = (
        html_block.replace("__BUTTON_ID__", button_id)
        .replace("__MSG_ID__", msg_id)
        .replace("__BUTTON_ID_JSON__", json.dumps(button_id))
        .replace("__MSG_ID_JSON__", json.dumps(msg_id))
        .replace("__SAFE_TEXT__", safe_text)
    )
    components.html(html_block, height=46)


def render_news_section(items, title, state_prefix):
    limit_key = f"news_post_{state_prefix}_limit"
    if limit_key not in st.session_state:
        st.session_state[limit_key] = 10
    visible = items[: st.session_state[limit_key]]
    st.markdown(f"**{html.escape(title)}**")
    if visible:
        for item in visible:
            date_text = item.get("date") or "실시간 수집"
            st.markdown(
                f"""
                <a class="news-post-item" href="{html.escape(item['link'])}" target="_blank">
                    <div class="news-post-item-title">{html.escape(item['title'])}</div>
                    <div class="news-post-item-meta"><span>{html.escape(item['source'])}</span><span>{html.escape(date_text)}</span></div>
                </a>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("뉴스를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    b1, b2 = st.columns(2)
    with b1:
        if st.session_state[limit_key] < min(50, len(items)):
            if st.button("기사 더보기", key=f"news_post_{state_prefix}_more", use_container_width=True):
                st.session_state[limit_key] = min(50, st.session_state[limit_key] + 10)
                st.rerun()
    with b2:
        if st.session_state[limit_key] > 10:
            if st.button("접기", key=f"news_post_{state_prefix}_collapse", use_container_width=True):
                st.session_state[limit_key] = 10
                st.rerun()


def render_related_links():
    st.markdown("**관련 정보 사이트**")
    cols = st.columns(4)
    for idx, (name, url) in enumerate(RELATED_LINKS):
        cols[idx % 4].link_button(name, url, use_container_width=True)


def render_guide():
    show_key = "news_post_show_guide"
    show = st.session_state.get(show_key, False)
    guide_btn_label = "안내 접기" if show else "안내 내용 펼치기"
    if st.button(guide_btn_label, key="news_post_show_guide_btn"):
        st.session_state[show_key] = not show
        st.rerun()
    if st.session_state.get(show_key, False):
        guide_body = """1. 이 페이지에서 확인하는 정보
서울 기준 실시간 시간과 날씨, 공기지수, 패션·유통·IT·온라인마케팅 뉴스, 주요 경제뉴스, 관련 기관·전문매체 링크, 그리고 기사 흐름을 바탕으로 정리하는 버튼형 인사이트까지 한 번에 볼 수 있습니다.

2. 누가 활용하면 좋은가
패션 브랜드 운영자, 온라인 쇼핑몰 대표, 유통 실무자, 마케터, 콘텐츠 기획자, 창업 준비자, 정책지원사업을 찾는 소상공인과 스타트업 실무자에게 특히 유용합니다.

3. 인사이트 활용법
아침 회의 전 체크리스트, 콘텐츠 주제 발굴, 광고 문구 정리, 상품기획 방향 점검용으로 활용할 수 있습니다.

4. 참고 안내
기사와 관련 사이트는 외부 페이지로 연결되며, 인사이트 내용은 참고용 자료입니다."""
        st.markdown(text_to_html_blocks(guide_body), unsafe_allow_html=True)


def _get_secret(name: str) -> str:
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


def render():
    try:
        st.markdown(
            """
            <style>
            .news-post-card{border:1px solid rgba(255,255,255,.10); border-radius:16px; padding:14px 16px; background:rgba(255,255,255,.03);}
            .news-post-item{display:block; text-decoration:none; padding:12px 14px; border:1px solid rgba(255,255,255,.10); border-radius:14px; margin-bottom:10px; color:inherit !important; background:rgba(255,255,255,.02);}
            .news-post-item-title{font-weight:700; line-height:1.45; color:inherit;}
            .news-post-item-meta{display:flex; justify-content:space-between; gap:10px; margin-top:6px; font-size:.82rem; opacity:.75;}
            .news-post-formatted-block{line-height:1.82; margin:0 0 14px 0;}
            </style>
            """,
            unsafe_allow_html=True,
        )

        tz = pytz.timezone("Asia/Seoul") if pytz else None
        now = datetime.now(tz) if tz else datetime.now()
        weather = get_seoul_weather()
        fashion_news = get_fashion_news()
        economy_news = get_economy_news()

        top1, top2 = st.columns(2)
        with top1:
            st.markdown(
                f"<div class='news-post-card'><strong>한국시간 · 서울</strong><br>{now.strftime('%Y-%m-%d (%a) %H:%M:%S')}<br>현재 {fmt_temp(weather.get('temp'))} / 체감 {fmt_temp(weather.get('feel'))} / {weather.get('code_text', '날씨 정보 확인 중')}</div>",
                unsafe_allow_html=True,
            )
        with top2:
            rain = weather.get("rain_prob")
            rain_text = f"강수확률 {int(rain)}%" if rain is not None else "강수확률 정보 없음"
            st.markdown(
                f"<div class='news-post-card'><strong>서울 실시간 날씨</strong><br>최저 {fmt_temp(weather.get('min'))} / 최고 {fmt_temp(weather.get('max'))}<br>{rain_text} · {weather.get('air', '공기지수 정보 없음')}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("### 미샵을 위한 오늘의 인사이트")
        st.caption("오늘 수집된 패션·소비유통·IT·경제 뉴스를 바탕으로 상품기획·콘텐츠·광고 실행 아이디어를 정리합니다.")

        insight_key = "news_post_misharp_insight_text"
        api_key = _get_secret("OPENAI_API_KEY")
        if not api_key:
            st.info("API 키 설정 필요")
        if st.button("오늘의 인사이트 생성", key="news_post_generate_misharp_insight", use_container_width=False):
            if not api_key:
                st.session_state[insight_key] = "API 키 설정 필요"
            else:
                with st.spinner("기사 흐름을 분석해 미샵 인사이트를 생성하는 중입니다..."):
                    st.session_state[insight_key] = generate_misharp_insight_cached(tuple((i['title'], i['source']) for i in fashion_news), tuple((i['title'], i['source']) for i in economy_news), api_key)
        if st.session_state.get(insight_key):
            insight_text = st.session_state[insight_key]
            render_copy_button(insight_text, "news_post_misharp_insight")
            st.markdown(f"<div class='news-post-card'>{text_to_html_blocks(insight_text)}</div>", unsafe_allow_html=True)

        left_col, right_col = st.columns(2)
        with left_col:
            render_news_section(fashion_news, "오늘의 패션, 온라인마케팅, 유통, IT 뉴스", "fashion_news")
        with right_col:
            render_news_section(economy_news, "오늘 주요 경제뉴스", "economy_news")

        st.markdown("---")
        render_related_links()
        st.markdown("---")
        render_guide()
    except Exception as e:
        st.error(f"앱 실행 중 오류: {e}")


def main():
    render()


def app():
    render()
