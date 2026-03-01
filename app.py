import datetime as dt
import json
from urllib.parse import urlparse

import streamlit as st

# =========================
# Branding / Global
# =========================
APP_BRAND = "MISHARP SELLER OS"
APP_TITLE = "미샵 셀러 스튜디오 OS v1"

IMAGE_COLLECTOR_URL = "https://misharp-image-crop-v1.streamlit.app/"
# (추후) 각 툴이 통합되면 내부 페이지로 교체
EXTERNAL_PLACEHOLDER = {
    "detail": None,
    "thumb": None,
    "gif": None,
    "blog": None,
    "shortform": None,
}

PAGES = [
    {
        "key": "dashboard",
        "name": "대시보드",
        "title": "나만의 업무 대시보드",
        "subtitle": "업무에 필요한 바로가기 + 오늘의 할 일을 한 화면에 정리하세요.",
        "icon": "📌",
    },
    {
        "key": "detail",
        "name": "상세페이지 생성",
        "title": "상세페이지 생성기",
        "subtitle": "상품 상세페이지 제작을 빠르게 시작할 수 있도록 이미지/자료를 정리합니다.",
        "icon": "🧩",
    },
    {
        "key": "thumb",
        "name": "썸네일 생성",
        "title": "썸네일 생성기",
        "subtitle": "규격에 맞춰 대표 이미지를 만들고, 채널별 썸네일을 빠르게 뽑습니다.",
        "icon": "🖼️",
    },
    {
        "key": "gif",
        "name": "GIF 생성",
        "title": "GIF 생성기",
        "subtitle": "상품 컷/영상으로 GIF를 만들어 상세·배너·SNS에 바로 쓰도록 준비합니다.",
        "icon": "🎞️",
    },
    {
        "key": "collector",
        "name": "이미지 수집툴",
        "title": "이미지 수집툴",
        "subtitle": "기존 수집툴을 열어 이미지 크롭/정리를 바로 진행합니다.",
        "icon": "🧲",
    },
    {
        "key": "blog",
        "name": "블로그 작성",
        "title": "블로그 글 자동 초안",
        "subtitle": "상품 정보를 바탕으로 SEO 친화적인 블로그 글 초안을 생성합니다.",
        "icon": "✍️",
    },
    {
        "key": "shortform",
        "name": "숏폼 메이커",
        "title": "숏폼 콘텐츠 메이커",
        "subtitle": "릴스/쇼츠용 콘티·후킹 문구·구성 아이디어를 빠르게 정리합니다.",
        "icon": "🚀",
    },
]


def _page_meta(page_key: str) -> dict:
    for p in PAGES:
        if p["key"] == page_key:
            return p
    return PAGES[0]


