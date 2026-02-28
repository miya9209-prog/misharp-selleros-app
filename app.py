
import os, sys, runpy, json, datetime
import streamlit as st

# =========================================================
# PAGE CONFIG (set once)
# =========================================================
st.set_page_config(
    page_title="미샵 셀러 스튜디오 OS",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DOMAIN = "misharp-selleros.com"
APP_TITLE = "미샵 셀러 스튜디오 OS V1"
SUBCOPY = "온라인 셀러를 위한 혁신적인 원스톱 상세페이지 콘텐츠 자동 생성"

# =========================================================
# GLOBAL CSS (mockup-style)
# =========================================================
st.markdown(
    """
<style>
/* Hide default footer/menu */
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* container padding */
div[data-testid="stAppViewContainer"] .main { padding-top: 18px; padding-bottom: 90px; }

/* Top domain pill */
.domain-pill{
  display:inline-flex; align-items:center; gap:8px;
  padding:8px 14px; border-radius:999px;
  background:#fff; border:1px solid rgba(17,17,17,.10);
  font-size:13px; color:rgba(17,17,17,.75);
}

/* Hero card */
.hero{
  background:#fff;
  border:1px solid rgba(17,17,17,.10);
  border-radius:18px;
  padding:26px 26px 22px 26px;
  box-shadow: 0 6px 22px rgba(0,0,0,.05);
}
.hero h1{ margin:0; font-size:44px; letter-spacing:-1px; color:#111; }
.hero p{ margin:10px 0 0 0; font-size:16px; color:rgba(17,17,17,.70); }

/* Section bar */
.section-bar{
  margin-top:16px;
  background:#0f172a; color:#fff;
  padding:14px 18px;
  border-radius:14px;
  font-size:18px;
  font-weight:700;
}

/* Big buttons */
.big-btn-wrap button{
  width:100%;
  border-radius:14px !important;
  height:58px;
  font-weight:800;
  font-size:16px;
}

/* Tabs */
div[data-testid="stTabs"] button {
  font-weight:800;
  letter-spacing:-0.2px;
}
div[data-testid="stTabs"] button[aria-selected="true"]{
  color:#d31616 !important;
  border-bottom:2px solid #d31616 !important;
}

/* Footer fixed */
.misharp-footer{
  position: fixed;
  left: 0; bottom: 0;
  width: 100%;
  padding: 12px 16px;
  background: rgba(15,23,42,0.92);
  color: rgba(255,255,255,0.92);
  border-top: 1px solid rgba(255,255,255,0.10);
  font-size: 12px;
  z-index: 999999;
  backdrop-filter: blur(6px);
  display:flex; justify-content:space-between; align-items:center;
}
.misharp-footer a{ color: rgba(255,255,255,0.92); text-decoration:none; margin-left:14px; }
.misharp-footer a:hover{ text-decoration:underline; }
</style>
<div class="misharp-footer">
  <div>© 2026 misharpcompany. All rights reserved.</div>
  <div>
    <a href="#" onclick="return false;">서비스 소개</a>
    <a href="#" onclick="return false;">개인정보처리방침</a>
    <a href="#" onclick="return false;">이용약관</a>
    <a href="#" onclick="return false;">문의</a>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# Session state
# =========================================================
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "user_id": "", "is_pro": False}

if "shared" not in st.session_state:
    st.session_state.shared = {
        "saved": False,
        "product": {
            "product_name": "",
            "price": "",
            "material": "",
            "fit": "",
            "size": "",
            "color": "",
            "keywords": "",
            "highlights": ["", "", "", "", ""],
            "target": "4050",
            "tone": "미샵 문체",
            "ban_words": "",
            "product_url": "",
        },
        "uploads": {
            "images": [],
        },
        "outputs": {
            # each tool may append files {name, bytes, mime}
            "files": []
        }
    }

# =========================================================
# Utilities
# =========================================================
def pill_domain():
    st.markdown(f'<span class="domain-pill">Domain · {DOMAIN}</span>', unsafe_allow_html=True)

def hero():
    st.markdown(
        f"""
<div class="hero">
  <h1>{APP_TITLE}</h1>
  <p>{SUBCOPY}</p>
</div>
""",
        unsafe_allow_html=True,
    )

def require_shared_saved():
    if not st.session_state.shared.get("saved"):
        st.info("먼저 상단 공통 입력폼에서 상품 정보를 저장해 주세요.")
        return False
    return True

def add_output_file(name: str, data: bytes, mime: str="application/octet-stream"):
    st.session_state.shared["outputs"]["files"].append({"name": name, "bytes": data, "mime": mime})

def reset_all():
    st.session_state.shared["saved"] = False
    st.session_state.shared["product"] = {
        "product_name": "",
        "price": "",
        "material": "",
        "fit": "",
        "size": "",
        "color": "",
        "keywords": "",
        "highlights": ["", "", "", "", ""],
        "target": "4050",
        "tone": "미샵 문체",
        "ban_words": "",
        "product_url": "",
    }
    st.session_state.shared["uploads"] = {"images": []}
    st.session_state.shared["outputs"] = {"files": []}
    st.toast("초기화 완료", icon="✅")

def download_package_zip():
    import zipfile, io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # product info
        meta = json.dumps(st.session_state.shared["product"], ensure_ascii=False, indent=2).encode("utf-8")
        zf.writestr("product_info.json", meta)
        # files
        for f in st.session_state.shared["outputs"]["files"]:
            zf.writestr(f"outputs/{f['name']}", f["bytes"])
    buf.seek(0)
    st.download_button(
        "전체 패키지 ZIP 다운로드",
        data=buf.getvalue(),
        file_name=f"misharp_selleros_package_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
        mime="application/zip",
        use_container_width=True,
    )

def run_tool_script(tool_dir: str, script_name: str = "app.py"):
    """
    Execute a tool's Streamlit script under tools/<tool_dir>/<script_name>.
    The script is patched to not call st.set_page_config.
    """
    tool_path = os.path.join(os.path.dirname(__file__), "tools", tool_dir)
    script_path = os.path.join(tool_path, script_name)

    # ensure imports within tool work
    if tool_path not in sys.path:
        sys.path.insert(0, tool_path)

    # run
    runpy.run_path(script_path, run_name="__main__")

# =========================================================
# Login screen (optional, mockup-compatible)
# =========================================================
def login_screen():
    pill_domain()
    hero()
    st.markdown("<div class='section-bar'>LOG-IN</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1,1])
    with col1:
        uid = st.text_input("ID", value=st.session_state.auth.get("user_id",""))
    with col2:
        pw = st.text_input("PASS", type="password")

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("LOG-IN", use_container_width=True):
            # MVP: any non-empty id/pw passes; PRO can be set later via secrets
            if uid.strip() and pw.strip():
                st.session_state.auth["logged_in"] = True
                st.session_state.auth["user_id"] = uid.strip()
                st.session_state.auth["is_pro"] = False
                st.success("로그인 완료")
                st.rerun()
            else:
                st.error("ID/PASS를 입력해 주세요.")
    with c2:
        if st.button("FREE로 시작", use_container_width=True):
            st.session_state.auth["logged_in"] = True
            st.session_state.auth["user_id"] = "FREE"
            st.session_state.auth["is_pro"] = False
            st.rerun()
    with c3:
        st.button("회원가입(준비중)", use_container_width=True, disabled=True)

    st.markdown("---")
    st.write("사용 및 협업 문의 : misharpmail@naver.com")

# =========================================================
# Shared input form (mockup)
# =========================================================
def shared_input_form():
    st.markdown("<div class='section-bar'>공통 입력폼 (1회 입력 → 전체 탭에서 재사용)</div>", unsafe_allow_html=True)

    p = st.session_state.shared["product"]

    with st.expander("공통 입력폼 (열기/닫기)", expanded=True):
        c1, c2, c3 = st.columns([1.2, 1, 1])
        with c1:
            p["product_name"] = st.text_input("상품명", value=p["product_name"])
            p["price"] = st.text_input("가격", value=p["price"])
            p["material"] = st.text_input("소재", value=p["material"])
            p["fit"] = st.text_input("핏", value=p["fit"])
        with c2:
            p["size"] = st.text_input("사이즈", value=p["size"])
            p["color"] = st.text_input("컬러", value=p["color"])
            p["keywords"] = st.text_input("키워드(콤마구분)", value=p["keywords"])
            p["product_url"] = st.text_input("상품 URL (선택)", value=p["product_url"])
        with c3:
            p["target"] = st.selectbox("타겟", ["4050", "3040", "기타"], index=0 if p["target"]=="4050" else 1)
            p["tone"] = st.text_input("톤", value=p["tone"])
            p["ban_words"] = st.text_input("금칙어(콤마구분)", value=p["ban_words"])

        st.markdown("### 특장점 5줄")
        hl = p.get("highlights", ["","","","",""])
        for i in range(5):
            hl[i] = st.text_input(f"특장점 {i+1}", value=hl[i], key=f"hl_{i}")
        p["highlights"] = hl

        st.markdown("### 상품 이미지 업로드 (공통 저장)")
        imgs = st.file_uploader(
            "이미지 업로드",
            type=["jpg","jpeg","png","webp"],
            accept_multiple_files=True,
            key="shared_images_uploader"
        )
        if imgs:
            st.session_state.shared["uploads"]["images"] = [
                {"name": f.name, "bytes": f.getvalue()} for f in imgs
            ]
            st.caption(f"업로드 {len(imgs)}개 저장됨 (탭에서 재사용)")

        st.markdown('<div class="big-btn-wrap">', unsafe_allow_html=True)
        if st.button("공통 입력 저장", use_container_width=True):
            st.session_state.shared["saved"] = True
            st.toast("공통 입력 저장 완료", icon="✅")
        st.markdown("</div>", unsafe_allow_html=True)

    # action buttons row
    left, right = st.columns([1,1])
    with left:
        st.markdown('<div class="big-btn-wrap">', unsafe_allow_html=True)
        if st.button("입력 초기화", use_container_width=True):
            reset_all()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="big-btn-wrap">', unsafe_allow_html=True)
        download_package_zip()
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Pages (mockup-based)
# =========================================================
def dashboard_page():
    st.markdown("<div class='section-bar'>대시보드</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        st.write("**날짜**")
        st.write(datetime.datetime.now().strftime("%Y-%m-%d"))
    with c2:
        st.write("**이벤트**")
        st.write("—")
    with c3:
        st.write("**날씨**")
        st.write("—")

    st.markdown("### 오늘의 주요업무 / 중요업무 메모")
    st.text_area("메모", height=120, placeholder="오늘 중요한 업무를 적어두세요.")

    st.markdown("### 나만의 대시보드 (바로가기 링크)")
    if "quick_links" not in st.session_state:
        st.session_state.quick_links = [{"title":"","url":""} for _ in range(6)]

    for i in range(len(st.session_state.quick_links)):
        colA, colB = st.columns([1,2])
        with colA:
            st.session_state.quick_links[i]["title"] = st.text_input(f"제목입력 {i+1}", st.session_state.quick_links[i]["title"], key=f"ql_t_{i}")
        with colB:
            st.session_state.quick_links[i]["url"] = st.text_input(f"바로가기 URL입력 {i+1}", st.session_state.quick_links[i]["url"], key=f"ql_u_{i}")

    st.caption("나만의 대시보드 하단에 내업무에 필요한 사이트를 자유롭게 추가, 삭제, 배치하세요.")

def detail_and_copy_page():
    st.markdown("<div class='section-bar'>상세페이지 / 원고 생성</div>", unsafe_allow_html=True)
    if not require_shared_saved():
        return
    # Use existing detail page maker tool
    st.caption("기존 상세페이지 생성기 기능을 통합 실행합니다.")
    run_tool_script("detail_page", "app.py")

def copy_only_page():
    st.markdown("<div class='section-bar'>원고 생성 (PRO)</div>", unsafe_allow_html=True)
    if not require_shared_saved():
        return
    # MVP: generate prompt text file based on the guideline
    p = st.session_state.shared["product"]
    prompt = f"""당신은 미샵(MISHARP) 4050 여성 전문 쇼핑몰의 상세페이지 원고 전문 라이터입니다.
아래 상품 정보로 '반품/취소율 감소'를 목표로 HTML 원고를 작성하세요.

[입력]
상품명: {p.get('product_name')}
가격: {p.get('price')}
소재: {p.get('material')}
핏: {p.get('fit')}
사이즈: {p.get('size')}
컬러: {p.get('color')}
키워드: {p.get('keywords')}
특장점: {", ".join([x for x in p.get("highlights", []) if x])}
타겟: {p.get('target')}
톤: {p.get('tone')}
금칙어: {p.get('ban_words')}

[출력 규칙]
- HTML로만 출력
- <div id="subsc"><h3>상품명</h3><p>...</p></div> 구조
- 소제목은 <strong style="font-weight:700 !important;">[...]
- 줄바꿈: <br>, 문단: <br><br>
- 전체 글자수 700자 이내
"""
    st.text_area("원고 생성 프롬프트(복사해서 사용)", value=prompt, height=300)
    st.download_button("프롬프트 TXT 저장하기", data=prompt.encode("utf-8"), file_name="copy_prompt.txt", use_container_width=True)

def thumbnail_page():
    st.markdown("<div class='section-bar'>썸네일 생성 (PRO)</div>", unsafe_allow_html=True)
    if not require_shared_saved():
        return
    run_tool_script("thumbnail", "app.py")

def gif_page():
    st.markdown("<div class='section-bar'>GIF 생성 (PRO)</div>", unsafe_allow_html=True)
    if not require_shared_saved():
        return
    run_tool_script("gif", "app.py")

def image_collect_page():
    st.markdown("<div class='section-bar'>이미지 수집툴 (PRO)</div>", unsafe_allow_html=True)
    if not require_shared_saved():
        return
    st.info("이미지 수집툴은 다음 단계에서 통합합니다. (현재는 별도 앱 버전을 사용 중)")
    st.write("현재 사용 URL: https://misharp-image-crop-v1.streamlit.app/")

def blog_page():
    st.markdown("<div class='section-bar'>블로그 작성 (PRO)</div>", unsafe_allow_html=True)
    if not require_shared_saved():
        return
    run_tool_script("blog", "app.py")

def shortform_page():
    st.markdown("<div class='section-bar'>숏폼 메이커 (PRO)</div>", unsafe_allow_html=True)
    if not require_shared_saved():
        return
    st.subheader("1) 입력")
    url = st.text_input("상품 URL 입력", value=st.session_state.shared["product"].get("product_url",""))
    topic = st.text_area("숏폼 주제/컨셉/요청사항 입력", height=120)
    seconds = st.slider("초수 입력 (10~40초)", min_value=10, max_value=40, value=20, step=1)
    uploads = st.file_uploader("첨부파일(이미지/동영상/문서 등)", accept_multiple_files=True)

    st.subheader("2) 플랫폼 선택")
    platform = st.radio("플랫폼", ["릴스", "카드뉴스", "쇼츠", "틱톡", "롱폼"], horizontal=True)

    st.subheader("3) 출력")
    if st.button("생성하기", use_container_width=True):
        p = st.session_state.shared["product"]
        out = f"""[릴스 제목]
{p.get('product_name','') or '주제 기반 제목'} ({seconds}초 / {platform})

[화면별 자막 구성]
- HOOK(1~2초): (공감/부정형 질문)  
- INTRO: 상황 공감 2~3줄  
- PRODUCT: 해결 포인트 3~4줄  
- EFFECT: 변화/결과 문장  
- CTA: 저장/댓글/사이트 유도  

[촬영 컷 가이드]
- 정면/측면/디테일/착장 TPO 컷 구성

[캡션 글 전체]
(여기에 캡션 초안)

[해시태그 20개]
#미샵 #4050패션 #중년여성코디 #체형커버 #꾸안꾸 #단정룩 ...
"""
        st.text_area("생성 결과", value=out, height=320)
        st.download_button("다운받기(TXT)", data=out.encode("utf-8"), file_name="shortform_idea.txt", use_container_width=True)

# =========================================================
# Main router
# =========================================================
pill_domain()
hero()

# if you want to require login for all pages, keep this on:
if not st.session_state.auth.get("logged_in"):
    login_screen()
    st.stop()

shared_input_form()

tab_labels = [
    "대시보드",
    "상세페이지/원고 생성",
    "원고 생성(PRO)",
    "썸네일 생성(PRO)",
    "GIF 생성(PRO)",
    "이미지 수집툴(PRO)",
    "블로그 작성(PRO)",
    "숏폼 메이커(PRO)",
]

tabs = st.tabs(tab_labels)

with tabs[0]:
    dashboard_page()
with tabs[1]:
    detail_and_copy_page()
with tabs[2]:
    copy_only_page()
with tabs[3]:
    thumbnail_page()
with tabs[4]:
    gif_page()
with tabs[5]:
    image_collect_page()
with tabs[6]:
    blog_page()
with tabs[7]:
    shortform_page()
