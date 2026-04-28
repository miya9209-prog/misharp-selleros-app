
import streamlit as st
from core.gpt_insight import generate_sales_planner


def planner_ui():
    st.subheader("매출형 상품기획 자동 생성")
    st.caption("입력한 주제로 상품기획서, 상세페이지 구조, 광고카피, 숏폼 후킹 문구를 자동 생성합니다.")
    keyword = st.text_input("기획 키워드", placeholder="예: 40대 여성 가디건 / 출근룩 블라우스 / 체형커버 팬츠")
    if st.button("상품기획 생성", use_container_width=True):
        if not keyword.strip():
            st.warning("기획 키워드를 입력해 주세요.")
            return
        try:
            with st.spinner("상품기획 생성중입니다..."):
                result = generate_sales_planner(keyword.strip())
            if "OPENAI_API_KEY" in str(result):
                st.info(result)
            else:
                st.success("상품기획 생성 완료")
                st.write(result)
        except Exception as e:
            st.error(f"상품기획 생성 중 오류가 발생했습니다: {e}")
