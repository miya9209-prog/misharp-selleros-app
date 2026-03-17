
import os, json, io, datetime, uuid, textwrap
import streamlit as st
import runpy
from pathlib import Path

APP_TITLE = "미샵 셀러 스튜디오 OS V1"

PAGES = [
    {"id": "dashboard", "label": "대시보드", "subtitle": "오늘 날짜/메모/할 일/바로가기를 한 화면에서 관리하세요.", "pro": False},
    {"id": "detailpage", "label": "상세페이지 생성", "subtitle": "이미지 업로드만 하면 상세페이지가 자동으로 완성됩니다.", "pro": False},
    {"id": "thumbnail", "label": "썸네일 생성", "subtitle": "규격에 맞게 자동 배치·텍스트 합성으로 썸네일을 만듭니다.", "pro": True},
    {"id": "gif", "label": "GIF 생성", "subtitle": "이미지/영상으로 상품 GIF를 빠르게 생성합니다.", "pro": True},
    {"id": "image_crop", "label": "이미지 추출 생성", "subtitle": "상품 이미지 크롭/추출 도구를 OS 안에 탑재했습니다.", "pro": True},
    {"id": "copy", "label": "상품설명 생성", "subtitle": "상품 특장점 기반으로 상세설명 문구를 자동 생성합니다.", "pro": True},
    {"id": "seo", "label": "SEO 생성", "subtitle": "상품 SEO 메타·키워드·설명문을 빠르게 생성합니다.", "pro": True},
    {"id": "blog", "label": "블로그 작성", "subtitle": "상품/키워드 기반으로 SEO 글 초안을 빠르게 만듭니다.", "pro": True},
    {"id": "shortform", "label": "숏폼 메이커", "subtitle": "릴스/숏츠용 후킹 스크립트·구성안을 빠르게 만듭니다.", "pro": True},
]

