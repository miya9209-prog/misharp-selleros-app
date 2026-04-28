import os, json, io, datetime, uuid, textwrap
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

APP_TITLE = "미샵 셀러 스튜디오 OS"
APP_DOMAIN = "misharp-selleros.com"
APP_COPYRIGHT = "© 2026 misharpcompany. All rights reserved."

PAGES = [
    {"id": "dashboard", "group": "대시보드", "label": "대시보드", "subtitle": "오늘 날짜, 메모, 할 일, 바로가기를 한 화면에서 관리하세요.", "pro": False},

    {"id": "page_builder", "group": "상세페이지 제작", "label": "기획/작성", "subtitle": "최신 페이지빌더로 상세페이지 기획과 상품 설명 원고를 작업합니다.", "pro": True},
    {"id": "template_os", "group": "상세페이지 제작", "label": "템플릿 작업", "subtitle": "재사용 가능한 템플릿 제작과 편집 작업을 진행합니다.", "pro": True},
    {"id": "detailpage", "group": "상세페이지 제작", "label": "PSD 작업", "subtitle": "이미지 업로드만 하면 상세페이지 PSD/JPG 작업을 빠르게 진행합니다.", "pro": False},
    {"id": "thumbnail", "group": "상세페이지 제작", "label": "썸네일 생성", "subtitle": "규격에 맞게 자동 배치와 텍스트 합성으로 썸네일을 만듭니다.", "pro": True},
    {"id": "gif", "group": "상세페이지 제작", "label": "GIF 생성", "subtitle": "이미지와 영상으로 상품 GIF를 빠르게 생성합니다.", "pro": True},

    {"id": "marketing_os", "group": "마케팅", "label": "마케팅 OS", "subtitle": "채널별 마케팅 문구와 원고를 통합 생성합니다.", "pro": True},
    {"id": "seo", "group": "마케팅", "label": "SEO 생성", "subtitle": "상품 SEO 메타, 키워드, 설명문을 빠르게 생성합니다.", "pro": True},
    {"id": "blog", "group": "마케팅", "label": "블로그 작성", "subtitle": "상품과 키워드 기반으로 SEO 글 초안을 빠르게 만듭니다.", "pro": True},

    {"id": "md_insight", "group": "인사이트 분석", "label": "MD 인사이트", "subtitle": "패션 키워드, 상품, 경쟁사 데이터를 분석하고 상품기획 인사이트를 제공합니다.", "pro": True},
    {"id": "miya_manager", "group": "분석도구", "label": "챗봇 관리/분석", "subtitle": "미야언니 상담 로그와 운영 현황을 점검합니다.", "pro": True},
    {"id": "db_maker", "group": "분석도구", "label": "상품DB 생성", "subtitle": "카테고리와 상품 URL 기반으로 미샵 상품 DB를 생성합니다.", "pro": True},

    {"id": "crm_os", "group": "운영관리", "label": "CRM 관리", "subtitle": "회원 데이터 업로드부터 세그먼트와 실행 전략까지 관리합니다.", "pro": True},
    {"id": "sample_manager", "group": "운영관리", "label": "샘플반품관리", "subtitle": "샘플과 반품 데이터 검색, 이력 관리를 빠르게 처리합니다.", "pro": True},
    {"id": "mishap_news_post", "group": "인사이트 분석", "label": "뉴스/정보/인사이트", "subtitle": "패션·유통·IT·경제 뉴스와 미샵 인사이트를 한 화면에서 확인합니다.", "pro": True},

    {"id": "usage_guide", "group": "설정", "label": "기능별 사용법", "subtitle": "Seller OS 전체 메뉴의 사용 흐름과 권장 루틴을 확인합니다.", "pro": False},
]

GROUP_ORDER = ["대시보드", "인사이트 분석", "상세페이지 제작", "마케팅", "분석도구", "운영관리", "설정"]
GROUP_META = {
    "대시보드": "오늘 업무를 한 화면에서 관리",
    "인사이트 분석": "MD 인사이트와 뉴스 기반 기획 분석",
    "상세페이지 제작": "기획부터 템플릿, PSD, 썸네일, GIF 작업",
    "마케팅": "광고, SEO, 블로그 콘텐츠",
    "분석도구": "챗봇과 상품 DB 점검 도구",
    "운영관리": "실무 운영과 관리 기능",
    "설정": "가이드와 공통 안내",
}

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
PAGES_BY_GROUP = {group: [p for p in PAGES if p['group'] == group] for group in GROUP_ORDER}

st.set_page_config(page_title=APP_TITLE, layout="wide", initial_sidebar_state="expanded")


