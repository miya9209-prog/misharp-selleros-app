
import os, json, io, runpy, datetime
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
div.block-container { padding-top: 2.0rem; padding-bottom: 3rem; }

/* Sidebar brand button style */
.sidebar-brand {
  display: block;
  font-weight: 800;
  font-size: 18px;
  letter-spacing: 0.5px;
  margin: 0.15rem 0 0.8rem 0;
  padding: 0.35rem 0.5rem;
  border-radius: 10px;
  cursor: pointer;
  color: #111;
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

/* Dashboard cards */
.card {
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 14px 14px;
  background: #fff;
}
.small-muted { color: rgba(0,0,0,0.6); font-size: 12px; }
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
    header("나만의 대시보드", "자주 쓰는 바로가기와 오늘의 할 일·메모를 관리하세요.")

    # init state
    st.session_state.setdefault("dash_links", [])
    st.session_state.setdefault("dash_todos", [])
    st.session_state.setdefault("dash_memo", "")

    now = datetime.datetime.now()
    colA, colB, colC = st.columns([1.2,1,1])
    with colA:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("오늘")
        st.write(now.strftime("%Y-%m-%d (%a)"))
        st.write(now.strftime("%H:%M"))
        st.markdown('</div>', unsafe_allow_html=True)

    with colB:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("대시보드 백업/복원")
        data = {
            "links": st.session_state["dash_links"],
            "todos": st.session_state["dash_todos"],
            "memo": st.session_state["dash_memo"],
        }
        st.download_button(
            "내 대시보드 JSON 다운로드",
            data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="misharp_dashboard.json",
            mime="application/json",
            use_container_width=True
        )
        up = st.file_uploader("JSON 업로드(복원)", type=["json"], label_visibility="collapsed")
        if up is not None:
            try:
                loaded = json.loads(up.read().decode("utf-8"))
                st.session_state["dash_links"] = loaded.get("links", [])
                st.session_state["dash_todos"] = loaded.get("todos", [])
                st.session_state["dash_memo"] = loaded.get("memo", "")
                st.success("복원 완료! (페이지가 자동 갱신됩니다)")
                st.rerun()
            except Exception as e:
                st.error(f"복원 실패: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with colC:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("빠른 추가")
        with st.form("add_link", clear_on_submit=True):
            title = st.text_input("바로가기 이름", placeholder="예: 스마트스토어 관리자")
            url = st.text_input("URL", placeholder="https://...")
            emoji = st.text_input("아이콘(선택)", placeholder="🔗")
            submitted = st.form_submit_button("바로가기 추가", use_container_width=True)
        if submitted:
            if not title or not url:
                st.warning("이름과 URL을 입력해 주세요.")
            else:
                st.session_state["dash_links"].append({"title": title, "url": url, "emoji": emoji})
                st.success("추가 완료")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("내 바로가기")
        links = st.session_state["dash_links"]
        if not links:
            st.caption("아직 바로가기가 없습니다. 오른쪽에서 추가해보세요.")
        else:
            for i, item in enumerate(links):
                c1, c2, c3, c4 = st.columns([3,1,1,1])
                label = f'{item.get("emoji","") or ""} {item.get("title","")}'
                with c1:
                    st.markdown(f"- [{label}]({item.get('url','')})")
                with c2:
                    if st.button("위", key=f"up_{i}", use_container_width=True, disabled=(i==0)):
                        links[i-1], links[i] = links[i], links[i-1]
                        st.session_state["dash_links"] = links
                        st.rerun()
                with c3:
                    if st.button("아래", key=f"down_{i}", use_container_width=True, disabled=(i==len(links)-1)):
                        links[i+1], links[i] = links[i], links[i+1]
                        st.session_state["dash_links"] = links
                        st.rerun()
                with c4:
                    if st.button("삭제", key=f"del_{i}", use_container_width=True):
                        links.pop(i)
                        st.session_state["dash_links"] = links
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("오늘의 할 일")
        with st.form("add_todo", clear_on_submit=True):
            todo = st.text_input("할 일", placeholder="예: 신상 등록 5개")
            add = st.form_submit_button("추가", use_container_width=True)
        if add and todo:
            st.session_state["dash_todos"].append({"text": todo, "done": False})
            st.rerun()

        todos = st.session_state["dash_todos"]
        if todos:
            for i, t in enumerate(todos):
                cols = st.columns([0.15, 0.75, 0.1])
                with cols[0]:
                    done = st.checkbox("", value=t["done"], key=f"todo_done_{i}")
                with cols[1]:
                    st.write(("✅ " if done else "▫️ ") + t["text"])
                with cols[2]:
                    if st.button("✖", key=f"todo_del_{i}"):
                        todos.pop(i)
                        st.session_state["dash_todos"] = todos
                        st.rerun()
                t["done"] = done
            if st.button("완료 항목 삭제", use_container_width=True):
                st.session_state["dash_todos"] = [t for t in todos if not t["done"]]
                st.rerun()
        else:
            st.caption("할 일을 추가해보세요.")

        st.write("")
        st.subheader("오늘의 메모")
        memo = st.text_area("", value=st.session_state["dash_memo"], height=140, placeholder="메모를 적어두세요…")
        st.session_state["dash_memo"] = memo

        st.markdown('</div>', unsafe_allow_html=True)

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
    # Embed via iframe (best effort) + open link
    st.link_button("새 탭에서 열기", IMAGE_CROP_URL, use_container_width=False)
    st.components.v1.iframe(IMAGE_CROP_URL, height=900, scrolling=True)
else:
    st.error("페이지를 찾을 수 없습니다.")