# PRO access codes (sha256 of the plain code).
VALID_CODE_HASHES = set([
    "02d59a23b827a146863fc956de2df1c891a616db7354b2359b6e0884953f2ab8",
    "0da36dbe23c8b8c695e1d318a3f9c46ae4ecd3c6d56ad8ef7d496d12ad06ca70",
    "14702adfcc03b5e377a280fa5ede65b53e668486e7456c3bd11d158dd64d9de2",
    "1c393314836c484e74ca7ba936cbe740ecc165bfd43ef022f227b8e330070b56",
    "25d5cc90e0823b13eacc2876fd6c3aa64de42332c0e95af62dacf9b715f0c26d",
    "26ed366b4c6eec70dbdaae69123bdc766341f0be3721c2ec3db0c10d1f00dccc",
    "2ed472bbe6847e106d87b107525d63f7379eaf712a6a9824d41a933593f6170e",
    "302778bfb024ef2e177d90bfcf523a1f53005b6ab477034dec4147c63d1d8c25",
    "33a9d3295bb34dff13bfd794da0b58c82d1dfa2adf41dfab918a40a4defbeb47",
    "3a36ff44ce8c7d1d98ebf28eadf109e8bc2b7e6a9e8d57dfdf48e4d74e855b43",
    "41e9bcf536ec0508ae321d1c51574122a938738a03ca754b402b29c50e8f66d4",
    "4750a0850e85769bf82fb113ec703b3bfb63639a038d332a994b7a37d6357488",
    "498494d17098d27a409ec2683e5504c191acc786b7d8a5fe3c77e4b698c9d189",
    "4a15a7e737f5b7736b6bb70c86f5b233e6c8774a9db4ca8046cb5f3b98935378",
    "4e34f0246fb251a0f71941a1f4b392dc8417661733a191c66d87b12c3ef5ca0e",
    "4e4686617e9cced252fa8b3a0efd128bd327075a4dfd1770710f12dc19206f0a",
    "510460d1a1b6be232af5133937e47e955ac8450f5848de0b616215783fa3331f",
    "602eef75d17ec0b696401b2600f6f53baddaccd18505a0f6ce78f785533c08be",
    "607cbe3b4ccc9594a188b7d9d16dc4738abcded3774a7cc0ed741366c0a0ad47",
    "633bab2837d341a0215f964e4a09af0329dea7f1d4ce8a33e0d52aeab29cbd11",
    "67439ad3e73e99e59637872eb7da529052b79d641cd4a052293e649f4e7eee78",
    "742e0c172d73c4afdc052027b752d74b6c49a2806c23ee126c1993c4ce148cd6",
    "748fce000ce903e5541f25030e4869fb9c1e47e39f9e226a54986a12f8da2946",
    "787d09b23c3e20b2b7d617babf4be728dbc8c072c28b9162c0d9d3647b209e12",
    "7987bbcfe7cdc28d3391e2b31196eb1718d49671140bef1eb5ef39e9b2373182",
    "7cf5fc0bd51c4edd7e33a1b8e79ef1cad18f99e063bd0b6fee89c572842409a0",
    "8224cc53bc2a20587376d654ec2bdd09e458fb7751e8651fadc0cbb9045dd7c8",
    "879b460c71ad3407b5da08f93a76f2a66c44db9b621fc01578f27d6ea7b69f7e",
    "8e6d5056763ab2b10748b6bcb9d95a19dea425f761c2278e6934b06d11fd663b",
    "9113272e480dec5f0ecee89f6bef5ca8248dd2ec54ae92288b9a925699e0cee1",
    "934f46f787fbcbc6b25f69fd1b5f367bdd778b4528f1dc0b3634ec130f82ed4e",
    "9770cd0d39c44a2daa7609dac0aa1d398db19db4a7779271f4f390f64985a9f6",
    "9b4e1c08e888d9a6681428913201d8f8e0596a307929345fb3ed1104048f82f8",
    "a7821b6889e797b7419c7ecd4a73be2ceb510bc5c4ba051aa8fd9b70731231db",
    "a7f1e6755a99dd413eda944ce93b88e06ffcdc11620d479412bae53c909b5fda",
    "b869513d194c3b72522294e8043744f100c2fc5800a535b70fe57647bf988182",
    "cf3f334249240966d67b3197938b04211660fb7b08b3b4b2193fc40ed544511e",
    "d2ed7e7500f69140b83e0c46a6183370dce13c9512ba0e942214428d3224a689",
    "d6ca4e044c957440a62e17fb3a16522e699dafaaf8c147d9dca83e66130ad51c",
    "dd1f82df77258d73134f67f3e5b09f5fab3a0a90257152fc58f8dca1e8ce42a0",
    "ddca47d1b026d84dce815f703ba11615dc5d7a37c661bf5c20c5944728b17e25",
    "ddcf07183a44b6608e4c384453137f941e8c514ad1cdf9f85a27c6dc5e77e761",
    "deaf76e2e3fa015966faae337543198f9b3c900020e97bdcf914562eb7670432",
    "e06807c54da24e54ad757f3609d8d1125130cf8ded55bd64df884706fc52833b",
    "e1ee1fcddce542ebdc5f98dec194bc6fd49c861301355f48a3c1d94c5e66d0b9",
    "e5f43cf77c594c4b490b40f139c465b2357278c5ee28d16f88e1ad07d5b40652",
    "f474b2d8627c66b3944a3ef91c619a0a0ab62c6f8a0c5c483fbfb22add3b9846",
    "f4b0ae6b12a0f82ea0642b963bd92dcdc84f667bfa257e76bd61dfa67052ddac",
    "f8a60e4f233cd032b7d1ec3fe3794471a10adfadf8e027767f0ed436d1b71e91",
    "fef725c3aca9d9c2d7cf75464b5efcb94fc3f2d05c0f4ee13a8592be04a13a87",
])

PRO_PAGE_IDS = {p['id'] for p in PAGES if p.get('pro')}
PAGE_META = {p['id']: (p['label'], p.get('subtitle','')) for p in PAGES}

if 'dash_shortcuts' not in st.session_state:
    st.session_state['dash_shortcuts'] = []


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