def _qp_get(name: str, default: str = "") -> str:
    try:
        val = st.query_params.get(name, default)
        if isinstance(val, list):
            return val[0] if val else default
        return val or default
    except Exception:
        return default

def _qp_set(**kwargs):
    try:
        for k, v in kwargs.items():
            if v is None:
                try:
                    del st.query_params[k]
                except Exception:
                    pass
            else:
                st.query_params[k] = str(v)
    except Exception:
        pass

def _restore_auth_from_url():
    auth_hash = _qp_get("mso_auth", "").strip()
    if auth_hash and auth_hash in VALID_CODE_HASHES:
        st.session_state["pro_authed"] = True
        st.session_state["pro_user_key"] = auth_hash[:16]

def _sync_page_from_url():
    page_from_url = _qp_get("page", "").strip()
    valid_ids = {p["id"] for p in PAGES}
    if page_from_url in valid_ids and st.session_state.get("page") != page_from_url:
        st.session_state["page"] = page_from_url

def _apply_shell_sidebar_fix():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] div.stButton{margin:0 !important; width:100% !important;}
    section[data-testid="stSidebar"] div.stButton > button{width:100% !important; min-height:42px !important; height:42px !important; padding:0.35rem 0.55rem !important; margin:0 !important; border-radius:12px !important; font-size:14px !important; line-height:1.15 !important; font-weight:700 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important;}
    section[data-testid="stSidebar"] div.stButton > button p{font-size:14px !important; line-height:1.15 !important; margin:0 !important; white-space:nowrap !important; overflow:hidden !important; text-overflow:ellipsis !important;}
    section[data-testid="stSidebar"] .mso-brand-button div.stButton > button{height:42px !important; min-height:42px !important; padding:0.35rem 0.55rem !important; background:rgba(255,255,255,0.02) !important; border:1px solid rgba(255,255,255,0.14) !important; text-align:center !important; color:#EDEDED !important; justify-content:center !important; border-radius:12px !important;}
    section[data-testid="stSidebar"] .mso-brand-button div.stButton > button p{font-size:14px !important; line-height:1.15 !important; font-weight:800 !important; letter-spacing:0px !important; white-space:nowrap !important;}
    </style>
    """, unsafe_allow_html=True)

_restore_auth_from_url()
_sync_page_from_url()

if 'page' not in st.session_state:
    st.session_state['page'] = 'dashboard'
if 'nav_nonce' not in st.session_state:
    st.session_state['nav_nonce'] = 0

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');
html, body, [class*="css"], .stApp, .stMarkdown, .stTextInput, .stSelectbox, .stTextArea, .stButton, .stDownloadButton { font-family: 'Nanum Gothic', sans-serif !important; }
div.block-container { padding-top: 3.2rem; padding-bottom: 2rem; max-width: 1200px; }
.ms-card { border: 1px solid rgba(255,255,255,0.10); border-radius: 18px; padding: 18px 18px; background: rgba(255,255,255,0.04); backdrop-filter: blur(6px); }
.ms-card + .ms-card { margin-top: 14px; }
.ms-header { border-radius: 18px; padding: 18px 18px; margin-top: 0.25rem; margin-bottom: 18px; border: 1px solid rgba(255,255,255,0.10); background: rgba(255,255,255,0.05); }
.ms-title { font-size: 30px; font-weight: 800; margin: 0; color: rgba(255,255,255,0.92); }
.ms-sub { font-size: 13px; margin: 8px 0 0 0; color: rgba(255,255,255,0.70); line-height: 1.5; }
.ms-page-footer {margin-top:28px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.08);color:rgba(255,255,255,0.58);font-size:12px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;}
.stButton>button, .stDownloadButton>button { border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.14) !important; background: rgba(255,255,255,0.06) !important; color: rgba(255,255,255,0.92) !important; }
.stButton>button:hover, .stDownloadButton>button:hover { background: rgba(255,255,255,0.10) !important; border-color: rgba(255,255,255,0.22) !important; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div { border-radius: 12px !important; }
.ms-shortcut-card .stLinkButton, .ms-shortcut-card .stLinkButton > a { width:100% !important; }
.ms-shortcut-link { display:flex !important; align-items:center !important; justify-content:center !important; min-height:42px !important; border-radius:10px !important; border:1px solid rgba(255,255,255,0.14) !important; background:rgba(255,255,255,0.02) !important; color:rgba(255,255,255,0.95) !important; text-decoration:none !important; font-weight:700 !important; margin:0 !important; }
.ms-shortcut-link:hover { background:rgba(255,255,255,0.08) !important; }
.ms-shortcut-card{margin:0 0 2px 0 !important;}
section[data-testid="stSidebar"] .stButton > button{min-height:42px !important; margin:0 !important; border-radius:12px !important; font-weight:700 !important;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div{gap:6px !important;}
section[data-testid="stSidebar"] .mso-brand-text{display:block !important;color:#EDEDED !important;font-weight:800 !important;font-size:14px !important;letter-spacing:0px !important;line-height:1.15 !important;margin:6px 0 10px 0 !important;white-space:nowrap !important;text-align:center !important;}
section[data-testid="stSidebar"] .mso-domain{font-size:11px;color:rgba(255,255,255,0.55);margin:-2px 0 14px 1px;}
section[data-testid="stSidebar"] .mso-group-title{font-size:14px;font-weight:900;color:rgba(255,255,255,0.92);margin:18px 0 4px 2px;letter-spacing:-0.2px;}
section[data-testid="stSidebar"] .mso-group-sub{font-size:11px;color:rgba(255,255,255,0.48);margin:0 0 8px 2px;line-height:1.35;}
section[data-testid="stSidebar"] .mso-badge{display:inline-block;padding:3px 7px;border-radius:999px;font-size:10px;font-weight:800;line-height:1;white-space:nowrap;}
section[data-testid="stSidebar"] .mso-badge.free{background:rgba(46,204,113,0.16);color:#8FF0B3;border:1px solid rgba(46,204,113,0.22);}
section[data-testid="stSidebar"] .mso-badge.pro{background:rgba(255,77,79,0.15);color:#FFB0B1;border:1px solid rgba(255,77,79,0.20);}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"] { background:#ffffff !important; color:#0d1522 !important; border-color:#ffffff !important; }
section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] { background:rgba(255,255,255,0.02) !important; color:#EDEDED !important; }
[data-testid="collapsedControl"]{display:flex !important; visibility:visible !important; opacity:1 !important;}
</style>
""", unsafe_allow_html=True)

