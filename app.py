
import os, json, io, runpy, datetime, uuid
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
div.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1200px; }

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
    If it exposes render(), call it. Otherwise, run the file with runpy.
    """
    import importlib.util, runpy
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
            runpy.run_path(target, run_name="__main__")
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
    header("대시보드", "오늘 날짜/바로가기/할 일/메모로 업무를 빠르게 정리하세요.")

    # ---- state ----
    st.session_state.setdefault("shortcuts", [])   # list[{id,emoji,title,url,created_at}]
    st.session_state.setdefault("todo_items", [])  # list[{id,text,done,created_at}]
    st.session_state.setdefault("memo_text", "")

    def _valid_url(u: str) -> bool:
        try:
            from urllib.parse import urlparse
            p = urlparse((u or "").strip())
            return p.scheme in ("http", "https") and bool(p.netloc)
        except Exception:
            return False

    def _new_id(prefix="id"):
        return f"{prefix}_{uuid.uuid4().hex[:10]}"

    # ---- Top: date + backup/restore ----
    now = datetime.datetime.now()
    top1, top2, top3 = st.columns([1.1, 1.0, 1.1], gap="large")

    with top1:
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.subheader("오늘", anchor=False)
        st.write(now.strftime("%Y-%m-%d (%a)"))
        st.write(now.strftime("%H:%M"))
        st.markdown('<div class="small-muted">이번 작업은 자동 저장되지 않습니다. 필요하면 백업을 눌러주세요.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with top2:
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.subheader("오늘의 메모", anchor=False)
        st.session_state["memo_text"] = st.text_area(
            "메모",
            value=st.session_state["memo_text"],
            height=120,
            label_visibility="collapsed",
            placeholder="오늘 꼭 기억할 것, 진행상황, 아이디어 등을 적어두세요."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    left, right = st.columns([1.35, 1.0], gap="large")

    # ---- Left: shortcuts ----
    with left:
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.subheader("바로가기", anchor=False)

        with st.expander("➕ 바로가기 추가", expanded=True):
            c1, c2 = st.columns([0.30, 0.70])
            with c1:
                emoji = st.text_input("아이콘(선택)", placeholder="예: 🔗", key="sc_emoji")
            with c2:
                title = st.text_input("이름", placeholder="예: 스마트스토어 관리자", key="sc_title")
            url = st.text_input("URL", placeholder="https:// ...", key="sc_url")

            add = st.button("바로가기 추가", type="primary", use_container_width=True)
            if add:
                if not (title or "").strip():
                    st.warning("이름을 입력해 주세요.")
                elif not _valid_url(url):
                    st.warning("URL 형식이 올바르지 않습니다. (https:// 포함)")
                else:
                    st.session_state["shortcuts"].insert(
                        0,
                        {
                            "id": _new_id("sc"),
                            "emoji": ((emoji or "").strip() or "🔗"),
                            "title": title.strip(),
                            "url": url.strip(),
                            "created_at": datetime.datetime.now().isoformat(),
                        },
                    )
                    st.success("추가되었습니다.")
                    st.session_state["sc_emoji"] = ""
                    st.session_state["sc_title"] = ""
                    st.session_state["sc_url"] = ""
                    st.rerun()

        items = st.session_state["shortcuts"]
        if not items:
            st.info("아직 바로가기가 없습니다. 위에서 추가해보세요.")
        else:
            cols = st.columns(2, gap="medium")
            for idx, sc in enumerate(items):
                with cols[idx % 2]:
                    st.markdown('<div class="tile">', unsafe_allow_html=True)
                    st.markdown(f'<div class="t-title">{sc["emoji"]} {sc["title"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="t-url">{sc["url"]}</div>', unsafe_allow_html=True)
                    st.link_button("열기", sc["url"], use_container_width=True)

                    b1, b2, b3 = st.columns([1,1,1])
                    with b1:
                        if st.button("▲", key=f"sc_up_{sc['id']}", use_container_width=True, disabled=(idx==0)):
                            items[idx-1], items[idx] = items[idx], items[idx-1]
                            st.session_state["shortcuts"] = items
                            st.rerun()
                    with b2:
                        if st.button("▼", key=f"sc_dn_{sc['id']}", use_container_width=True, disabled=(idx==len(items)-1)):
                            items[idx+1], items[idx] = items[idx], items[idx+1]
                            st.session_state["shortcuts"] = items
                            st.rerun()
                    with b3:
                        if st.button("삭제", key=f"sc_del_{sc['id']}", use_container_width=True):
                            st.session_state["shortcuts"] = [x for x in items if x["id"] != sc["id"]]
                            st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Right: todo ----
    with right:
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.subheader("오늘의 할 일", anchor=False)

        with st.form("todo_add", clear_on_submit=True):
            t = st.text_input("할 일 추가", placeholder="예: 신상 5개 상세페이지 생성", label_visibility="collapsed")
            ok = st.form_submit_button("추가", use_container_width=True)
        if ok and (t or "").strip():
            st.session_state["todo_items"].insert(
                0,
                {"id": _new_id("td"), "text": t.strip(), "done": False, "created_at": datetime.datetime.now().isoformat()},
            )
            st.rerun()

        items = st.session_state["todo_items"]
        if not items:
            st.caption("할 일을 추가해보세요.")
        else:
            for it in items:
                c1, c2 = st.columns([0.85, 0.15])
                with c1:
                    it["done"] = st.checkbox(it["text"], value=it.get("done", False), key=f"td_ck_{it['id']}")
                with c2:
                    if st.button("삭제", key=f"td_del_{it['id']}", use_container_width=True):
                        st.session_state["todo_items"] = [x for x in items if x["id"] != it["id"]]
                        st.rerun()

            done_count = sum(1 for x in st.session_state["todo_items"] if x.get("done"))
            if done_count:
                if st.button(f"완료 항목 {done_count}개 삭제", use_container_width=True):
                    st.session_state["todo_items"] = [x for x in st.session_state["todo_items"] if not x.get("done")]
                    st.rerun()

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
