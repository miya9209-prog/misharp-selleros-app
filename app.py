
import os, json, io, runpy, datetime, uuid
import streamlit as st

APP_TITLE = "미샵 셀러 스튜디오 OS V1"

PAGES = [
    ("대시보드", "업무 바로가기·할 일·메모를 한 화면에서 관리하세요.", "dashboard"),
    ("상세페이지 생성", "이미지 업로드만 하면 상세페이지가 자동으로 완성됩니다.", "detailpage"),
    ("썸네일 생성", "규격에 맞게 자동 배치·텍스트 합성으로 썸네일을 만듭니다.", "thumbnail"),
    ("GIF 생성", "이미지/영상으로 상품 GIF를 빠르게 생성합니다.", "gif"),
    ("블로그 작성", "상품/키워드 기반으로 SEO 글 초안을 빠르게 만듭니다.", "blog"),
    ("이미지 수집툴", "상품 이미지 크롭/추출을 도와주는 도구입니다.", "imagecrop"),
]

IMAGE_CROP_URL = "https://misharp-image-crop-v1.streamlit.app/"

# -----------------------------
# Page config (only once)
# -----------------------------
st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")

# -----------------------------
# Global CSS (top padding fix + sidebar brand)
# -----------------------------
st.markdown("""
<style>
/* Fix top clipping */
div.block-container { padding-top: 3.4rem; padding-bottom: 3rem; }

/* Sidebar brand button style */
.sidebar-brand {
  display: block;
  font-weight: 800;
  font-size: 22px;
  letter-spacing: 0.5px;
  margin: 0.15rem 0 0.8rem 0;
  padding: 0.35rem 0.5rem;
  border-radius: 10px;
  cursor: pointer;
  color: #111; text-transform: uppercase;
  text-decoration: none;
}
.sidebar-brand:hover { background: rgba(0,0,0,0.06); }

/* Page header card */
.page-header {
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 18px 18px;
  margin-bottom: 16px;
  background: #fff;
}
.page-title { font-size: 26px; font-weight: 800; margin: 0; color: #111; }
.page-sub { font-size: 13px; margin: 6px 0 0 0; color: rgba(0,0,0,0.65); }


/* Shortcut tiles */
.tile{
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 12px 12px;
  margin-bottom: 12px;
  background: #fff;
}
.t-title{ font-weight: 700; font-size: 14px; margin-bottom: 6px; color:#111; }
.t-url{ font-size: 12px; color: rgba(0,0,0,0.55); word-break: break-all; margin-bottom: 10px; }

/* Dashboard cards */
.card {
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 14px 14px;
  background: #fff;
}
.small-muted { color: rgba(0,0,0,0.6); font-size: 12px; }

/* Sidebar radio spacing */
section[data-testid="stSidebar"] div[role="radiogroup"] > label { 
  padding: 6px 8px; border-radius: 10px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { 
  background: rgba(0,0,0,0.05);
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
        <div class="page-header">
          <div class="page-title">{title}</div>
          <div class="page-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def run_embedded_app(app_dir: str):
    import sys
    """Run an embedded Streamlit app (app.py) under apps/<app_dir>/app.py."""
    base = os.path.join(os.path.dirname(__file__), "apps", app_dir)
    target = os.path.join(base, "app.py")
    if not os.path.exists(target):
        st.error(f"앱 파일을 찾을 수 없습니다: {target}")
        return
    cwd = os.getcwd()
    try:
        os.chdir(base)
        if base not in sys.path:
            sys.path.insert(0, base)
        # Run in isolated globals; Streamlit will render as it executes
        runpy.run_path(target, run_name="__main__")
    finally:
        os.chdir(cwd)

# -----------------------------
# Sidebar Navigation
# -----------------------------
with st.sidebar:
    # Brand: click to dashboard
    st.markdown(f'<a class="sidebar-brand" href="?page=dashboard">MISHARP SELLER OS</a>', unsafe_allow_html=True)

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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("오늘", anchor=False)
        st.write(now.strftime("%Y-%m-%d (%a)"))
        st.write(now.strftime("%H:%M"))
        st.markdown('<div class="small-muted">이번 작업은 자동 저장되지 않습니다. 필요하면 백업을 눌러주세요.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with top2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("오늘의 메모", anchor=False)
        st.session_state["memo_text"] = st.text_area(
            "메모",
            value=st.session_state["memo_text"],
            height=120,
            label_visibility="collapsed",
            placeholder="오늘 꼭 기억할 것, 진행상황, 아이디어 등을 적어두세요."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with top3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("대시보드 백업/복원", anchor=False)

        data = {
            "shortcuts": st.session_state["shortcuts"],
            "todo_items": st.session_state["todo_items"],
            "memo_text": st.session_state["memo_text"],
        }

        st.download_button(
            "현재 대시보드 JSON 다운로드",
            data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="misharp_dashboard.json",
            mime="application/json",
            use_container_width=True,
        )

        up = st.file_uploader("JSON 업로드(복원)", type=["json"], label_visibility="collapsed")
        if up is not None:
            try:
                loaded = json.loads(up.read().decode("utf-8"))
                st.session_state["shortcuts"] = loaded.get("shortcuts", [])
                st.session_state["todo_items"] = loaded.get("todo_items", [])
                st.session_state["memo_text"] = loaded.get("memo_text", "")
                st.success("복원 완료! (페이지가 새로고침됩니다)")
                st.rerun()
            except Exception as e:
                st.error(f"복원 실패: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    left, right = st.columns([1.35, 1.0], gap="large")

    # ---- Left: shortcuts ----
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
page = get_page()

if page == "dashboard":
    dashboard()
elif page == "detailpage":
    header("상세페이지 생성", "이미지 업로드만 하면 상세페이지가 자동으로 완성됩니다.")
    run_embedded_app("detailpage")
elif page == "thumbnail":
    header("썸네일 생성", "규격에 맞게 자동 배치·텍스트 합성으로 썸네일을 만듭니다.")
    run_embedded_app("thumbnail")
elif page == "gif":
    header("GIF 생성", "이미지/영상으로 상품 GIF를 빠르게 생성합니다.")
    run_embedded_app("gif")
elif page == "blog":
    header("블로그 작성", "상품/키워드 기반으로 SEO 글 초안을 빠르게 만듭니다.")
    run_embedded_app("blog")
elif page == "imagecrop":
    header("이미지 수집툴", "이미지 크롭/추출 도구를 OS 안에 탑재했습니다.")
    # Embed inside OS (iframe). 일부 브라우저/정책에서 차단될 수 있습니다.
    st.components.v1.iframe(IMAGE_CROP_URL, height=980, scrolling=True)
else:
    st.error("페이지를 찾을 수 없습니다.")
