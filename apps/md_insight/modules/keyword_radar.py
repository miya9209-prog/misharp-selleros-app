
import time
import pandas as pd
import streamlit as st
from core.keyword_service import build_keyword_rankings, analyze_single_keyword, category_keyword_suggestions
from core.naver_api import get_naver_api_error_message
from utils.db import insert_keyword_cache, get_recent_keywords, log_event

SOURCE_NAME = "naver_datalab"


def _fallback_rankings(period_key):
    """네이버 API 호출이 실패하거나 캐시가 비어 있을 때 화면 공백을 막는 기본 트렌드 데이터."""
    base = [
        ("하객룩", 38.2857), ("여성 셔츠", 18.8571), ("여성 티셔츠", 14.2857),
        ("여성 자켓", 11.5714), ("여성 가방", 11.1429), ("여성 니트", 9.1429),
        ("여성 원피스", 8.0000), ("여성 팬츠", 8.0000), ("여성 블라우스", 8.0000),
        ("여성 가디건", 7.0000), ("출근룩", 6.4000), ("체형커버", 5.9000),
    ]
    if period_key == "weekly":
        base = [
            ("하객룩", 36.3214), ("여성 자켓", 15.7143), ("여성 셔츠", 10.7857),
            ("여성 티셔츠", 10.5714), ("여성 원피스", 9.6786), ("여성 가방", 9.3929),
            ("여성 니트", 6.7857), ("여성 가디건", 6.0714), ("여성 팬츠", 6.0357),
            ("여성 블라우스", 5.8571), ("출근룩", 5.2000), ("체형커버", 4.9000),
        ]
    elif period_key == "monthly":
        base = [
            ("하객룩", 21.9560), ("여성 자켓", 19.2198), ("여성 니트", 10.2088),
            ("여성 가방", 9.2747), ("여성 티셔츠", 6.3736), ("여성 원피스", 6.1978),
            ("여성 팬츠", 5.3407), ("여성 셔츠", 4.2747), ("여성 가디건", 3.9780),
            ("여성 블라우스", 1.8022), ("출근룩", 1.7000), ("체형커버", 1.5000),
        ]
    return base


def _ensure_fallback_cache():
    existing = get_recent_keywords(limit=1, source=SOURCE_NAME, period="daily")
    if existing:
        return False
    rows = []
    for period in ("daily", "weekly", "monthly"):
        rows.extend(_cache_rows(period, _fallback_rankings(period)))
    if rows:
        insert_keyword_cache(rows)
        log_event(SOURCE_NAME, "fallback", "네이버 데이터 수집 실패 또는 초기 캐시 없음: 기본 트렌드 데이터 표시")
        return True
    return False


def _show_rank_table(rows):
    if not rows:
        st.info("아직 데이터가 없습니다. '트렌드 새로고침'을 눌러주세요.")
        return
    df = pd.DataFrame(rows, columns=["id", "source", "period", "keyword", "score", "collected_at"])
    df = df[["keyword", "score"]].sort_values("score", ascending=False)
    df.columns = ["키워드", "클릭 지수"]
    st.dataframe(df, use_container_width=True, hide_index=True)


def _cache_rows(period_key, rankings):
    return [(SOURCE_NAME, period_key, kw, float(score)) for kw, score in rankings[:30]]


def keyword_ui():
    st.subheader("키워드 RADAR")

    api_error = get_naver_api_error_message()
    if api_error:
        st.warning(api_error)

    if "last_trend_refresh" not in st.session_state:
        st.session_state["last_trend_refresh"] = 0

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("#### 오늘/주간/월간 트렌드 요약")
    with c2:
        cooldown_sec = 30
        remain = cooldown_sec - (time.time() - st.session_state["last_trend_refresh"])
        refresh_disabled = remain > 0
        if refresh_disabled:
            st.caption(f"새로고침 가능까지 {int(remain)}초")
        if st.button("트렌드 새로고침", use_container_width=True, disabled=refresh_disabled):
            st.session_state["last_trend_refresh"] = time.time()
            if api_error:
                _ensure_fallback_cache()
                st.warning("네이버 API 설정 필요 → 기본 트렌드 데이터로 표시합니다.")
            else:
                try:
                    with st.spinner("네이버 데이터 수집중입니다..."):
                        daily, failed_daily = build_keyword_rankings("daily")
                        weekly, failed_weekly = build_keyword_rankings("weekly")
                        monthly, failed_monthly = build_keyword_rankings("monthly")
                        rows = _cache_rows("daily", daily) + _cache_rows("weekly", weekly) + _cache_rows("monthly", monthly)
                        if rows:
                            insert_keyword_cache(rows)
                        failed = failed_daily + failed_weekly + failed_monthly
                        if failed:
                            log_event(SOURCE_NAME, "warning", f"일부 실패 {len(failed)}건")
                            st.warning("네이버 데이터 수집 실패 → 기존 데이터 표시중")
                        else:
                            log_event(SOURCE_NAME, "success", f"{len(rows)}건 저장")
                            st.success("트렌드 갱신 완료")
                except Exception as e:
                    log_event(SOURCE_NAME, "error", str(e))
                    made = _ensure_fallback_cache()
                    if made:
                        st.warning("네이버 데이터 수집 실패 → 기본 트렌드 데이터로 표시합니다.")
                    else:
                        st.warning("네이버 데이터 수집 실패 → 기존 데이터 표시중")

    _ensure_fallback_cache()
    daily = get_recent_keywords(limit=20, source=SOURCE_NAME, period="daily")
    weekly = get_recent_keywords(limit=20, source=SOURCE_NAME, period="weekly")
    monthly = get_recent_keywords(limit=20, source=SOURCE_NAME, period="monthly")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**일간 상위 키워드**")
        _show_rank_table(daily)
    with col2:
        st.markdown("**주간 상위 키워드**")
        _show_rank_table(weekly)
    with col3:
        st.markdown("**월간 상위 키워드**")
        _show_rank_table(monthly)

    st.divider()
    st.markdown("#### 카테고리별 추천 키워드")
    st.dataframe(pd.DataFrame(category_keyword_suggestions()), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 직접 검색")
    keyword = st.text_input("키워드 입력", placeholder="예: 40대 여성 가디건", key="keyword_radar_input")

    if st.button("키워드 분석", use_container_width=True):
        if not keyword.strip():
            st.warning("키워드를 입력해 주세요.")
            return
        if api_error:
            st.warning("네이버 API 설정 필요")
            return
        try:
            with st.spinner("키워드 분석중입니다..."):
                result = analyze_single_keyword(keyword.strip())
            daily_rows = result.get("daily", [])
            if not daily_rows:
                st.info("표시할 네이버 데이터가 없습니다.")
                return
            df = pd.DataFrame(daily_rows)
            if not df.empty:
                st.line_chart(df.set_index("period")[["ratio"]])
                show = df.rename(columns={"period": "기간", "ratio": "클릭 지수"})
                st.dataframe(show, use_container_width=True, hide_index=True)
        except Exception as e:
            log_event(SOURCE_NAME, "error", str(e))
            st.warning("네이버 데이터 수집 실패 → 기존 데이터 표시중")
