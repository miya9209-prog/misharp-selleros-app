import streamlit as st

# =========================
# 초기 세션 설정
# =========================
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True  # 테스트용 (나중에 실제 로그인 로직 연결)

# =========================
# 페이지 함수들 (기존 연결 자리)
# =========================
def dashboard():
    st.title("대시보드")
    st.write("메인 대시보드 영역")

def detail_page():
    st.title("상세페이지 생성")
    st.write("상세페이지 생성기 연결")

def seo_page():
    st.title("SEO 생성")
    st.write("SEO 생성기 연결")

def blog_page():
    st.title("블로그 생성")
    st.write("블로그 생성기 연결")

def thumbnail_page():
    st.title("썸네일 생성")
    st.write("썸네일 생성기 연결")

def gif_page():
    st.title("GIF 생성")
    st.write("GIF 생성기 연결")

def shortform_page():
    st.title("숏폼 메이커")
    st.write("숏폼 메이커 연결")

def guide_page():
    st.title("기능별 사용법")
    st.write("각 기능 설명 페이지")

# =========================
# 사이드바 (핵심 수정 영역)
# =========================
with st.sidebar:

    st.markdown(
        """
        <div style="font-size:20px; font-weight:700; margin-bottom:10px;">
        MISHARP SELLER OS
        </div>
        """,
        unsafe_allow_html=True
    )

    def menu(label, key):
        if st.button(label, key=key, use_container_width=True):
            st.session_state.page = key

    menu("대시보드", "dashboard")
    menu("상세페이지 생성", "detail")
    menu("SEO 생성", "seo")
    menu("블로그 작성", "blog")
    menu("썸네일 생성", "thumbnail")
    menu("GIF 생성", "gif")
    menu("숏폼 메이커", "shortform")

    st.markdown("---")

    if st.button("기능별 사용법", use_container_width=True):
        st.session_state.page = "guide"

# =========================
# 페이지 라우팅
# =========================
page = st.session_state.page

if page == "dashboard":
    dashboard()

elif page == "detail":
    detail_page()

elif page == "seo":
    seo_page()

elif page == "blog":
    blog_page()

elif page == "thumbnail":
    thumbnail_page()

elif page == "gif":
    gif_page()

elif page == "shortform":
    shortform_page()

elif page == "guide":
    guide_page()
