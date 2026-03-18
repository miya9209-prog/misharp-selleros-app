# --- MISHARP SELLER OS (FINAL FIXED VERSION) ---

import streamlit as st
from datetime import datetime
import pytz

# ---------- 기본 설정 ----------
st.set_page_config(page_title="MISHARP SELLER OS", layout="wide")

# ---------- 세션 초기화 ----------
if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

# ---------- 사이드바 ----------
with st.sidebar:

    # ✅ 좌측 상단 타이틀 (완전 복원 + 크기 조정)
    st.markdown("""
    <div style="
        font-size: 28px;
        font-weight: 800;
        line-height: 1.05;
        color: #f5f1e8;
        letter-spacing: -0.02em;
        margin: 8px 0 18px 4px;
    ">
        MISHARP<br>SELLER OS
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 메뉴 버튼
    if st.button("대시보드"):
        st.session_state["page"] = "dashboard"

    if st.button("상세페이지 생성"):
        st.session_state["page"] = "detail"

    if st.button("썸네일 생성"):
        st.session_state["page"] = "thumb"

# ---------- 페이지 함수 ----------
def show_dashboard():
    korea = pytz.timezone("Asia/Seoul")
    now = datetime.now(korea)

    st.title("대시보드")
    st.write(now.strftime("%Y-%m-%d %H:%M"))

def show_detail():
    st.title("상세페이지 생성")

def show_thumb():
    st.title("썸네일 생성")

# ---------- 라우팅 ----------
if st.session_state["page"] == "dashboard":
    show_dashboard()

elif st.session_state["page"] == "detail":
    show_detail()

elif st.session_state["page"] == "thumb":
    show_thumb()
