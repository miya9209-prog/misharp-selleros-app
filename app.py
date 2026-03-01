
import streamlit as st

from modules import detail_page, thumbnail, gif_maker, blog

APP_TITLE = "미샵 셀러 스튜디오 OS v1"
APP_SUBTITLE = "온라인 셀러를 위한 원스톱 상세페이지 콘텐츠 자동 생성"

MENU = [
    ("대시보드", "dashboard"),
    ("상세페이지 생성", "detail"),
    ("원고 생성", "copy"),
    ("썸네일 생성", "thumb"),
    ("GIF 생성", "gif"),
    ("이미지 수집툴", "collector"),
    ("블로그 작성", "blog"),
    ("숏폼 메이커", "shortform"),
]

def _init_state():
    st.session_state.setdefault("selleros_inputs", {
        "상품명": "",
        "가격": "",
        "소재": "",
        "핏": "",
        "사이즈": "",
        "컬러": "",
        "키워드": "",
        "금칙어": "",
        "상품URL": "",
        "특장점5줄": ["", "", "", "", ""],
    })

def inject_css():
    st.markdown(
        """
<style>
/* ---- base ---- */
html, body { background: #0b1220; }
div[data-testid="stAppViewContainer"] { background: radial-gradient(1200px 600px at 20% 0%, rgba(33,82,163,0.18), transparent 55%),
                                      radial-gradient(1000px 700px at 80% 10%, rgba(202,57,57,0.12), transparent 55%),
                                      linear-gradient(180deg, #07101e 0%, #0b1220 60%, #07101e 100%); }
.main { padding-top: 14px; padding-bottom: 70px; }

/* hide default streamlit footer & menu */
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* ---- header card ---- */
.misharp-hero {
  background: rgba(255,255,255,0.94);
  border-radius: 18px;
  padding: 28px 28px;
  box-shadow: 0 14px 40px rgba(0,0,0,0.35);
  border: 1px solid rgba(255,255,255,0.16);
}
.misharp-hero h1 {
  margin: 0;
  font-size: 40px;
  font-weight: 800;
  letter-spacing: -1px;
  color: #111827;
}
.misharp-hero p {
  margin: 10px 0 0 0;
  font-size: 14px;
  color: rgba(17,24,39,0.65);
}

/* ---- sidebar ---- */
section[data-testid="stSidebar"] { background: rgba(0,0,0,0.42); border-right: 1px solid rgba(255,255,255,0.08); }
section[data-testid="stSidebar"] .stRadio label { color: rgba(255,255,255,0.88); }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
  padding: 8px 10px;
  border-radius: 12px;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
  background: rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] { margin: 2px 0; }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: rgba(255,255,255,0.92); }

/* ---- cards ---- */
.misharp-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 16px;
  padding: 18px 18px;
  box-shadow: 0 10px 26px rgba(0,0,0,0.25);
}
.misharp-muted { color: rgba(255,255,255,0.72); }
.misharp-h { color: rgba(255,255,255,0.92); font-weight: 800; margin: 0 0 10px 0; }

/* ---- footer ---- */
.misharp-footer {
  position: fixed;
  left: 0; bottom: 0;
  width: 100%;
  padding: 10px 16px;
  background: rgba(0,0,0,0.55);
  color: rgba(255,255,255,0.82);
  border-top: 1px solid rgba(255,255,255,0.10);
  font-size: 12px;
  z-index: 999999;
  backdrop-filter: blur(10px);
}
</style>
        """,
        unsafe_allow_html=True,
    )

def render_hero():
    st.markdown(
        f"""
<div class="misharp-hero">
  <h1>{APP_TITLE}</h1>
  <p>{APP_SUBTITLE}</p>
</div>
        """,
        unsafe_allow_html=True,
    )

def render_top_actions():
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.button("FREE | 무로그인 시작", use_container_width=True)
    with c2:
        st.button("PRO 가입 (준비중)", use_container_width=True, disabled=True)
    with c3:
        st.button("사용/협업 문의", use_container_width=True)

