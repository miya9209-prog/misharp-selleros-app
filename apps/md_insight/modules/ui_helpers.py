import streamlit as st

def render_clickable_table(df):
    config = {}
    if "링크" in df.columns:
        config["링크"] = st.column_config.LinkColumn("바로가기", help="클릭하면 상품 페이지로 이동합니다.", display_text="열기")
    if "이미지" in df.columns:
        config["이미지"] = st.column_config.ImageColumn("썸네일", help="상품 썸네일")
    st.data_editor(df, use_container_width=True, hide_index=True, disabled=True, column_config=config)
