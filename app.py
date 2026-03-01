import json

import streamlit as st
import streamlit.components.v1 as components

from modules import blog, detail_page, gif_maker, thumbnail

# ============================================================
# MISHARP SELLER OS v1 (Streamlit)
# - Sidebar: list tools
# - Main: dynamic title/subtitle per tool
# - Dashboard: user can create shortcuts (session-based + JSON import/export)
# - Collector: embeds existing external Streamlit app via iframe
# ============================================================

APP_BRAND = "MISHARP SELLER OS"
APP_TITLE_DEFAULT = "미샵 셀러 스튜디오 OS v1"

COLLECTOR_URL = "https://misharp-image-crop-v1.streamlit.app/"


PAGES = [
    ("대시보드", "dashboard", "오늘 필요한 생성기만 골라, 바로가기로 묶어두세요."),
    ("상세페이지 생성", "detail", "상품 이미지만 올리면, 상세페이지 이미지 자동 생성."),
    ("원고 생성", "copy", "상품 특장점 기반으로 상세페이지 원고를 빠르게 뽑아드립니다."),
    ("썸네일 생성", "thumb", "썸네일 규격에 맞춰 자동 배치·텍스트 합성."),
    ("GIF 생성", "gif", "이미지/컷을 이어 GIF로 만들고 홍보용으로 바로 저장."),
    ("이미지 수집툴", "collector", "상세페이지 URL 이미지 수집·정리(기존 툴 연동)."),
    ("블로그 작성", "blog", "상품 정보 기반으로 블로그 글/구성 자동 생성."),
    ("숏폼 메이커", "shortform", "릴스/쇼츠용 훅·콘티·자막 아이디어 생성."),
]

PAGE_BY_KEY = {k: {"label": l, "title": l, "subtitle": s} for (l, k, s) in PAGES}


def _init_state() -> None:
    st.session_state.setdefault("page", "dashboard")
    st.session_state.setdefault("selleros_shortcuts", ["detail", "thumb", "gif", "blog"])


def _get_query_page() -> str | None:
    """Read ?page=... from query params (supports both old/new Streamlit APIs)."""
    try:
        qp = st.query_params
        v = qp.get("page")
        if isinstance(v, list):
            return v[0] if v else None
        return v
    except Exception:
        qp = st.experimental_get_query_params()
        v = qp.get("page")
        return v[0] if v else None


def _set_query_page(page_key: str) -> None:
    try:
        st.query_params["page"] = page_key
    except Exception:
        st.experimental_set_query_params(page=page_key)


def _goto(page_key: str) -> None:
    st.session_state["page"] = page_key
    _set_query_page(page_key)
    st.rerun()


