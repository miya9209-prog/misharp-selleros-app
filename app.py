
import os, json, io, datetime, uuid
import streamlit as st

APP_TITLE = "미샵 셀러 스튜디오 OS V1"

PAGES = [
    ("대시보드", "업무 바로가기·할 일·메모를 한 화면에서 관리하세요.", "dashboard"),
    ("상세페이지 생성", "이미지 업로드만 하면 상세페이지가 자동으로 완성됩니다.", "detailpage"),
    ("썸네일 생성", "규격에 맞게 자동 배치·텍스트 합성으로 썸네일을 만듭니다.", "thumbnail"),
    ("GIF 생성", "이미지/영상으로 상품 GIF를 빠르게 생성합니다.", "gif"),
    ("블로그 작성", "상품/키워드 기반으로 SEO 글 초안을 빠르게 만듭니다.", "blog"),
    ("이미지 수집툴", "상품 이미지 크롭/추출을 도와주는 도구입니다.", "image_crop"),
]


# -----------------------------
# Page config (only once)
# -----------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")

# -----------------------------
# Global CSS (top padding fix + sidebar brand)
# -----------------------------
st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, .stTextInput, .stSelectbox, .stTextArea, .stButton, .stDownloadButton {
  font-family: 'Nanum Gothic', sans-serif !important;
}

/* Fix top clipping / spacing */
div.block-container { padding-top: 3.2rem; padding-bottom: 3rem; max-width: 1200px; }

/* Subtle dark cards */
.ms-card {
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 18px 18px;
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(6px);
}
.ms-card + .ms-card { margin-top: 14px; }

.ms-header {
  border-radius: 18px;
  padding: 18px 18px;
  margin-top: 0.25rem;
  margin-bottom: 18px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.05);
}
.ms-title { font-size: 30px; font-weight: 800; margin: 0; color: rgba(255,255,255,0.92); }
.ms-sub { font-size: 13px; margin: 8px 0 0 0; color: rgba(255,255,255,0.70); line-height: 1.5; }

/* Sidebar brand */
a.ms-brand{
  display:block;
  font-weight:800;
  font-size: 24px;
  letter-spacing: 0.6px;
  margin: 0.2rem 0 1rem 0;
  padding: 0.35rem 0.45rem;
  border-radius: 12px;
  color: rgba(255,255,255,0.92);
  text-decoration: none;
}
a.ms-brand:hover{
  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.95);
}

/* Sidebar radio spacing */
section[data-testid="stSidebar"] .stRadio > div { gap: 6px; }
section[data-testid="stSidebar"] label { font-size: 15px; }

/* Buttons */
.stButton>button, .stDownloadButton>button {
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.06) !important;
  color: rgba(255,255,255,0.92) !important;
}
.stButton>button:hover, .stDownloadButton>button:hover {
  background: rgba(255,255,255,0.10) !important;
  border-color: rgba(255,255,255,0.22) !important;
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
  border-radius: 12px !important;
}
</style>

""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def set_page(page_key: str):
    st.session_state["page"] = page_key

def get_page():
    return st.session_state.get("page", "dashboard")

