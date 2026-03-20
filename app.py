
import streamlit as st

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

def go(p):
    st.session_state.page = p

with st.sidebar:
    st.markdown("""<div style='font-size:24px;font-weight:800;'>MISHARP<br>SELLER OS</div>""", unsafe_allow_html=True)

    if st.button("대시보드"):
        go("dashboard")

    if st.button("페이지빌더"):
        go("page_builder")

    if st.button("CRM OS"):
        go("crm")

    if st.button("샘플반품관리"):
        go("return")

def dashboard():
    st.title("대시보드")

def page_builder():
    st.title("페이지빌더 연결 완료")

def crm():
    st.title("CRM OS 연결 완료")

def returns():
    st.title("샘플 반품 관리")

if st.session_state.page == "dashboard":
    dashboard()
elif st.session_state.page == "page_builder":
    page_builder()
elif st.session_state.page == "crm":
    crm()
elif st.session_state.page == "return":
    returns()