def _valid_url(u: str) -> bool:
    try:
        p = urlparse(u.strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def _init_state():
    st.session_state.setdefault("page", "dashboard")

    # dashboard state
    st.session_state.setdefault("shortcuts", [])  # list[{id,title,url,emoji,created_at}]
    st.session_state.setdefault("memo_text", "")
    st.session_state.setdefault("todo_items", [])  # list[{id,text,done,created_at}]
    st.session_state.setdefault("todo_new", "")

    # UI toggles
    st.session_state.setdefault("dash_edit_mode", True)


def inject_css():
    st.markdown(
        """
        <style>
          :root{
            --card-bg: rgba(255,255,255,0.06);
            --card-border: rgba(255,255,255,0.10);
            --muted: rgba(255,255,255,0.70);
          }
          /* Give breathing room so top header/card never looks clipped */
          .block-container { padding-top: 2.2rem !important; padding-bottom: 2.6rem !important; max-width: 1200px; }
          header[data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }

          /* Sidebar */
          [data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.08); }
          [data-testid="stSidebar"] .stButton button { width: 100%; border-radius: 12px; }

          /* Brand button */
          .brand-btn button{
            width: 100%;
            padding: 0.85rem 0.95rem !important;
            font-weight: 900 !important;
            letter-spacing: 0.6px;
            font-size: 1.05rem !important;
            border-radius: 14px !important;
          }
          .brand-btn button:hover{
            filter: brightness(1.06);
            transform: translateY(-1px);
          }

          /* Header card */
          .hero {
            padding: 1.35rem 1.5rem;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
            border: 1px solid rgba(255,255,255,0.10);
            box-shadow: 0 10px 30px rgba(0,0,0,0.20);
            margin-bottom: 1.2rem;
          }
          .hero .brandline{
            font-size: 0.90rem;
            color: rgba(255,255,255,0.75);
            margin-bottom: 0.35rem;
          }
          .hero .title{
            font-size: 2.05rem;
            font-weight: 900;
            margin: 0.1rem 0 0.45rem 0;
          }
          .hero .subtitle{
            font-size: 1.02rem;
            color: var(--muted);
            margin: 0.05rem 0 0 0;
            line-height: 1.5;
          }

          /* Cards */
          .card{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.1rem 1.1rem;
          }

          /* Shortcut tiles */
          .tile{
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 14px;
            padding: 0.85rem 0.9rem;
          }
          .tile .t-title{ font-weight: 800; margin-bottom: 0.25rem; }
          .tile .t-url{ color: rgba(255,255,255,0.65); font-size: 0.88rem; overflow-wrap:anywhere; }

          /* Make link buttons look nice */
          .stLinkButton a{
            border-radius: 12px !important;
            padding: 0.65rem 0.9rem !important;
          }

          /* Reduce “empty top space” in some components */
          section.main > div { padding-top: 0.25rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_nav():
    with st.sidebar:
        st.markdown('<div class="brand-btn">', unsafe_allow_html=True)
        if st.button(APP_BRAND, key="brand_home"):
            st.session_state.page = "dashboard"
        st.markdown("</div>", unsafe_allow_html=True)

        st.caption("좌측 메뉴에서 생성기를 선택하세요.")

        for p in PAGES:
            label = f'{p["icon"]}  {p["name"]}'
            is_active = st.session_state.page == p["key"]
            if st.button(label, key=f"nav_{p['key']}", type="primary" if is_active else "secondary"):
                st.session_state.page = p["key"]

        st.divider()
        st.caption("© 2026 misharpcompany. 내부 전용.")


def render_header(page_key: str):
    meta = _page_meta(page_key)
    now = dt.datetime.now()
    datestr = now.strftime("%Y.%m.%d (%a)").replace("Mon", "월").replace("Tue", "화").replace("Wed", "수").replace("Thu", "목").replace("Fri", "금").replace("Sat", "토").replace("Sun", "일")
    timestr = now.strftime("%H:%M")

    st.markdown(
        f"""
        <div class="hero">
          <div class="brandline">{APP_TITLE} · {datestr} {timestr}</div>
          <div class="title">{meta["title"]}</div>
          <div class="subtitle">{meta["subtitle"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Dashboard
# =========================
def _new_id(prefix: str) -> str:
    return f"{prefix}_{dt.datetime.now().strftime('%Y%m%d%H%M%S%f')}"


def dashboard_page():
    left, right = st.columns([1.35, 1.0], gap="large")

    # ---- Left: shortcuts ----
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("바로가기", anchor=False)

        with st.expander("➕ 바로가기 추가", expanded=True):
            c1, c2 = st.columns([0.38, 0.62])
            with c1:
                emoji = st.text_input("아이콘(선택)", placeholder="예: 🧵", key="sc_emoji")
            with c2:
                title = st.text_input("이름", placeholder="예: 도매처 주문관리", key="sc_title")

            url = st.text_input("URL", placeholder="https:// ...", key="sc_url")

            add = st.button("바로가기 추가", type="primary")
            if add:
                if not title.strip():
                    st.warning("이름을 입력해 주세요.")
                elif not _valid_url(url):
                    st.warning("URL 형식이 올바르지 않습니다. (https:// 포함)")
                else:
                    st.session_state.shortcuts.insert(
                        0,
                        {
                            "id": _new_id("sc"),
                            "emoji": (emoji.strip() or "🔗"),
                            "title": title.strip(),
                            "url": url.strip(),
                            "created_at": dt.datetime.now().isoformat(),
                        },
                    )
                    st.success("추가되었습니다.")
                    st.session_state.sc_emoji = ""
                    st.session_state.sc_title = ""
                    st.session_state.sc_url = ""

        # Grid
        items = st.session_state.shortcuts
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
                    if st.button("삭제", key=f"del_{sc['id']}", use_container_width=True):
                        st.session_state.shortcuts = [x for x in st.session_state.shortcuts if x["id"] != sc["id"]]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Right: todo + memo ----
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("오늘의 할 일", anchor=False)

        new_text = st.text_input("할 일 추가", placeholder="예: 신상 3개 촬영 요청", key="todo_new")
        if st.button("추가", type="primary", use_container_width=True):
            if new_text.strip():
                st.session_state.todo_items.insert(
                    0,
                    {"id": _new_id("td"), "text": new_text.strip(), "done": False, "created_at": dt.datetime.now().isoformat()},
                )
                st.session_state.todo_new = ""
                st.rerun()

        if not st.session_state.todo_items:
            st.caption("할 일이 비어있어요. 오늘의 1~3개만 적어도 충분합니다.")
        else:
            for t in st.session_state.todo_items:
                c1, c2 = st.columns([0.84, 0.16])
                with c1:
                    t["done"] = st.checkbox(t["text"], value=bool(t.get("done", False)), key=f"chk_{t['id']}")
                with c2:
                    if st.button("🗑️", key=f"rm_{t['id']}", use_container_width=True):
                        st.session_state.todo_items = [x for x in st.session_state.todo_items if x["id"] != t["id"]]
                        st.rerun()

            if st.button("완료 항목 삭제", use_container_width=True):
                st.session_state.todo_items = [x for x in st.session_state.todo_items if not x.get("done")]
                st.rerun()

        st.divider()
        st.subheader("메모", anchor=False)
        st.session_state.memo_text = st.text_area(
            "오늘 메모",
            value=st.session_state.memo_text,
            placeholder="예: CS 이슈 / 발주 메모 / 촬영 체크리스트 ...",
            height=220,
            label_visibility="collapsed",
        )

        # quick export/import
        with st.expander("백업/복원 (JSON)", expanded=False):
            export = {
                "shortcuts": st.session_state.shortcuts,
                "todo_items": st.session_state.todo_items,
                "memo_text": st.session_state.memo_text,
            }
            st.download_button(
                "내 대시보드 백업(JSON) 다운로드",
                data=json.dumps(export, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name="misharp_dashboard_backup.json",
                mime="application/json",
                use_container_width=True,
            )
            upl = st.file_uploader("백업 파일 업로드", type=["json"])
            if upl is not None:
                try:
                    data = json.loads(upl.read().decode("utf-8"))
                    st.session_state.shortcuts = list(data.get("shortcuts", []))
                    st.session_state.todo_items = list(data.get("todo_items", []))
                    st.session_state.memo_text = str(data.get("memo_text", ""))
                    st.success("복원 완료! 화면을 새로고침합니다.")
                    st.rerun()
                except Exception as e:
                    st.error(f"복원 실패: {e}")

        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# Placeholder pages
# =========================
def placeholder_page(page_key: str):
    meta = _page_meta(page_key)

    if page_key == "collector":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("아래 버튼을 눌러 **이미지 수집툴**을 여세요.")
        st.link_button("이미지 수집툴 열기", IMAGE_COLLECTOR_URL, use_container_width=True)
        st.caption("※ Streamlit 정책상 현재 페이지에 '완전한 임베드'가 제한될 수 있어, 우선 링크 방식으로 제공합니다.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("이 페이지는 **통합본 구조를 먼저 잡기 위한 자리**입니다.")
    st.write("형준님이 올려주신 각 레포(zip)의 기능을 **여기 안으로 하나씩 이식**해가며 완성합니다.")
    st.divider()

    st.write("다음 단계(개발 순서):")
    st.markdown(
        """
        - 1) 상세페이지 생성기: 기존 repo `app.py` 기능을 모듈화해서 이 페이지에 탑재  
        - 2) 썸네일 → 3) GIF → 4) 블로그 → 5) 숏폼  
        """
    )
    st.info("지금은 UI/네비게이션/대시보드(개인화)부터 확정하는 단계입니다.")
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🧰", layout="wide")

    _init_state()
    inject_css()
    sidebar_nav()

    page_key = st.session_state.page
    render_header(page_key)

    if page_key == "dashboard":
        dashboard_page()
    else:
        placeholder_page(page_key)


if __name__ == "__main__":
    main()