.ms-shortcut-card .stLinkButton, .ms-shortcut-card .stLinkButton > a { width:100% !important; }
.ms-shortcut-card a {
  display:flex !important; align-items:center !important; justify-content:center !important;
  min-height:42px !important;
  border-radius:10px !important;
  border:1px solid rgba(255,255,255,0.14) !important;
  background:rgba(255,255,255,0.02) !important;
  color:rgba(255,255,255,0.95) !important;
  text-decoration:none !important;
  font-weight:700 !important;
}
.ms-shortcut-card a:hover { background:rgba(255,255,255,0.08) !important; }

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def set_page(page_key: str):
    st.session_state["page"] = page_key

def get_page():
    # Prefer query param (for sidebar HTML links), fall back to session state.
    qp = st.query_params.get('page', None)
    if isinstance(qp, list):
        qp = qp[0] if qp else None
    page = (qp or st.session_state.get('page') or 'dashboard').strip()
    valid_ids = {p['id'] for p in PAGES}
    if page not in valid_ids:
        page = 'dashboard'
    st.session_state['page'] = page
    return page

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
    """Load an embedded tool from apps/<app_key>/app.py (in-place)."""
    import importlib.util
    import sys

    repo_root = os.path.dirname(__file__)
    apps_root = os.path.join(repo_root, "apps")
    base = os.path.join(apps_root, app_key)
    target = os.path.join(base, "app.py")

    if not os.path.exists(target):
        st.error(f"앱 파일을 찾을 수 없습니다: {target}")
        return

    old_sys_path = list(sys.path)
    for p in (base, apps_root, repo_root):
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        nonce = st.session_state.get("nav_nonce", 0)
        mod_name = f"mso_{app_key}_{nonce}"
        spec = importlib.util.spec_from_file_location(mod_name, target)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        if hasattr(module, "render") and callable(getattr(module, "render")):
            module.render()
        elif hasattr(module, "main") and callable(getattr(module, "main")):
            module.main()
        elif hasattr(module, "app") and callable(getattr(module, "app")):
            module.app()
        else:
            st.warning(f"{app_key} 앱에서 실행 가능한 진입점(render/main/app)을 찾지 못했습니다.")
    except Exception as e:
        st.error(f"앱 실행 중 오류: {e}")
    finally:
        sys.path = old_sys_path