def render_dashboard(shared):
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">대시보드</div>', unsafe_allow_html=True)
    st.markdown(
        """
- 왼쪽 메뉴에서 원하는 생성기를 선택하세요.
- 각 생성기는 **독립적으로** 사용할 수 있습니다. (공통 입력은 선택)
- 결과물은 각 화면에서 다운로드할 수 있습니다.
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

def render_copywriter(shared):
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">원고 생성 (준비중)</div>', unsafe_allow_html=True)
    st.info("원고 생성기는 다음 단계에서 연결합니다. (현재는 UI만 정리)")
    st.markdown('</div>', unsafe_allow_html=True)

def render_collector(shared):
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">이미지 수집툴 (준비중)</div>', unsafe_allow_html=True)
    st.info("상세페이지 URL에서 이미지 수집 기능은 다음 단계에서 연결합니다. (현재는 UI만 정리)")
    st.markdown('</div>', unsafe_allow_html=True)

def render_shortform(shared):
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">숏폼 메이커 (준비중)</div>', unsafe_allow_html=True)
    st.info("숏폼 문구/콘티 생성은 다음 단계에서 연결합니다. (현재는 UI만 정리)")
    st.markdown('</div>', unsafe_allow_html=True)

def sidebar_nav():
    st.sidebar.markdown("## MISHARP SELLER OS")
    labels = [x[0] for x in MENU]
    keys = [x[1] for x in MENU]
    default_label = labels[0]
    choice = st.sidebar.radio("생성기 메뉴", labels, index=0)
    page_key = keys[labels.index(choice)]

    with st.sidebar.expander("프로젝트 정보 (선택 입력)", expanded=False):
        inp = st.session_state["selleros_inputs"]
        inp["상품명"] = st.text_input("상품명", inp.get("상품명",""))
        inp["가격"] = st.text_input("가격", inp.get("가격",""))
        inp["소재"] = st.text_input("소재", inp.get("소재",""))
        inp["핏"] = st.text_input("핏", inp.get("핏",""))
        inp["사이즈"] = st.text_input("사이즈", inp.get("사이즈",""))
        inp["컬러"] = st.text_input("컬러", inp.get("컬러",""))
        inp["키워드"] = st.text_input("키워드(쉼표구분)", inp.get("키워드",""))
        inp["금칙어"] = st.text_input("금칙어(쉼표구분)", inp.get("금칙어",""))
        inp["상품URL"] = st.text_input("상품 URL(선택)", inp.get("상품URL",""))
        st.caption("※ 공통 입력은 **선택**입니다. 입력하지 않아도 각 생성기를 사용할 수 있어요.")

        if st.button("입력 초기화", use_container_width=True):
            st.session_state["selleros_inputs"] = {
                "상품명": "", "가격": "", "소재": "", "핏": "", "사이즈": "", "컬러": "",
                "키워드": "", "금칙어": "", "상품URL": "", "특장점5줄": ["","","","",""],
            }
            st.toast("초기화 완료")

    return page_key

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🧩", layout="wide")
    _init_state()
    inject_css()

    page_key = sidebar_nav()

    # main header
    render_hero()
    st.write("")
    render_top_actions()
    st.write("")

    shared = {
        "inputs": st.session_state.get("selleros_inputs", {}),
        "outputs": {},
    }

    # page switch
    if page_key == "dashboard":
        render_dashboard(shared)
    elif page_key == "detail":
        detail_page.render(shared)
    elif page_key == "thumb":
        thumbnail.render(shared)
    elif page_key == "gif":
        gif_maker.render(shared)
    elif page_key == "blog":
        blog.render(shared)
    elif page_key == "copy":
        render_copywriter(shared)
    elif page_key == "collector":
        render_collector(shared)
    elif page_key == "shortform":
        render_shortform(shared)
    else:
        render_dashboard(shared)

    st.markdown(
        """
<div class="misharp-footer">
  © 2026 misharpcompany. All rights reserved. &nbsp; | &nbsp;
  본 프로그램은 미샵컴퍼니 내부 직원 전용으로, 외부 유출 및 제3자 제공을 금합니다.
</div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