def header(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="ms-header">
          <div class="ms-title">{title}</div>
          <div class="ms-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def run_embedded_app(app_key: str):
    """Load an embedded tool from apps/<app_key>/app.py.
    If it exposes render(), call it. Otherwise, assume it renders on import.
    """
    import importlib.util
    base = os.path.join(os.path.dirname(__file__), "apps", app_key)
    target = os.path.join(base, "app.py")
    if not os.path.exists(target):
        st.error(f"앱 파일을 찾을 수 없습니다: {target}")
        return
    try:
        spec = importlib.util.spec_from_file_location(f"apps.{app_key}", target)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        if hasattr(module, "render") and callable(getattr(module, "render")):
            module.render()
        else:
         pass   # This tool does not expose render(); assume it renders at import time.
    except Exception as e:
        st.error(f"앱 실행 중 오류: {e}")

# -----------------------------

# Sidebar Navigation
# -----------------------------
with st.sidebar:
    # Brand: click to dashboard
    st.markdown("""<a class='ms-brand' href='https://misharp-selleros.com'>MISHARP SELLER OS</a>""", unsafe_allow_html=True)

    # Sync query param -> session_state
    qp = st.query_params
    if "page" in qp:
        st.session_state["page"] = qp.get("page")
    current = get_page()

    labels = [p[0] for p in PAGES]
    keys   = [p[2] for p in PAGES]
    idx = keys.index(current) if current in keys else 0

    choice = st.radio("메뉴", labels, index=idx, label_visibility="collapsed")
    page_key = keys[labels.index(choice)]
    if page_key != current:
        st.query_params.update({"page": page_key})
        set_page(page_key)

# -----------------------------
# Dashboard (personal)
# -----------------------------

def dashboard():
    # 사용자 개인 업무용 대시보드
    import uuid
    from datetime import datetime

    # page_header() handles the title/subtitle

    # --- state init ---
    if "dash_shortcuts" not in st.session_state:
        st.session_state.dash_shortcuts = [
            {"id": str(uuid.uuid4()), "title": "미샵 관리자", "url": "https://misharp.co.kr", "emoji": "🛍️"},
            {"id": str(uuid.uuid4()), "title": "카페24 관리자", "url": "https://eclogin.cafe24.com/Shop/", "emoji": "🧾"},
        ]
    if "dash_memo" not in st.session_state:
        st.session_state.dash_memo = ""
    if "dash_todos" not in st.session_state:
        st.session_state.dash_todos = []  # [{"id":..., "text":..., "done": False}]

    def _valid_url(url: str) -> bool:
        url = (url or "").strip()
        return url.startswith("http://") or url.startswith("https://")

    # -----------------------------
    # TOP: 오늘 / 오늘 메모 / 오늘 할일 (한 줄)
    # -----------------------------
    c1, c2, c3 = st.columns([1.1, 2.2, 2.2], gap="large")

    with c1:
        now = datetime.now()
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown(f"### 오늘\n**{now.strftime('%Y-%m-%d')}**")
        st.caption(now.strftime("%A"))
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown("### 오늘 메모")
        st.session_state.dash_memo = st.text_area(
            label="",
            value=st.session_state.dash_memo,
            height=140,
            placeholder="오늘 중요한 메모를 적어두세요.",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown("### 오늘 할일")

        add_cols = st.columns([3, 1])
        with add_cols[0]:
            new_todo = st.text_input("할일 추가", "", placeholder="예) 상세페이지 3개 생성", label_visibility="collapsed")
        with add_cols[1]:
            add_clicked = st.button("추가", key="todo_add", use_container_width=True)

        if add_clicked and new_todo.strip():
            st.session_state.dash_todos.append(
                {"id": str(uuid.uuid4()), "text": new_todo.strip(), "done": False}
            )
            st.rerun()

        # 리스트
        remove_ids = []
        for item in st.session_state.dash_todos:
            row = st.columns([0.12, 0.74, 0.14])
            item["done"] = row[0].checkbox("", value=item.get("done", False), key=f"todo_done_{item['id']}")
            row[1].markdown(item["text"])
            if row[2].button("삭제", key=f"todo_del_{item['id']}"):
                remove_ids.append(item["id"])
        if remove_ids:
            st.session_state.dash_todos = [t for t in st.session_state.dash_todos if t["id"] not in remove_ids]
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -----------------------------
    # BOTTOM: 바로가기 (하단 배치)
    # -----------------------------
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown("### 바로가기")

    # 보기: 카드 그리드
    shortcuts = st.session_state.dash_shortcuts
    if not shortcuts:
        st.info("아직 바로가기가 없습니다. 아래에서 추가해보세요.")
    else:
        cols = st.columns(4, gap="medium")
        for i, sc in enumerate(shortcuts):
            with cols[i % 4]:
                st.markdown('<div class="ms-shortcut-card">', unsafe_allow_html=True)
                st.markdown(f"<div class='ms-shortcut-emoji'>{sc.get('emoji','🔗')}</div>", unsafe_allow_html=True)
                st.markdown(f"**{sc.get('title','(제목 없음)')}**")
                st.caption(sc.get("url", ""))
                st.link_button("열기", sc.get("url", ""), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    with st.expander("바로가기 추가/편집", expanded=False):
        st.markdown("**새 바로가기 추가**")
        a1, a2, a3, a4 = st.columns([1.1, 2.2, 3.3, 1.2])
        emoji = a1.text_input("아이콘", "🔗", key="sc_add_emoji")
        title = a2.text_input("제목", "", key="sc_add_title")
        url = a3.text_input("URL", "", key="sc_add_url", placeholder="https:// 로 시작")
        if a4.button("추가", key="shortcut_add", use_container_width=True):
            if not title.strip():
                st.error("제목을 입력해 주세요.")
            elif not _valid_url(url):
                st.error("URL은 http:// 또는 https:// 로 시작해야 합니다.")
            else:
                st.session_state.dash_shortcuts.append(
                    {"id": str(uuid.uuid4()), "title": title.strip(), "url": url.strip(), "emoji": (emoji or "🔗").strip()}
                )
                st.success("추가되었습니다.")
                st.rerun()

        st.divider()
        st.markdown("**기존 바로가기 관리**")
        for sc in list(st.session_state.dash_shortcuts):
            row = st.columns([1.2, 2.2, 4.2, 1.2])
            row[0].markdown(sc.get("emoji", "🔗"))
            new_title = row[1].text_input("제목", sc.get("title", ""), key=f"sc_title_{sc['id']}", label_visibility="collapsed")
            new_url = row[2].text_input("URL", sc.get("url", ""), key=f"sc_url_{sc['id']}", label_visibility="collapsed")
            if row[3].button("삭제", key=f"sc_rm_{sc['id']}", use_container_width=True):
                st.session_state.dash_shortcuts = [x for x in st.session_state.dash_shortcuts if x["id"] != sc["id"]]
                st.rerun()
            # 저장(자동 반영)
            sc["title"] = new_title
            sc["url"] = new_url

    st.markdown("</div>", unsafe_allow_html=True)
# -----------------------------
# Pages
# -----------------------------
# -------------------
page = get_page()

page_meta = {
    "dashboard": ("대시보드", "오늘 날짜/메모/바로가기로 나만의 작업 대시보드를 구성해보세요."),
    "detailpage": ("상세페이지 생성", "상품 이미지로 상세페이지를 자동 구성하고 결과물을 저장합니다."),
    "thumbnail": ("썸네일 생성", "상세페이지/피드용 썸네일을 빠르게 생성합니다."),
    "gif": ("GIF 생성", "상품 이미지를 GIF로 만들어 SNS/상세페이지에 활용합니다."),
    "blog": ("블로그 작성", "상품/이벤트용 블로그 원고 초안을 빠르게 생성합니다."),
    "image_crop": ("이미지 수집툴", "이미지 크롭/추출 등 이미지 준비 작업을 빠르게 처리합니다."),
}

if page == "dashboard":
    header(*page_meta["dashboard"])
    dashboard()

elif page in page_meta:
    header(*page_meta[page])
    if page == "image_crop":
        run_embedded_app("image_crop")
    else:
        run_embedded_app(page)

else:
    header("미샵 셀러 스튜디오 OS v1", "온라인 셀러를 위한 원스톱 콘텐츠 자동 생성 도구")
    st.info("페이지를 찾을 수 없습니다. 좌측 메뉴에서 다시 선택해주세요.")
