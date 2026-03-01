
import json
import datetime as dt
import streamlit as st
from urllib.parse import urlparse

APP_TITLE = "미샵 셀러 스튜디오 OS v1"

PAGES = {
    "dashboard": {
        "name": "대시보드",
        "title": "나만의 업무 대시보드",
        "subtitle": "바로가기와 오늘의 할 일을 한 화면에 정리하세요.",
    },
    "detail": {
        "name": "상세페이지 생성",
        "title": "상세페이지 생성",
        "subtitle": "상품 이미지를 정리해 상세페이지 제작을 빠르게 시작합니다.",
    },
    "thumb": {
        "name": "썸네일 생성",
        "title": "썸네일 생성",
        "subtitle": "규격에 맞춰 이미지/텍스트를 배치해 썸네일을 만듭니다.",
    },
    "gif": {
        "name": "GIF 생성",
        "title": "GIF 생성",
        "subtitle": "상품 컷을 연결해 GIF를 생성합니다.",
    },
    "collector": {
        "name": "이미지 수집툴",
        "title": "이미지 수집툴",
        "subtitle": "기존 수집툴을 바로 실행합니다.",
    },
    "blog": {
        "name": "블로그 작성",
        "title": "블로그 작성",
        "subtitle": "상품 정보를 바탕으로 블로그 글 초안을 만듭니다.",
    },
    "shortform": {
        "name": "숏폼 메이커",
        "title": "숏폼 메이커",
        "subtitle": "릴스/쇼츠용 콘티와 카피 아이디어를 정리합니다.",
    },
}

IMAGE_COLLECTOR_URL = "https://misharp-image-crop-v1.streamlit.app/"

def _init_state():
    st.session_state.setdefault("page", "dashboard")
    st.session_state.setdefault("shortcuts", [])  # list[{title,url,emoji,created_at}]
    st.session_state.setdefault("memo_text", "")
    st.session_state.setdefault("todo_items", [])  # list[{text,done}]
    st.session_state.setdefault("todo_new", "")

