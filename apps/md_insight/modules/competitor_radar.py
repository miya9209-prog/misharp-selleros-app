
import pandas as pd
import streamlit as st
from core.competitor_sources import COMPETITOR_ALIASES, DEFAULT_KEYWORDS
from core.competitor_service import collect_by_keyword, collect_all_mode
from core.naver_api import get_naver_api_error_message
from modules.ui_helpers import render_clickable_table
from utils.db import insert_products, get_recent_products, log_event


def competitor_ui():
    st.subheader("경쟁사 RADAR")
    st.caption("네이버쇼핑 결과를 활용해 경쟁사 상품을 수집합니다. 키워드 방식과 전체 탐색 방식을 함께 제공합니다.")
    api_error = get_naver_api_error_message()
    if api_error:
        st.warning(api_error)

    mode = st.radio("수집 방식", ["추적 키워드 방식", "전체 상품 탐색 방식"], horizontal=True)
    selected = st.multiselect(
        "추적할 경쟁사 몰",
        list(COMPETITOR_ALIASES.keys()),
        default=["조아맘","캔마트","퍼플리아","그레이시크","스토리나인","안나앤모드","안나키즈","코코블랙","마리앙플러스","마이더스비","저스트원"],
    )
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        keyword = st.text_input("경쟁사 추적 키워드", placeholder="예: 여성 가디건 / 티셔츠 / 블라우스")
    with c2:
        sort = st.selectbox("정렬 방식", ["sim", "date", "asc", "dsc"], key="comp_sort")
    with c3:
        pages = st.selectbox("검색 페이지 수", [1,2,3], index=1, key="comp_pages")
    quick = st.selectbox("빠른 키워드", ["직접 입력"] + DEFAULT_KEYWORDS)
    if quick != "직접 입력" and not keyword:
        keyword = quick

    if st.button("경쟁사 수집 실행", use_container_width=True):
        if not selected:
            st.warning("경쟁사 몰을 최소 1개 이상 선택해 주세요.")
            return
        if api_error:
            st.warning("네이버 API 설정 필요")
            return
        try:
            with st.spinner("경쟁사 데이터 수집중입니다..."):
                if mode == "전체 상품 탐색 방식":
                    rows, cards = collect_all_mode(selected_malls=selected, pages=pages, sort=sort)
                else:
                    if not keyword.strip():
                        st.warning("키워드를 입력해 주세요.")
                        return
                    rows, cards = collect_by_keyword(keyword.strip(), selected_malls=selected, pages=pages, sort=sort)
                saved = insert_products(rows)
                log_event("competitor_naver", "success", f"{mode} / {saved}건 저장")
            if saved:
                st.success(f"{saved}건 저장했습니다.")
                render_clickable_table(pd.DataFrame(cards))
            else:
                st.info("선택 조건에서 경쟁사 결과를 찾지 못했습니다.")
        except Exception as e:
            log_event("competitor_naver", "error", str(e))
            st.error(f"경쟁사 수집 중 오류가 발생했습니다: {e}")

    st.divider()
    st.caption("최근 저장 데이터")
    rows = get_recent_products(limit=100, source="competitor_naver")
    if rows:
        df = pd.DataFrame(rows, columns=["id","source","keyword","category","name","price","mall","link","image_url","collected_at"])
        show = df.rename(columns={"image_url":"이미지","mall":"몰","name":"상품명","category":"카테고리","price":"가격","keyword":"키워드","link":"링크","collected_at":"수집일시"})
        show = show[["이미지","몰","상품명","카테고리","가격","키워드","링크","수집일시"]]
        render_clickable_table(show)