# -----------------------------
# Sidebar Navigation
# -----------------------------
with st.sidebar:
    st.sidebar.markdown(
        textwrap.dedent("""
        <style>
        .mso-brand-link{
            display:block;
            text-decoration:none !important;
            color:#EDEDED !important;
            font-weight:900 !important;
            font-size:36px !important;
            letter-spacing:0.6px !important;
            line-height:1.05;
            margin:6px 0 18px 0;
            white-space:pre-line;
        }
        .mso-nav-wrap{
            display:flex;
            flex-direction:column;
            gap:10px;
            margin-top:8px;
            margin-bottom:72px;
        }
        .mso-nav-item{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:10px;
            text-decoration:none !important;
            border:1px solid rgba(255,255,255,0.10);
            border-radius:10px;
            padding:12px 14px;
            background:rgba(255,255,255,0.02);
            color:#EDEDED !important;
            transition:all .15s ease;
        }
        .mso-nav-item:hover{
            background:rgba(255,255,255,0.06);
            border-color:rgba(255,255,255,0.18);
        }
        .mso-nav-item.active{
            background:#ffffff !important;
            color:#0d1522 !important;
            border-color:#ffffff !important;
            margin-bottom:8px;
        }
        .mso-nav-label{
            flex:1;
            text-align:left;
            font-weight:600;
            font-size:15px;
            line-height:1.2;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }
        .mso-badge{
            display:inline-flex;
            align-items:center;
            justify-content:center;
            min-width:34px;
            height:18px;
            font-size:9px;
            font-weight:600;
            color:white;
            padding:0 6px;
            border-radius:6px;
            line-height:1;
            white-space:nowrap;
            flex-shrink:0;
        }
        .mso-badge.pro{background:#ff4d4f;}
        .mso-badge.free{background:#2ecc71;}
        .mso-sidebar-footer{
            position:fixed;left:0;bottom:0;width:300px;
            padding:12px 12px 10px 12px;color:rgba(255,255,255,0.45);
            font-size:11px;border-top:1px solid rgba(255,255,255,0.08);
            background:rgba(15,18,24,0.92);backdrop-filter: blur(8px);
        }
        </style>
        """),
        unsafe_allow_html=True,
    )

    current_page = get_page()

    st.sidebar.markdown(
        '<a class="mso-brand-link" href="?page=dashboard">MISHARP SELLER OS</a>',
        unsafe_allow_html=True
    )

    if st.session_state.get('pro_authed', False):
        st.sidebar.success('PRO 사용 가능')
        if st.sidebar.button('로그아웃', key='pro_logout', use_container_width=True):
            st.session_state['pro_authed'] = False
            st.toast('로그아웃 되었습니다.')
            st.rerun()
    else:
        code = st.sidebar.text_input('PRO 로그인 코드', type='password', key='pro_code_input')
        if st.sidebar.button('로그인', key='pro_login', use_container_width=True):
            import hashlib
            c = (code or '').strip()
            h = hashlib.sha256(c.encode('utf-8')).hexdigest()
            if h in VALID_CODE_HASHES:
                st.session_state['pro_authed'] = True
                st.rerun()
            else:
                st.sidebar.error('코드가 올바르지 않습니다.')

    st.sidebar.markdown('---')

    nav_parts = ['<div class="mso-nav-wrap">']
    for p in PAGES:
        pid = p['id']
        active_cls = 'active' if pid == current_page else ''
        badge_text = 'PRO' if p.get('pro', False) else 'FREE'
        badge_cls = 'pro' if p.get('pro', False) else 'free'
        nav_parts.append(
            f'<a class="mso-nav-item {active_cls}" href="?page={pid}">'
            f'<span class="mso-nav-label">{p["label"]}</span>'
            f'<span class="mso-badge {badge_cls}">{badge_text}</span>'
            f'</a>'
        )
    nav_parts.append('</div>')
    st.sidebar.markdown("".join(nav_parts), unsafe_allow_html=True)

    st.sidebar.markdown(
        '<div class="mso-sidebar-footer">© 2026 misharpcompany. All rights reserved.</div>',
        unsafe_allow_html=True,
    )
# -----------------------------
# Dashboard (personal)
# -----------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_weather_seoul_daily():
    from urllib.request import urlopen
    lat, lon = 37.5665, 126.9780
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&daily=weathercode,temperature_2m_max,temperature_2m_min"
        "&timezone=Asia%2FSeoul"
    )
    try:
        with urlopen(url, timeout=6) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return None

    daily = (data or {}).get("daily") or {}
    codes = daily.get("weathercode") or []
    tmaxs = daily.get("temperature_2m_max") or []
    tmins = daily.get("temperature_2m_min") or []
    if not codes or not tmaxs or not tmins:
        return None

    code = int(codes[0])
    tmax = round(float(tmaxs[0]))
    tmin = round(float(tmins[0]))

    if code == 0:
        desc = "맑음"
    elif code in (1, 2, 3):
        desc = "흐림"
    elif code in (45, 48):
        desc = "안개"
    elif 71 <= code <= 77:
        desc = "눈"
    elif 95 <= code <= 99:
        desc = "뇌우"
    elif 80 <= code <= 82:
        desc = "소나기"
    elif 51 <= code <= 67:
        desc = "비"
    else:
        desc = "흐림"

    return desc, tmax, tmin


