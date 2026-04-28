
import time
import pandas as pd
import streamlit as st
from core.keyword_service import build_keyword_rankings, analyze_single_keyword, category_keyword_suggestions
from core.naver_api import get_naver_api_error_message
from utils.db import insert_keyword_cache, get_recent_keywords, log_event

SOURCE_NAME = "naver_datalab"


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
                st.warning("네이버 API 설정 필요")
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
                    st.warning("네이버 데이터 수집 실패 → 기존 데이터 표시중")

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
