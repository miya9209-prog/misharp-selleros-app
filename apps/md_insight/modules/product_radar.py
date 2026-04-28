
import pandas as pd
import streamlit as st
from core.product_service import collect_products_by_keyword, discover_hot_categories
from core.naver_api import get_naver_api_error_message
from modules.ui_helpers import render_clickable_table
from utils.db import insert_products, get_recent_products, log_event


def product_ui():
    st.subheader("상품 RADAR")
    api_error = get_naver_api_error_message()
    if api_error:
        st.warning(api_error)

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("#### 핫 카테고리")
    with c2:
        if st.button("카테고리 재탐색", use_container_width=True):
            st.session_state["refresh_hot_categories"] = True

    if st.session_state.get("refresh_hot_categories", True) and not api_error:
        try:
            ranking, sample_map = discover_hot_categories(pages=1)
            st.session_state["hot_category_ranking"] = ranking
            st.session_state["hot_category_samples"] = sample_map
            st.session_state["refresh_hot_categories"] = False
        except Exception as e:
            log_event("naver", "error", str(e))
            st.warning("카테고리 탐색에 실패했습니다. 기존 데이터를 확인해 주세요.")

    ranking = st.session_state.get("hot_category_ranking", [])
    sample_map = st.session_state.get("hot_category_samples", {})

    if ranking:
        rank_df = pd.DataFrame(ranking)
        st.dataframe(rank_df, use_container_width=True, hide_index=True)
        category_options = rank_df["카테고리"].tolist()
        selected_category = st.selectbox("카테고리 선택", category_options, key="product_hot_category")
        st.caption("카테고리 탐색 샘플")
        render_clickable_table(pd.DataFrame(sample_map.get(selected_category, [])))

    st.divider()
    st.markdown("#### 직접 검색")
    c1, c2, c3 = st.columns([4, 1, 1])
    with c1:
        keyword = st.text_input("상품 키워드", placeholder="예: 40대 여성 티셔츠")
    with c2:
        sort = st.selectbox("정렬", ["sim", "date", "asc", "dsc"], index=0)
    with c3:
        pages = st.selectbox("수집량", [1, 2, 3], index=1)
    if st.button("네이버 검색", use_container_width=True):
        if not keyword.strip():
            st.warning("상품 키워드를 입력해 주세요.")
            return
        if api_error:
            st.warning("네이버 API 설정 필요")
            return
        try:
            with st.spinner("상품 검색중입니다..."):
                rows, cards = collect_products_by_keyword(keyword.strip(), pages=pages, sort=sort)
                saved = insert_products(rows)
                log_event("naver", "success", f"{keyword.strip()} / {saved}건 저장")
            st.success(f"{saved}건 저장했습니다.")
            render_clickable_table(pd.DataFrame(cards))
        except Exception as e:
            log_event("naver", "error", str(e))
            st.error(f"상품 검색 중 오류가 발생했습니다: {e}")

    st.divider()
    st.caption("최근 저장 데이터")
    rows = get_recent_products(limit=50, source="naver")
    if rows:
        df = pd.DataFrame(rows, columns=["id","source","keyword","category","name","price","mall","link","image_url","collected_at"])
        show = df.rename(columns={"image_url":"이미지","name":"상품명","category":"카테고리","price":"가격","mall":"몰","keyword":"키워드","link":"링크","collected_at":"수집일시"})
        show = show[["이미지","상품명","카테고리","가격","몰","키워드","링크","수집일시"]]
        render_clickable_table(show)