def dashboard():
    import uuid
    from datetime import datetime

    if "dash_shortcuts" not in st.session_state:
        st.session_state.dash_shortcuts = [
            {"id": str(uuid.uuid4()), "title": "미샵 관리자", "url": "https://misharp.co.kr", "emoji": ""},
            {"id": str(uuid.uuid4()), "title": "카페24 관리자", "url": "https://eclogin.cafe24.com/Shop/", "emoji": ""},
        ]
    if "dash_memo" not in st.session_state:
        st.session_state.dash_memo = ""
    if "dash_todos" not in st.session_state:
        st.session_state.dash_todos = []

    def _valid_url(url: str) -> bool:
        url = (url or "").strip()
        return url.startswith("http://") or url.startswith("https://")

    c1, c2, c3 = st.columns([1.1, 2.2, 2.2], gap="large")

    with c1:
        now = datetime.now()
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        dow_ko = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
        st.markdown("### 오늘")
        st.markdown(f"**{now.strftime('%Y-%m-%d')}({dow_ko}) {now.strftime('%H:%M')}**")
        w = _fetch_weather_seoul_daily()
        if w:
            desc, tmax, tmin = w
            st.caption(f"{desc}  {tmax}° / {tmin}°")
        else:
            st.caption("날씨 정보를 불러오지 못했어요.")
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
            new_todo = st.text_input(
                "할일 추가",
                "",
                placeholder="예) 상세페이지 3개 생성",
                label_visibility="collapsed",
            )
        with add_cols[1]:
            add_clicked = st.button("추가", key="todo_add", use_container_width=True)

        if add_clicked and new_todo.strip():
            st.session_state.dash_todos.append(
                {"id": str(uuid.uuid4()), "text": new_todo.strip(), "done": False}
            )
            st.rerun()

        remove_ids = []
        for item in st.session_state.dash_todos:
            row = st.columns([0.12, 0.74, 0.14])
            item["done"] = row[0].checkbox(
                "",
                value=item.get("done", False),
                key=f"todo_done_{item['id']}"
            )
            row[1].markdown(item["text"])
            if row[2].button("삭제", key=f"todo_del_{item['id']}"):
                remove_ids.append(item["id"])

        if remove_ids:
            st.session_state.dash_todos = [
                t for t in st.session_state.dash_todos if t["id"] not in remove_ids
            ]
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown("### 바로가기")

    shortcuts = st.session_state.dash_shortcuts
    if not shortcuts:
        st.info("아직 바로가기가 없습니다. 아래에서 추가해보세요.")
    else:
        cols = st.columns(4, gap="medium")
        for i, sc in enumerate(shortcuts):
            with cols[i % 4]:
                st.markdown('<div class="ms-shortcut-card">', unsafe_allow_html=True)
                st.link_button(sc.get("title", "바로가기"), sc.get("url", ""), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    with st.expander("바로가기 추가/편집", expanded=False):
        st.markdown("**새 바로가기 추가**")

        h = st.columns([2.2, 4.0, 1.2], gap="small")
        h[0].markdown("제목")
        h[1].markdown("URL")
        h[2].markdown("&nbsp;", unsafe_allow_html=True)

        row = st.columns([2.2, 4.0, 1.2], gap="small")
        title = row[0].text_input(
            "", "", key="sc_add_title",
            placeholder="예) 미샵 관리자",
            label_visibility="collapsed",
        )
        url = row[1].text_input(
            "", "", key="sc_add_url",
            placeholder="https://",
            label_visibility="collapsed",
        )
        row[2].markdown("<div style='height:27px'></div>", unsafe_allow_html=True)

        if row[2].button("추가", key="shortcut_add", use_container_width=True):
            if not title.strip():
                st.error("제목을 입력해 주세요.")
            elif not _valid_url(url):
                st.error("URL은 http:// 또는 https:// 로 시작해야 합니다.")
            else:
                st.session_state.dash_shortcuts.append(
                    {"id": str(uuid.uuid4()), "title": title.strip(), "url": url.strip(), "emoji": ""}
                )
                st.success("추가되었습니다.")
                st.rerun()

        st.divider()
        st.markdown("**기존 바로가기 관리**")
        for sc in list(st.session_state.dash_shortcuts):
            row = st.columns([2.2, 4.2, 1.2], gap="small")
            new_title = row[0].text_input(
                "제목", sc.get("title", ""),
                key=f"sc_title_{sc['id']}",
                label_visibility="collapsed",
            )
            new_url = row[1].text_input(
                "URL", sc.get("url", ""),
                key=f"sc_url_{sc['id']}",
                label_visibility="collapsed",
            )
            if row[2].button("삭제", key=f"sc_rm_{sc['id']}", use_container_width=True):
                st.session_state.dash_shortcuts = [
                    x for x in st.session_state.dash_shortcuts if x["id"] != sc["id"]
                ]
                st.rerun()
            sc["title"] = new_title
            sc["url"] = new_url

    st.markdown("</div>", unsafe_allow_html=True)

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
                st.link_button(sc.get("title", "바로가기"), sc.get("url", ""), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)




def render_copy_page():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown("### 상품 핵심 정보 입력")
    c1, c2 = st.columns(2, gap="medium")
    product_name = c1.text_input("상품명", key="copy_product_name", placeholder="예) 몬트 A라인 사파리 자켓")
    target = c2.text_input("타겟 고객", key="copy_target", placeholder="예) 4050 여성 / 출근룩 / 체형커버")
    c3, c4 = st.columns(2, gap="medium")
    tone = c3.selectbox("문체", ["전문적이지만 대중적인 말투", "친근한 판매형 말투", "차분한 프리미엄 말투"], key="copy_tone")
    use_case = c4.text_input("추천 상황", key="copy_use_case", placeholder="예) 출근룩, 학모룩, 주말모임")
    points = st.text_area(
        "핵심 포인트",
        key="copy_points",
        height=160,
        placeholder="예)\n- 원단이 부드럽고 관리가 편함\n- 군살 커버되는 여유핏\n- 슬랙스/스커트 모두 매칭 쉬움",
    )
    banned = st.text_input("금칙어/제외어", key="copy_banned", placeholder="예) 최저가, 무조건, 완벽")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    if st.button("상품설명 생성", key="generate_copy", use_container_width=True):
        bullets = [x.strip('-• ').strip() for x in points.splitlines() if x.strip()]
        if not product_name.strip() or not bullets:
            st.error("상품명과 핵심 포인트를 입력해 주세요.")
        else:
            reason = bullets[0] if len(bullets) > 0 else "상품 강점"
            fabric = bullets[1] if len(bullets) > 1 else bullets[0]
            fit = bullets[2] if len(bullets) > 2 else bullets[-1]
            styling = bullets[3] if len(bullets) > 3 else (use_case or "데일리 스타일링")
            banned_text = banned.strip() or "없음"
            result = (
                f"{product_name}\n"
                f"[이 상품을 초이스한 이유입니다.]\n"
                f"{product_name}는 {reason}에 집중해 선택한 아이템입니다.\n"
                f"{target or '미샵 고객'}에게 특히 잘 맞는 포인트를 중심으로\n"
                f"실제로 손이 자주 가는 상품 설명이 되도록 정리했습니다.\n\n"
                f"[원단을 가장 먼저 봅니다.]\n"
                f"{product_name}는 {fabric} 강점이 돋보입니다.\n"
                f"사진만으로는 잘 보이지 않는 착용감과 관리 편의성까지\n"
                f"구매 전 바로 이해할 수 있게 전달하는 데 초점을 맞췄습니다.\n\n"
                f"[체형과 핏에 대하여]\n"
                f"{fit} 느낌을 중심으로\n"
                f"부담 없이 입기 좋고, 과하게 꾸민 느낌 없이\n"
                f"단정하고 세련된 인상을 주도록 설명하면 좋습니다.\n\n"
                f"[이렇게 활용해 보세요.]\n"
                f"{styling} 상황에 자연스럽게 연결해 제안하면 전환율에 유리합니다.\n"
                f"문체 가이드: {tone}\n"
                f"금칙어: {banned_text}\n"
            )
            st.session_state['generated_copy_text'] = result
            st.session_state['generated_copy_meta'] = {
                'product_name': product_name,
                'target': target,
                'tone': tone,
                'use_case': use_case,
                'banned': banned_text,
            }

    if st.session_state.get('generated_copy_text'):
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown("### 생성 결과")
        st.text_area("생성 결과", value=st.session_state['generated_copy_text'], height=420, key="copy_result_box")
        st.download_button(
            "TXT 다운로드",
            data=st.session_state['generated_copy_text'].encode('utf-8'),
            file_name=f"copy_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="copy_download",
        )
        st.markdown("</div>", unsafe_allow_html=True)


def render_shortform_page():
    st.markdown('<div class="ms-card">', unsafe_allow_html=True)
    st.markdown("### 숏폼 기획 입력")
    c1, c2 = st.columns(2, gap="medium")
    product_name = c1.text_input("상품명", key="sf_product_name", placeholder="예) 어반 실버 포인트 긴팔 셔츠")
    audience = c2.text_input("타겟", key="sf_audience", placeholder="예) 4050 여성 / 출근룩 / 학교방문룩")
    c3, c4 = st.columns(2, gap="medium")
    angle = c3.text_input("콘텐츠 각도", key="sf_angle", placeholder="예) 첫인상 좋아 보이는 코디")
    duration = c4.selectbox("길이", ["15초", "20초", "30초"], key="sf_duration")
    features = st.text_area(
        "핵심 포인트",
        key="sf_features",
        height=160,
        placeholder="예)\n- 차르르 흐르는 실키 터치감\n- 군살 커버되는 여유핏\n- 단정하면서도 세련된 분위기",
    )
    cta = st.text_input("마무리 CTA", key="sf_cta", placeholder="예) 지금 미샵에서 만나보세요")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    if st.button("숏폼 구성 생성", key="generate_shortform", use_container_width=True):
        pts = [x.strip('-• ').strip() for x in features.splitlines() if x.strip()]
        if not product_name.strip() or not pts:
            st.error("상품명과 핵심 포인트를 입력해 주세요.")
        else:
            hook = angle.strip() or f"{product_name} 코디 포인트"
            p1 = pts[0]
            p2 = pts[1] if len(pts) > 1 else pts[0]
            p3 = pts[2] if len(pts) > 2 else pts[-1]
            result = (
                f"헤드라인 : {hook}\n\n"
                f"오프닝\n{audience or '이런 코디 고민 있으셨죠'}\n\n"
                f"본문 1\n{product_name}\n{p1}\n\n"
                f"본문 2\n{p2}\n\n"
                f"본문 3\n{p3}\n\n"
                f"클로징\n{cta or '지금 미샵에서 만나보세요'}\n\n"
                f"추천 자막 흐름 ({duration})\n"
                f"1. 고민 제시\n2. 상품 포인트 1\n3. 상품 포인트 2\n4. 스타일링/상황 제안\n5. CTA\n\n"
                f"추천 해시태그\n#미샵 #{product_name.replace(' ', '')} #4050여성코디 #데일리룩 #중년패션\n"
            )
            st.session_state['generated_shortform_text'] = result

    if st.session_state.get('generated_shortform_text'):
        st.markdown('<div class="ms-card">', unsafe_allow_html=True)
        st.markdown("### 생성 결과")
        st.text_area("생성 결과", value=st.session_state['generated_shortform_text'], height=420, key="shortform_result_box")
        st.download_button(
            "TXT 다운로드",
            data=st.session_state['generated_shortform_text'].encode('utf-8'),
            file_name=f"shortform_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="shortform_download",
        )
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Pages
page = st.session_state.get('page') or get_page()
st.session_state['page'] = page

# Header (title + one-line description)
title, subtitle = PAGE_META.get(page, ('', ''))
header(title, subtitle)

# PRO gate
if page in PRO_PAGE_IDS and not st.session_state.get('pro_authed', False):
    st.warning('이 기능은 **PRO 전용**입니다. 좌측 사이드바에서 로그인 코드를 입력해 잠금 해제해 주세요.')
    st.stop()


if page == 'dashboard':
    dashboard()
elif page == 'detailpage':
    run_embedded_app('detailpage')
elif page == 'thumbnail':
    run_embedded_app('thumbnail')
elif page == 'gif':
    run_embedded_app('gif')
elif page == 'image_crop':
    run_embedded_app('image_crop')
elif page == 'copy':
    render_copy_page()
elif page == 'seo':
    run_embedded_app('seo')
elif page == 'blog':
    run_embedded_app('blog')
elif page == 'shortform':
    render_shortform_page()
else:
    st.info('준비 중인 페이지입니다.')

