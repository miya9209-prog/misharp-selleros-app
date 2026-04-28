
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from utils.db import init_db
from modules.keyword_radar import keyword_ui
from modules.product_radar import product_ui
from modules.competitor_radar import competitor_ui
from modules.insight import insight_ui
from modules.planner import planner_ui

st.set_page_config(page_title="MD 인사이트", layout="wide")
init_db()

st.markdown("""
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 2rem;}
button[data-baseweb="tab"] {
    font-size: 20px !important;
    font-weight: 700 !important;
    padding: 14px 28px !important;
    margin-right: 14px !important;
}
div[data-baseweb="tab-list"] {gap: 0.35rem !important;}
</style>
""", unsafe_allow_html=True)

st.markdown("# MD 인사이트")
st.caption("패션 키워드 트렌드, 인기 상품 검색, 경쟁사 탐색, MD 분석과 상품기획을 지원합니다.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["키워드 RADAR", "상품 RADAR", "경쟁사 RADAR", "MD 인사이트", "매출형 상품기획"]
)

with tab1:
    keyword_ui()
with tab2:
    product_ui()
with tab3:
    competitor_ui()
with tab4:
    insight_ui()
with tab5:
    planner_ui()