def _valid_url(u: str) -> bool:
    try:
        p = urlparse(u.strip())
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def inject_css():
    st.markdown(
        """
        <style>
          /* overall */
          .block-container { padding-top: 2.0rem !important; padding-bottom: 2.5rem !important; }
          header[data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
          /* avoid top clipping on some embeds */
          section.main > div { padding-top: 0.25rem; }

          /* Sidebar brand button */
          div[data-testid="stSidebar"] .brand-btn button {
            width: 100%;
            font-weight: 800;
            letter-spacing: 0.5px;
            padding: 0.85rem 0.9rem !important;
            border-radius: 12px !important;
          }
          div[data-testid="stSidebar"] .brand-btn button:hover {
            filter: brightness(1.08);
            transform: translateY(-1px);
          }

          /* Title card */
          .title-card {
            border-radius: 18px;
            padding: 22px 24px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            margin-top: 8px;
            margin-bottom: 18px;
          }
          .title-card h1 { margin: 0 !important; line-height: 1.15; }
          .title-card p { margin: 10px 0 0 0 !important; opacity: 0.85; }

          /* Dashboard cards */
          .dash-card {
            border-radius: 16px;
            padding: 18px 18px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
          }
          .muted { opacity: 0.75; }
          .shortcut-grid a {
            text-decoration: none !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

def sidebar():
    with st.sidebar:
        st.markdown('<div class="brand-btn">', unsafe_allow_html=True)
        if st.button("MISHARP SELLER OS", use_container_width=True):
            st.session_state.page = "dashboard"
        st.markdown("</div>", unsafe_allow_html=True)

        st.caption(APP_TITLE)
        st.divider()

        # menu
        for key in ["dashboard","detail","thumb","gif","collector","blog","shortform"]:
            label = PAGES[key]["name"]
            is_active = (st.session_state.page == key)
            if st.button(("✅ " if is_active else "") + label, use_container_width=True):
                st.session_state.page = key

        st.divider()
        with st.expander("📦 내 대시보드 저장/복원", expanded=False):
            export = {
                "shortcuts": st.session_state.shortcuts,
                "memo_text": st.session_state.memo_text,
                "todo_items": st.session_state.todo_items,
                "exported_at": dt.datetime.now().isoformat(),
            }
            st.download_button(
                "현재 설정 JSON 다운로드",
                data=json.dumps(export, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name="misharp_dashboard_settings.json",
                mime="application/json",
                use_container_width=True,
            )
            up = st.file_uploader("JSON 업로드(복원)", type=["json"])
            if up is not None:
                try:
                    data = json.loads(up.read().decode("utf-8"))
                    st.session_state.shortcuts = data.get("shortcuts", []) or []
                    st.session_state.memo_text = data.get("memo_text", "") or ""
                    st.session_state.todo_items = data.get("todo_items", []) or []
                    st.success("복원 완료! 좌측 메뉴에서 대시보드로 돌아가 확인하세요.")
                except Exception as e:
                    st.error(f"복원 실패: {e}")

def title_area(page_key: str):
    meta = PAGES[page_key]
    st.markdown(
        f"""
        <div class="title-card">
          <h1>{meta["title"]}</h1>
          <p>{meta["subtitle"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def dashboard_page():
    title_area("dashboard")

    # Top date row (like a personal dashboard header)
    now = dt.datetime.now()
    weekday_kr = ["월","화","수","목","금","토","일"][now.weekday()]
    st.markdown(
        f"""
        <div class="dash-card">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
            <div>
              <div style="font-size:18px;font-weight:800;">{now.strftime('%Y.%m.%d')} ({weekday_kr})</div>
              <div class="muted" style="margin-top:4px;">오늘도 한 번에 정리하고, 빨리 끝내기.</div>
            </div>
            <div class="muted" style="font-weight:700;">{now.strftime('%p %I:%M')}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    col_l, col_r = st.columns([3.2, 2.0], gap="large")

    # Left: shortcuts
    with col_l:
        st.markdown("### 🔗 내 바로가기")
        with st.expander("➕ 바로가기 추가", expanded=True):
            c1, c2, c3 = st.columns([1.2, 3.2, 1.2], gap="small")
            with c1:
                emoji = st.text_input("아이콘", value="🔗", max_chars=2, help="예: 🛒 📦 📊 ✉️")
            with c2:
                title = st.text_input("이름", placeholder="예: 카페24 관리자 / 스마트스토어 / 카카오채널", max_chars=40)
            with c3:
                url = st.text_input("URL", placeholder="https://...", max_chars=300)

            add = st.button("바로가기 추가", type="primary", use_container_width=True)
            if add:
                if not title.strip():
                    st.warning("이름을 입력해주세요.")
                elif not _valid_url(url):
                    st.warning("URL 형식이 올바르지 않습니다. https:// 로 시작하는 주소를 넣어주세요.")
                else:
                    st.session_state.shortcuts.insert(0, {
                        "emoji": (emoji.strip() or "🔗")[:2],
                        "title": title.strip(),
                        "url": url.strip(),
                        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
                    })
                    st.success("추가 완료!")

        if not st.session_state.shortcuts:
            st.info("아직 바로가기가 없습니다. 위에서 추가해보세요.")
        else:
            # Render shortcuts list
            for i, sc in enumerate(st.session_state.shortcuts):
                box = st.container(border=True)
                with box:
                    cA, cB = st.columns([6.5, 3.5], vertical_alignment="center")
                    with cA:
                        st.markdown(f"**{sc.get('emoji','🔗')} {sc.get('title','')}**")
                        st.caption(sc.get("url",""))
                    with cB:
                        open_col, up_col, down_col, del_col = st.columns([2.3, 1, 1, 1])
                        with open_col:
                            st.link_button("열기", sc.get("url",""), use_container_width=True)
                        with up_col:
                            if st.button("↑", key=f"sc_up_{i}", use_container_width=True, help="위로"):
                                if i > 0:
                                    st.session_state.shortcuts[i-1], st.session_state.shortcuts[i] = st.session_state.shortcuts[i], st.session_state.shortcuts[i-1]
                                    st.rerun()
                        with down_col:
                            if st.button("↓", key=f"sc_dn_{i}", use_container_width=True, help="아래로"):
                                if i < len(st.session_state.shortcuts)-1:
                                    st.session_state.shortcuts[i+1], st.session_state.shortcuts[i] = st.session_state.shortcuts[i], st.session_state.shortcuts[i+1]
                                    st.rerun()
                        with del_col:
                            if st.button("✕", key=f"sc_del_{i}", use_container_width=True, help="삭제"):
                                st.session_state.shortcuts.pop(i)
                                st.rerun()

    # Right: memo + todos
    with col_r:
        st.markdown("### 📝 오늘의 메모")
        st.session_state.memo_text = st.text_area(
            "메모",
            value=st.session_state.memo_text,
            height=180,
            placeholder="오늘 처리할 것, 꼭 확인할 것, 아이디어 등을 적어두세요.",
            label_visibility="collapsed",
        )

        st.markdown("### ✅ 오늘의 할 일")
        new = st.text_input("할 일 추가", value=st.session_state.todo_new, placeholder="예: 신상 촬영컷 정리 / 배너 교체", label_visibility="collapsed")
        add_todo = st.button("추가", use_container_width=True)
        if add_todo and new.strip():
            st.session_state.todo_items.insert(0, {"text": new.strip(), "done": False})
            st.session_state.todo_new = ""
            st.rerun()

        if not st.session_state.todo_items:
            st.caption("할 일이 아직 없습니다.")
        else:
            for idx, item in enumerate(st.session_state.todo_items):
                row = st.columns([0.9, 5.1, 1.0, 1.0, 1.0], vertical_alignment="center")
                with row[0]:
                    done = st.checkbox("done", value=item.get("done", False), key=f"todo_done_{idx}", label_visibility="collapsed")
                    st.session_state.todo_items[idx]["done"] = done
                with row[1]:
                    txt = item.get("text","")
                    if done:
                        st.markdown(f"~~{txt}~~")
                    else:
                        st.markdown(txt)
                with row[2]:
                    if st.button("↑", key=f"todo_up_{idx}", use_container_width=True):
                        if idx > 0:
                            st.session_state.todo_items[idx-1], st.session_state.todo_items[idx] = st.session_state.todo_items[idx], st.session_state.todo_items[idx-1]
                            st.rerun()
                with row[3]:
                    if st.button("↓", key=f"todo_dn_{idx}", use_container_width=True):
                        if idx < len(st.session_state.todo_items)-1:
                            st.session_state.todo_items[idx+1], st.session_state.todo_items[idx] = st.session_state.todo_items[idx], st.session_state.todo_items[idx+1]
                            st.rerun()
                with row[4]:
                    if st.button("✕", key=f"todo_del_{idx}", use_container_width=True):
                        st.session_state.todo_items.pop(idx)
                        st.rerun()

        st.divider()
        st.caption("Tip) 좌측 사이드바에서 대시보드 설정을 JSON으로 저장해두면 다음에 그대로 복원 가능합니다.")

def placeholder_page(key: str):
    title_area(key)
    st.info("이 화면은 다음 단계에서 기능을 연결합니다. (현재는 UX/레이아웃 뼈대만 고정)")

def image_collector_page():
    title_area("collector")
    c1, c2 = st.columns([1,1])
    with c1:
        st.link_button("새 탭에서 열기", IMAGE_COLLECTOR_URL, use_container_width=True)
    with c2:
        st.caption("iframe이 막히는 환경이 있어, 새 탭 열기도 함께 제공합니다.")
    st.components.v1.iframe(IMAGE_COLLECTOR_URL, height=900, scrolling=True)

def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    _init_state()
    inject_css()
    sidebar()

    page = st.session_state.page

    if page == "dashboard":
        dashboard_page()
    elif page == "collector":
        image_collector_page()
    elif page in PAGES:
        placeholder_page(page)
    else:
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown(
        "<div style='opacity:.7;text-align:center;margin-top:26px;font-size:12px;'>© 2026 misharpcompany. All rights reserved.</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