def inject_css() -> None:
    st.markdown(
        """
<style>
/* ---- page layout ---- */
.block-container { padding-top: 1.2rem; padding-bottom: 3.2rem; }

/* ---- hero ---- */
.misharp-hero {
  border-radius: 18px;
  padding: 26px 28px;
  margin: 0 0 14px 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.10);
}
.misharp-hero h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.15;
  letter-spacing: -0.2px;
}
.misharp-hero p {
  margin: 10px 0 0 0;
  color: rgba(255,255,255,0.80);
  font-size: 14px;
}

/* ---- cards ---- */
.misharp-card {
  border-radius: 18px;
  padding: 18px 18px;
  background: rgba(255,255,255,0.035);
  border: 1px solid rgba(255,255,255,0.08);
}
.misharp-h {
  font-size: 16px;
  font-weight: 800;
  margin: 0 0 10px 0;
}
.misharp-muted { color: rgba(255,255,255,0.75); }

/* ---- sidebar ---- */
section[data-testid="stSidebar"] { background: rgba(0,0,0,0.42); border-right: 1px solid rgba(255,255,255,0.08); }
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color: rgba(255,255,255,0.92); }

a.misharp-brand {
  display: inline-block;
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0.3px;
  color: rgba(255,255,255,0.95) !important;
  text-decoration: none !important;
  padding: 8px 10px;
  border-radius: 12px;
  margin-bottom: 4px;
}
a.misharp-brand:hover { background: rgba(255,255,255,0.10); }

/* ---- buttons ---- */
div.stButton > button {
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.05);
}
div.stButton > button:hover {
  border: 1px solid rgba(255,255,255,0.26);
  background: rgba(255,255,255,0.08);
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
<div class="misharp-hero">
  <h1>{title}</h1>
  <p>{subtitle}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_top_actions() -> None:
    c1, c2, c3 = st.columns([1.2, 1.2, 1.6])
    with c1:
        st.button("입력 초기화", use_container_width=True)
    with c2:
        st.button("전체 패키지 ZIP 다운로드", use_container_width=True)
    with c3:
        st.caption("※ 이 버튼들은 기능 개발 단계에서 하나씩 연결합니다.")


def render_dashboard() -> None:
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">사용자 바로가기(대시보드)</div>', unsafe_allow_html=True)
    st.caption("원하는 생성기만 골라 대시보드에 고정해두고, 클릭 한 번으로 이동하세요.")

    shortcuts: list[str] = st.session_state.get("selleros_shortcuts", [])
    available = [k for (_, k, _) in PAGES if k != "dashboard"]

    a1, a2, a3 = st.columns([2, 1, 1])
    with a1:
        add_key = st.selectbox(
            "추가할 생성기",
            options=available,
            format_func=lambda k: PAGE_BY_KEY.get(k, {}).get("label", k),
        )
    with a2:
        if st.button("추가", use_container_width=True):
            if add_key not in shortcuts:
                shortcuts.append(add_key)
                st.session_state["selleros_shortcuts"] = shortcuts
                st.toast("추가 완료")
            else:
                st.toast("이미 추가된 항목입니다")
    with a3:
        if st.button("기본값", use_container_width=True):
            st.session_state["selleros_shortcuts"] = ["detail", "thumb", "gif", "blog"]
            st.toast("기본 구성으로 복원")

    st.write("")

    if not shortcuts:
        st.info("아직 바로가기가 없습니다. 위에서 생성기를 추가해보세요.")
    else:
        cols = st.columns(2)
        for i, key in enumerate(shortcuts):
            meta = PAGE_BY_KEY.get(key, {"title": key, "subtitle": ""})
            col = cols[i % 2]
            with col:
                st.markdown(
                    f"""
<div class="misharp-card" style="margin-bottom: 14px;">
  <div class="misharp-h" style="margin-bottom: 6px;">{meta['title']}</div>
  <div class="misharp-muted" style="margin-bottom: 12px; font-size: 13px;">{meta['subtitle']}</div>
</div>
                    """,
                    unsafe_allow_html=True,
                )

                b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
                with b1:
                    if st.button("열기", key=f"open_{key}_{i}", use_container_width=True):
                        _goto(key)
                with b2:
                    if st.button("▲", key=f"up_{key}_{i}", use_container_width=True, disabled=(i == 0)):
                        shortcuts[i - 1], shortcuts[i] = shortcuts[i], shortcuts[i - 1]
                        st.session_state["selleros_shortcuts"] = shortcuts
                        st.rerun()
                with b3:
                    if st.button("▼", key=f"down_{key}_{i}", use_container_width=True, disabled=(i == len(shortcuts) - 1)):
                        shortcuts[i + 1], shortcuts[i] = shortcuts[i], shortcuts[i + 1]
                        st.session_state["selleros_shortcuts"] = shortcuts
                        st.rerun()
                with b4:
                    if st.button("삭제", key=f"del_{key}_{i}", use_container_width=True):
                        shortcuts.pop(i)
                        st.session_state["selleros_shortcuts"] = shortcuts
                        st.rerun()

    st.write("")
    st.markdown("---")

    ie1, ie2 = st.columns(2)
    with ie1:
        payload = json.dumps({"shortcuts": st.session_state.get("selleros_shortcuts", [])}, ensure_ascii=False, indent=2)
        st.download_button(
            "바로가기 JSON 다운로드",
            data=payload.encode("utf-8"),
            file_name="misharp_selleros_shortcuts.json",
            mime="application/json",
            use_container_width=True,
        )
    with ie2:
        up = st.file_uploader("바로가기 JSON 업로드", type=["json"], label_visibility="collapsed")
        if up is not None:
            try:
                data = json.loads(up.read().decode("utf-8"))
                items = data.get("shortcuts", [])
                valid = [k for (_, k, _) in PAGES]
                items = [x for x in items if x in valid]
                st.session_state["selleros_shortcuts"] = items
                st.success("업로드 완료")
            except Exception:
                st.error("JSON 형식이 올바르지 않습니다.")

    st.markdown('</div>', unsafe_allow_html=True)


def render_detail() -> None:
    detail_page.render({})


def render_thumb() -> None:
    thumbnail.render({})


def render_gif() -> None:
    gif_maker.render({})


def render_blog() -> None:
    blog.render({})


def render_copy() -> None:
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">원고 생성 (준비중)</div>', unsafe_allow_html=True)
    st.info("다음 단계에서 ‘원고 생성기’ 모듈을 붙이겠습니다. (현재는 UI/구조만 정리)")
    st.markdown('</div>', unsafe_allow_html=True)


def render_shortform() -> None:
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">숏폼 메이커 (준비중)</div>', unsafe_allow_html=True)
    st.info("다음 단계에서 ‘숏폼 메이커’ 모듈을 붙이겠습니다. (현재는 UI/구조만 정리)")
    st.markdown('</div>', unsafe_allow_html=True)


def render_collector() -> None:
    st.markdown('<div class="misharp-card">', unsafe_allow_html=True)
    st.markdown('<div class="misharp-h">이미지 수집툴</div>', unsafe_allow_html=True)
    st.caption("기존에 만들어둔 이미지 수집/크롭 툴을 이 화면에서 바로 열어 사용합니다.")

    st.link_button("새 탭에서 열기", COLLECTOR_URL, use_container_width=True)
    st.write("")

    components.html(
        f"""
<iframe src="{COLLECTOR_URL}" style="width:100%; height:820px; border:0; border-radius:16px; background:#0b1220;"></iframe>
        """,
        height=840,
    )
    st.markdown('</div>', unsafe_allow_html=True)


RENDERERS = {
    "dashboard": render_dashboard,
    "detail": render_detail,
    "copy": render_copy,
    "thumb": render_thumb,
    "gif": render_gif,
    "collector": render_collector,
    "blog": render_blog,
    "shortform": render_shortform,
}


def sidebar_nav() -> str:
    st.sidebar.markdown(
        f'<a class="misharp-brand" href="?page=dashboard">{APP_BRAND}</a>',
        unsafe_allow_html=True,
    )
    st.sidebar.caption("클릭하면 인덱스(대시보드)로 이동")

    labels = [x[0] for x in PAGES]
    keys = [x[1] for x in PAGES]

    qp_page = _get_query_page()
    if qp_page in keys:
        st.session_state["page"] = qp_page

    current = st.session_state.get("page", "dashboard")
    index = keys.index(current) if current in keys else 0

    choice = st.sidebar.radio("생성기", labels, index=index)
    page_key = keys[labels.index(choice)]

    if page_key != st.session_state.get("page"):
        st.session_state["page"] = page_key
        _set_query_page(page_key)

    st.sidebar.markdown("---")
    st.sidebar.caption("※ 공통 입력폼은 제거했습니다. 각 생성기는 독립적으로 빠르게 개발합니다.")
    return page_key


def render_footer() -> None:
    st.markdown(
        """
<div style="margin-top:24px; opacity:0.7; font-size:12px;">
  © 2026 misharpcompany. All rights reserved.
</div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE_DEFAULT, page_icon="🧩", layout="wide")
    _init_state()
    inject_css()

    page_key = sidebar_nav()
    meta = PAGE_BY_KEY.get(page_key, {"title": APP_TITLE_DEFAULT, "subtitle": ""})
    render_hero(meta.get("title", APP_TITLE_DEFAULT), meta.get("subtitle", ""))

    st.write("")
    render_top_actions()
    st.write("")

    renderer = RENDERERS.get(page_key)
    if renderer:
        renderer()
    else:
        st.warning("해당 메뉴는 아직 준비 중입니다.")

    render_footer()


if __name__ == "__main__":
    main()