def set_page(page_key: str):
    valid_ids = {p["id"] for p in PAGES}
    if page_key in valid_ids:
        st.session_state["page"] = page_key
        st.session_state["nav_nonce"] = st.session_state.get("nav_nonce", 0) + 1
        _qp_set(page=page_key)

def get_page():
    valid_ids = {p['id'] for p in PAGES}
    page = (st.session_state.get('page') or 'dashboard').strip()
    if page not in valid_ids:
        page = 'dashboard'
    st.session_state['page'] = page
    return page

def get_dashboard_user_key():
    if st.session_state.get('pro_authed', False) and st.session_state.get('pro_user_key'):
        return st.session_state.get('pro_user_key')
    return None

def header(title: str, subtitle: str):
    st.markdown(f"""
    <div class="ms-header">
      <div class="ms-title">{title}</div>
      <div class="ms-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def _usage_guide_html() -> str:
    items = [
        ("대시보드", "오늘 메모·할 일·바로가기를 한 화면에 모아 매일 작업 시작점을 만드는 화면입니다.", ["로그인 후 메모, 할인 일정, 바로가기 URL을 저장합니다.", "자주 쓰는 관리자·상품등록·프로모션 페이지를 등록해 반복 이동 시간을 줄입니다.", "오늘 처리할 상품/콘텐츠/운영 업무를 3~5개로 정리해 실행 순서를 잡습니다."]),
        ("기획/작성", "상품 상세페이지의 설득 구조와 미샵식 설명 원고를 만드는 핵심 제작 도구입니다.", ["상품명, 소재, 핏, 체형 커버 포인트, 착용 상황을 입력합니다.", "생성된 원고를 상세페이지, 스마트스토어, 광고 문구의 기본 소스로 재활용합니다.", "4050 고객이 실제로 궁금해하는 사이즈·비침·두께·활용도를 빠짐없이 보강합니다."]),
        ("템플릿 작업", "반복 사용 가능한 상세페이지 템플릿을 만들고 관리하는 작업실입니다.", ["브랜드 공통 섹션과 상품별 변동 섹션을 분리해 템플릿을 만듭니다.", "상품군별로 자주 쓰는 문장 구조를 저장해 다음 제작 시간을 줄입니다.", "PSD 작업 전 텍스트와 섹션 순서를 먼저 정리할 때 사용합니다."]),
        ("PSD 작업", "상세페이지 이미지를 정해진 폭과 순서로 합치고 PSD/JPG 작업물을 빠르게 만드는 도구입니다.", ["상세 이미지 파일을 업로드하고 순서를 정리합니다.", "10장 이상 PSD 분할 등 기존 제작 규칙에 맞춰 결과물을 생성합니다.", "생성 후 모바일 화면에서 컷 순서, 여백, 광고 이미지 위치를 확인합니다."]),
        ("썸네일 생성", "상품 대표 이미지에 클릭을 유도하는 짧은 문구를 얹어 썸네일을 만드는 도구입니다.", ["대표컷 1장과 핵심 후킹 문구를 준비합니다.", "문구는 짧게 잡고 상품 장점은 하나만 강조합니다.", "신상, 세일, 체형커버, 출근룩 등 판매 목적에 따라 문구를 바꿔 테스트합니다."]),
        ("GIF 생성", "상품 디테일, 착용감, 움직임을 짧은 반복 이미지로 보여주는 도구입니다.", ["연속 이미지나 짧은 영상을 업로드합니다.", "핏 변화, 원단 찰랑임, 디테일 클로즈업처럼 정지 이미지로 부족한 부분을 보여줍니다.", "너무 빠른 속도보다 고객이 이해할 수 있는 자연스러운 속도를 우선합니다."]),
        ("마케팅 OS", "인스타그램, 숏폼, 광고, 문자 등 채널별 판매 문구를 생성하는 마케팅 작업실입니다.", ["상품 정보와 행사 내용을 입력합니다.", "릴스·쇼츠·틱톡·카카오스타일·문자 등 필요한 채널 형식을 선택합니다.", "첫 3초 후킹, 고객 고민, 해결 포인트, CTA가 모두 들어갔는지 확인합니다."]),
        ("SEO 생성", "상품명, 메타 설명, 검색 키워드, 이미지 ALT 등 검색 노출 요소를 정리하는 도구입니다.", ["상품 URL 또는 상품 정보를 입력합니다.", "네이버·구글 검색 의도에 맞는 제목, 설명, 키워드를 생성합니다.", "AI 검색에 잡히도록 질문에 답하는 문장과 고객 고민 해결형 표현을 보강합니다."]),
        ("블로그 작성", "상품·생활정보·마케팅 주제를 블로그 글 초안으로 확장하는 도구입니다.", ["주제, 상품 링크, 핵심 키워드, 독자 대상을 입력합니다.", "상단 요약, 서론, 본문, 3줄 요약, 태그까지 한 번에 구성합니다.", "발행 전 제목과 첫 300자를 직접 다듬어 검색 클릭률을 높입니다."]),
        ("MD 인사이트", "키워드, 인기 상품, 경쟁사 흐름을 보고 다음 상품기획 아이디어를 찾는 분석 도구입니다.", ["키워드 RADAR로 수요가 움직이는 단어를 확인합니다.", "상품 RADAR와 경쟁사 RADAR로 실제 판매 화면의 흐름을 비교합니다.", "매출형 상품기획 탭에서 미샵 고객에게 맞는 기획 방향으로 정리합니다."]),
        ("챗봇 관리/분석", "미야언니 상담 로그와 고객 질문 흐름을 확인해 챗봇 품질을 관리하는 도구입니다.", ["상담 수, 오류, fallback, 자주 나오는 질문을 확인합니다.", "사이즈·코디·상품추천 답변 품질을 점검합니다.", "반복 오류는 상품 DB 또는 상담 프롬프트 수정 대상으로 분류합니다."]),
        ("상품DB 생성", "미야언니와 상품추천 도구가 참고할 상품 DB를 만드는 도구입니다.", ["상품 URL 또는 카테고리 정보를 입력해 상품 데이터를 생성합니다.", "상품명, 컬러, 사이즈, 소재, 추천 체형, 설명 정보를 확인합니다.", "신상품이 자주 올라오는 월~금에는 DB 최신화 루틴을 정해 운영합니다."]),
        ("CRM 관리", "회원 데이터를 기준으로 광고 발송·재구매·휴면 고객 전략을 세우는 운영 도구입니다.", ["회원/주문 엑셀을 업로드하고 SMS 수신 동의 여부를 확인합니다.", "실결제금액, 주문당단가, 최종접속일 등으로 고객군을 나눕니다.", "불량회원과 장기 미접속 고객은 별도 전략으로 분리해 발송 품질을 관리합니다."]),
        ("샘플반품관리", "샘플과 반품 데이터를 검색하고 이력을 관리하는 실무 운영 도구입니다.", ["날짜별 자료를 기준으로 상품명, 업체명, 반품 여부를 검색합니다.", "반복 반품이나 샘플 회수 누락을 확인합니다.", "주간 정산 전 확인용으로 사용하면 운영 누락을 줄일 수 있습니다."]),
        ("뉴스/정보/인사이트", "패션·유통·AI·마케팅 뉴스를 모아 콘텐츠와 운영 아이디어로 바꾸는 도구입니다.", ["관심 분야 뉴스를 확인하고 미샵에 적용할 인사이트를 정리합니다.", "블로그 소재, SNS 후킹 문구, 상품기획 아이디어로 재활용합니다.", "매일 10개 이하 핵심 기사만 축적해 과부하 없이 운영합니다."]),
        ("기능별 사용법", "셀러OS 전체 메뉴의 목적과 기본 사용 순서를 확인하는 안내 페이지입니다.", ["처음 쓰는 기능은 먼저 이 페이지에서 목적과 입력 순서를 확인합니다.", "직원 교육이나 새 작업 루틴 공유용으로 활용합니다.", "기능이 추가될 때마다 사용법을 함께 보완합니다."]),
    ]
    cards = []
    for title, purpose, steps in items:
        li = ''.join(f'<li>{x}</li>' for x in steps)
        cards.append(f'<article class="card"><h2>{title}</h2><p class="purpose">{purpose}</p><h3>사용방법</h3><ul>{li}</ul></article>')
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MISHARP SELLER OS 기능별 사용법</title>
<style>
body{{margin:0;background:#08111f;color:#f3f4f6;font-family:'Nanum Gothic',Arial,sans-serif;line-height:1.72;}}
.wrap{{max-width:1080px;margin:0 auto;padding:34px 22px 80px;}}
.hero,.card{{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.11);border-radius:18px;padding:22px;}}
.hero h1{{font-size:40px;line-height:1.15;margin:0 0 12px;font-weight:900;}}
.hero p{{margin:8px 0;color:rgba(255,255,255,.82);font-size:16px;}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:20px;}}
.card h2{{margin:0 0 8px;font-size:22px;font-weight:900;}}
.card h3{{margin:16px 0 6px;font-size:15px;color:#dbeafe;}}
.purpose{{margin:0;color:rgba(255,255,255,.78);}}
ul{{margin:8px 0 0 20px;padding:0;}} li{{margin:4px 0;}}
.flow{{margin-top:16px;padding:16px;border-radius:14px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.08);}}
.footer{{margin-top:24px;color:rgba(255,255,255,.55);font-size:13px;text-align:center;}}
@media (max-width:860px){{.grid{{grid-template-columns:1fr;}}.hero h1{{font-size:32px;}}}}
</style></head><body><div class="wrap">
<section class="hero"><h1>기능별 사용법</h1>
<p>MISHARP SELLER OS는 상세페이지 제작, 마케팅 콘텐츠, 분석, 운영관리를 한 화면에서 연결하는 미샵 전용 업무 OS입니다.</p>
<div class="flow"><b>추천 작업 흐름</b><br>상품 이미지 정리 → 기획/작성 → PSD 작업 → SEO 생성 → 블로그 작성 → 마케팅 OS → 성과/상담 분석</div>
</section><section class="grid">{''.join(cards)}</section>
<div class="footer">© 2026 MISHARP SELLER OS · 기능별 사용법 안내</div></div></body></html>"""




def render_usage_page():
    components.html(_usage_guide_html(), height=2600, scrolling=True)

def run_embedded_app(app_key: str):
    """Load an embedded tool from apps/<app_key>/app.py in the current process."""
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
    original_set_page_config = getattr(st, 'set_page_config', None)
    old_embed_flag = st.session_state.get("_mso_embedded_shell")
    old_embed_app = st.session_state.get("_mso_embedded_app")

    def _noop_set_page_config(*args, **kwargs):
        return None

    for p in (base, apps_root, repo_root):
        if p not in sys.path:
            sys.path.insert(0, p)

    for mod in list(sys.modules):
        if mod in {"utils", "modules", "core"} or mod.startswith(("utils.", "modules.", "core.")):
            sys.modules.pop(mod, None)

    try:
        st.session_state["_mso_embedded_shell"] = True
        st.session_state["_mso_embedded_app"] = app_key
        if original_set_page_config:
            st.set_page_config = _noop_set_page_config
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
    except SystemExit:
        pass
    except Exception as e:
        st.error(f"앱 실행 중 오류: {e}")
    finally:
        if old_embed_flag is None:
            st.session_state.pop("_mso_embedded_shell", None)
        else:
            st.session_state["_mso_embedded_shell"] = old_embed_flag
        if old_embed_app is None:
            st.session_state.pop("_mso_embedded_app", None)
        else:
            st.session_state["_mso_embedded_app"] = old_embed_app
        if original_set_page_config:
            st.set_page_config = original_set_page_config
        sys.path = old_sys_path
        _apply_shell_sidebar_fix()




with st.sidebar:
    current_page = get_page()
    st.sidebar.markdown('<div class="mso-brand-button">', unsafe_allow_html=True)
    if st.sidebar.button('MISHARP SELLER OS', key='brand_go_dashboard', use_container_width=True):
        set_page('dashboard')
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="mso-domain">{APP_DOMAIN}</div>', unsafe_allow_html=True)

    if st.session_state.get('pro_authed', False):
        st.sidebar.success('PRO 사용 가능')
        if st.sidebar.button('로그아웃', key='pro_logout', use_container_width=True):
            st.session_state['pro_authed'] = False
            st.session_state.pop('pro_user_key', None)
            _qp_set(mso_auth=None)
            for k in ['dash_booted','dash_user_loaded','dash_shortcuts','dash_memo','dash_todos','dash_memo_editor','dash_new_todo']:
                st.session_state.pop(k, None)
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
                st.session_state['pro_user_key'] = h[:16]
                _qp_set(mso_auth=h)
                for k in ['dash_booted','dash_user_loaded','dash_shortcuts','dash_memo','dash_todos','dash_memo_editor','dash_new_todo']:
                    st.session_state.pop(k, None)
                st.rerun()
            else:
                st.sidebar.error('코드가 올바르지 않습니다.')

    st.sidebar.markdown('---')

    # 대시보드는 최상단 고정
    dash = next((p for p in PAGES if p["id"] == "dashboard"), None)
    if dash:
        cols = st.sidebar.columns([5,1], gap='small')
        active = current_page == dash['id']
        btn_type = 'primary' if active else 'secondary'
        if cols[0].button(dash['label'], key=f"nav_{dash['id']}", use_container_width=True, type=btn_type):
            set_page(dash['id'])
            st.rerun()
        badge_cls = 'pro' if dash.get('pro', False) else 'free'
        badge_txt = 'PRO' if dash.get('pro', False) else 'FREE'
        cols[1].markdown(f'<div style="margin-top:8px;"><span class="mso-badge {badge_cls}">{badge_txt}</span></div>', unsafe_allow_html=True)

    for group in [g for g in GROUP_ORDER if g != "대시보드"]:
        pages = PAGES_BY_GROUP.get(group, [])
        if not pages:
            continue
        st.sidebar.markdown(f'<div class="mso-group-title">{group}</div>', unsafe_allow_html=True)
        for p in pages:
            cols = st.sidebar.columns([5,1], gap='small')
            active = current_page == p['id']
            btn_type = 'primary' if active else 'secondary'
            if cols[0].button(p['label'], key=f"nav_{p['id']}", use_container_width=True, type=btn_type):
                set_page(p['id'])
                st.rerun()
            badge_cls = 'pro' if p.get('pro', False) else 'free'
            badge_txt = 'PRO' if p.get('pro', False) else 'FREE'
            cols[1].markdown(f'<div style="margin-top:8px;"><span class="mso-badge {badge_cls}">{badge_txt}</span></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div style="color:rgba(255,255,255,0.45);font-size:11px;line-height:1.45;">{APP_COPYRIGHT}</div>', unsafe_allow_html=True)



def restore_shell_sidebar():
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:block !important; visibility:visible !important; transform:none !important;}
    [data-testid="collapsedControl"]{display:flex !important; visibility:visible !important; opacity:1 !important;}
    </style>
    """, unsafe_allow_html=True)
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
    from zoneinfo import ZoneInfo

    user_key = get_dashboard_user_key()
    state_path = Path(__file__).with_name(f"dashboard_state_{user_key}.json") if user_key else None

    def _default_shortcuts():
        return []

    def _empty_state():
        return {"memo": "", "todos": [], "shortcuts": _default_shortcuts()}

    def _load_dashboard_state():
        if state_path and state_path.exists():
            try:
                data = json.loads(state_path.read_text(encoding="utf-8"))
                return {
                    "memo": data.get("memo", ""),
                    "todos": data.get("todos", []),
                    "shortcuts": data.get("shortcuts", _default_shortcuts()) or _default_shortcuts(),
                }
            except Exception:
                pass
        return _empty_state()

    def _save_dashboard_state():
        if not state_path:
            return True
        try:
            payload = {
                "memo": st.session_state.get("dash_memo", ""),
                "todos": st.session_state.get("dash_todos", []),
                "shortcuts": st.session_state.get("dash_shortcuts", []),
            }
            state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    if ("dash_booted" not in st.session_state) or (st.session_state.get('dash_user_loaded') != user_key):
        loaded = _load_dashboard_state()
        st.session_state.dash_shortcuts = loaded["shortcuts"]
        st.session_state.dash_memo = loaded["memo"]
        st.session_state.dash_todos = loaded["todos"]
        st.session_state.dash_booted = True
        st.session_state.dash_user_loaded = user_key

    if "dash_shortcuts" not in st.session_state:
        st.session_state.dash_shortcuts = _default_shortcuts()
    if "dash_memo" not in st.session_state:
        st.session_state.dash_memo = ""
    if "dash_todos" not in st.session_state:
        st.session_state.dash_todos = []

    def _valid_url(url: str) -> bool:
        url = (url or "").strip()
        return url.startswith("http://") or url.startswith("https://")

    c1, c2, c3 = st.columns([1.0, 2.1, 2.2], gap="large")

    with c1:
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        dow_ko = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
        st.markdown("### 오늘")
        st.markdown(f"**{now.strftime('%Y-%m-%d')}({dow_ko})**")
        st.markdown(f"**{now.strftime('%H:%M')}**")
        w = _fetch_weather_seoul_daily()
        if w:
            desc, tmax, tmin = w
            st.caption(f"{desc} {tmax}° / {tmin}°")
        else:
            st.caption("날씨 정보를 불러오지 못했어요.")

    with c2:
        st.markdown("### 오늘 메모")
        st.session_state.dash_memo = st.text_area(
            label="",
            value=st.session_state.dash_memo,
            height=140,
            placeholder="오늘 중요한 메모를 적어두세요.",
            label_visibility="collapsed",
            key="dash_memo_editor",
        )
        if st.button("메모 저장하기", key="dash_memo_save", use_container_width=True):
            st.session_state.dash_memo = st.session_state.get("dash_memo_editor", "")
            if _save_dashboard_state():
                st.toast("메모를 저장했습니다.")
            else:
                st.error("메모 저장 중 오류가 발생했습니다.")

    with c3:
        st.markdown("### 오늘 할일")
        add_cols = st.columns([4.4, 1.0], gap="small")
        with add_cols[0]:
            new_todo = st.text_input(
                "할일 추가",
                "",
                placeholder="예) 상세페이지 3개 생성",
                label_visibility="collapsed",
                key="dash_new_todo",
            )
        with add_cols[1]:
            add_clicked = st.button("추가", key="todo_add", use_container_width=True)

        if add_clicked and new_todo.strip():
            st.session_state.dash_todos.append(
                {"id": str(uuid.uuid4()), "text": new_todo.strip(), "done": False}
            )
            _save_dashboard_state()
            st.rerun()

        remove_ids = []
        changed_done = False
        for item in st.session_state.dash_todos:
            row = st.columns([0.12, 0.66, 0.22], gap="small")
            checked = row[0].checkbox(
                "",
                value=item.get("done", False),
                key=f"todo_done_{item['id']}"
            )
            if checked != item.get("done", False):
                item["done"] = checked
                changed_done = True
            row[1].markdown(item["text"])
            if row[2].button("삭제", key=f"todo_del_{item['id']}", use_container_width=True):
                remove_ids.append(item["id"])

        if remove_ids:
            st.session_state.dash_todos = [
                t for t in st.session_state.dash_todos if t["id"] not in remove_ids
            ]
            _save_dashboard_state()
            st.rerun()

        if changed_done:
            _save_dashboard_state()

        if st.button("할일 저장하기", key="todo_save", use_container_width=True):
            if _save_dashboard_state():
                st.toast("할일을 저장했습니다.")
            else:
                st.error("할일 저장 중 오류가 발생했습니다.")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    st.markdown("### 바로가기")

    shortcuts = st.session_state.dash_shortcuts
    if not shortcuts:
        st.info("아직 바로가기가 없습니다. 아래에서 추가해보세요.")
    else:
        def _safe_html(v: str) -> str:
            return str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('\"', '&quot;')

        for start_idx in range(0, len(shortcuts), 4):
            cols = st.columns(4, gap="small")
            row_items = shortcuts[start_idx:start_idx+4]
            for idx, sc in enumerate(row_items):
                with cols[idx]:
                    st.markdown(
                        f'<div class="ms-shortcut-card"><a class="ms-shortcut-link" href="{_safe_html(sc.get("url", ""))}" target="_blank">{_safe_html(sc.get("title", "바로가기"))}</a></div>',
                        unsafe_allow_html=True,
                    )
            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)

    with st.expander("바로가기 추가/편집", expanded=False):
        st.markdown("**새 바로가기 추가**")

        h = st.columns([2.1, 3.8, 1.0], gap="small")
        h[0].markdown("제목")
        h[1].markdown("URL")
        h[2].markdown("&nbsp;", unsafe_allow_html=True)

        row = st.columns([2.1, 3.8, 1.0], gap="small")
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
        row[2].markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        if row[2].button("추가", key="shortcut_add", use_container_width=True):
            if not title.strip():
                st.error("제목을 입력해 주세요.")
            elif not _valid_url(url):
                st.error("URL은 http:// 또는 https:// 로 시작해야 합니다.")
            else:
                st.session_state.dash_shortcuts.append(
                    {"id": str(uuid.uuid4()), "title": title.strip(), "url": url.strip(), "emoji": ""}
                )
                _save_dashboard_state()
                st.success("추가되었습니다.")
                st.rerun()

        st.divider()
        st.markdown("**기존 바로가기 관리**")
        for idx, sc in enumerate(list(st.session_state.dash_shortcuts)):
            row = st.columns([0.55, 0.55, 2.0, 4.0, 1.1], gap="small")
            if row[0].button("↑", key=f"sc_up_{sc['id']}", use_container_width=True, disabled=(idx == 0)):
                st.session_state.dash_shortcuts[idx - 1], st.session_state.dash_shortcuts[idx] = (
                    st.session_state.dash_shortcuts[idx],
                    st.session_state.dash_shortcuts[idx - 1],
                )
                _save_dashboard_state()
                st.rerun()
            if row[1].button("↓", key=f"sc_down_{sc['id']}", use_container_width=True, disabled=(idx == len(st.session_state.dash_shortcuts) - 1)):
                st.session_state.dash_shortcuts[idx + 1], st.session_state.dash_shortcuts[idx] = (
                    st.session_state.dash_shortcuts[idx],
                    st.session_state.dash_shortcuts[idx + 1],
                )
                _save_dashboard_state()
                st.rerun()

            new_title = row[2].text_input(
                "제목", sc.get("title", ""),
                key=f"sc_title_{sc['id']}",
                label_visibility="collapsed",
            )
            new_url = row[3].text_input(
                "URL", sc.get("url", ""),
                key=f"sc_url_{sc['id']}",
                label_visibility="collapsed",
            )
            if row[4].button("삭제", key=f"sc_rm_{sc['id']}", use_container_width=True):
                st.session_state.dash_shortcuts = [
                    x for x in st.session_state.dash_shortcuts if x["id"] != sc["id"]
                ]
                _save_dashboard_state()
                st.rerun()
            sc["title"] = new_title
            sc["url"] = new_url

        if st.button("바로가기 변경사항 저장", key="shortcut_save", use_container_width=True):
            _save_dashboard_state()
            st.toast("바로가기를 저장했습니다.")





st.markdown("""
<style>
section[data-testid="stSidebar"] div.stButton{margin:0 !important;}
section[data-testid="stSidebar"] div.stButton > button{min-height:42px !important; padding-top:0.35rem !important; padding-bottom:0.35rem !important;}
</style>
""", unsafe_allow_html=True)

_apply_shell_sidebar_fix()
page = get_page()
title, subtitle = PAGE_META.get(page, ('', ''))
header(title, subtitle)

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
elif page == 'seo':
    run_embedded_app('seo')
elif page == 'page_builder':
    run_embedded_app('page_builder')
elif page == 'marketing_os':
    run_embedded_app('marketing_os')
elif page == 'crm_os':
    run_embedded_app('crm_os')
elif page == 'sample_manager':
    run_embedded_app('sample_manager')
elif page == 'mishap_news_post':
    run_embedded_app('mishap_news_post')
elif page == 'blog':
    run_embedded_app('blog')
elif page == 'md_insight':
    run_embedded_app('md_insight')
elif page == 'miya_manager':
    run_embedded_app('miya_manager')
elif page == 'db_maker':
    run_embedded_app('db_maker')
elif page == 'template_os':
    restore_shell_sidebar()
    run_embedded_app('template_os')
    restore_shell_sidebar()
elif page == 'usage_guide':
    render_usage_page()
else:
    st.info('준비 중인 페이지입니다.')

st.markdown(f'<div class="ms-page-footer"><div>미샵 셀러 스튜디오 OS · 공통 페이지 프레임 적용</div><div>{APP_COPYRIGHT}</div></div>', unsafe_allow_html=True)
