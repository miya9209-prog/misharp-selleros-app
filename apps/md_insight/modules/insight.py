
import pandas as pd
import streamlit as st
from core.catalog import ALL_CATEGORIES
from core.gpt_insight import generate_insight
from utils.db import get_db_path_text, get_summary_stats


def insight_ui():
    st.subheader("MD 인사이트")
    st.caption("현재 인사이트는 프로그램이 수집해 저장한 데이터(DB)를 바탕으로 GPT가 해석합니다.")
    st.caption(f"DB 저장 위치: {get_db_path_text()}")

    if st.button("GPT 분석 실행", use_container_width=True):
        try:
            with st.spinner("분석 생성중입니다..."):
                result = generate_insight()
            if "OPENAI_API_KEY" in str(result):
                st.info(result)
            else:
                st.success("완료되었습니다.")
                st.write(result)
        except Exception as e:
            st.error(f"GPT 분석 중 오류가 발생했습니다: {e}")

    st.divider()

    stats = get_summary_stats()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("전체 저장 건수", stats["total"])
    with c2:
        st.metric("수집 소스 수", len(stats["by_source"]))
    with c3:
        st.metric("카테고리 수", len(ALL_CATEGORIES))

    cat_dict = dict(stats["by_category"])
    final_categories = [[cat, cat_dict.get(cat, 0)] for cat in ALL_CATEGORIES]
    cat_df = pd.DataFrame(final_categories, columns=["category", "count"])

    mall_df = pd.DataFrame(stats["by_mall"][:len(ALL_CATEGORIES)], columns=["mall", "count"])

    col1, col2 = st.columns(2)
    with col1:
        st.write("카테고리별 현황")
        st.dataframe(cat_df, use_container_width=True, hide_index=True)
    with col2:
        st.write("몰별 상위 현황")
        st.dataframe(mall_df, use_container_width=True, hide_index=True)
