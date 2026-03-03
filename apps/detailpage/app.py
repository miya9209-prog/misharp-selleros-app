import streamlit as st
from PIL import Image
import io
import os
import base64
import hashlib
from typing import List, Optional

# =========================================================
# PAGE CONFIG
# =========================================================
# =========================================================
# CONSTANTS
# =========================================================
MAX_FILES = 10

ASSETS_DIR = "assets"
AD_LEFT_PATH = os.path.join(ASSETS_DIR, "ad_left.png")
AD_RIGHT_PATH = os.path.join(ASSETS_DIR, "ad_right.png")
TOP_BANNER_PATH = os.path.join(ASSETS_DIR, "top_banner.png")

AD_W = 300
TOP_BANNER_H = 160

MISHARP_URL = "https://www.misharp.co.kr"

# ✅✅✅ PRO 신청 링크(구글폼)로 교체
PRO_APPLY_URL = "https://docs.google.com/forms/d/e/1FAIpQLScA_ZEMDmlW3DwdPk_Bn6L5WUeOoT7BFhRb3MPP2t_EMtBHwA/viewform?usp=publish-editor"

UPLOADER_KEY_BASE = "uploader_files"
RESET_FLAG_KEY = "do_reset"

OUTPUT_WIDTH = 900  # ✅ 생성 결과 가로 900px 고정

# =========================================================
# SESSION STATE INIT
# =========================================================
if "files" not in st.session_state:
    st.session_state["files"] = []  # list[(name, bytes, PIL)]
if "seen_hashes" not in st.session_state:
    st.session_state["seen_hashes"] = set()
if "result_bytes" not in st.session_state:
    st.session_state["result_bytes"] = None
if "result_filename" not in st.session_state:
    st.session_state["result_filename"] = "detail_page.jpg"
if "just_generated" not in st.session_state:
    st.session_state["just_generated"] = False
if "uploader_nonce" not in st.session_state:
    st.session_state["uploader_nonce"] = 0
if RESET_FLAG_KEY not in st.session_state:
    st.session_state[RESET_FLAG_KEY] = False

def current_uploader_key() -> str:
    return f"{UPLOADER_KEY_BASE}_{st.session_state['uploader_nonce']}"

# =========================================================
# SAFE RESET HANDLING
# ✅ 핵심: uploader_nonce를 증가시켜 file_uploader 위젯 자체를 새로 만들어 "이전 파일이 섞여오는 문제"를 차단
# =========================================================
if st.session_state.get(RESET_FLAG_KEY, False):
    st.session_state["files"] = []
    st.session_state["seen_hashes"] = set()
    st.session_state["result_bytes"] = None
    st.session_state["result_filename"] = "detail_page.jpg"
    st.session_state["just_generated"] = False

    # ✅ file_uploader 위젯 완전 초기화
    st.session_state["uploader_nonce"] += 1

    st.session_state[RESET_FLAG_KEY] = False

# =========================================================
# CSS
# =========================================================
st.markdown(
    f"""
<style>
:root{{
  --bg:#ffffff;
  --card:#ffffff;
  --border:#e6e8ef;
  --text:#101828;
  --muted:#667085;
  --danger:#e60012;

  --primary:#111827;
  --primaryHover: rgba(0,0,0,0.90);

  --shadow:0 10px 30px rgba(16,24,40,.07);

  --s1:16px; --s2:24px; --s3:32px; --s4:40px; --s5:56px;

  --greenText:#0f5132;
  --greenBg:#d1e7dd;
  --greenBorder:#badbcc;
}}

.stApp{{ background: var(--bg) !important; }}
.block-container{{
  max-width: 1320px;
  padding-top: var(--s3) !important;
  padding-bottom: 70px !important;
}}
html, body, [class*="css"] {{
  font-family: Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR",
               "Apple SD Gothic Neo", "Malgun Gothic", Arial, sans-serif !important;
}}

/* =========================================================
   ✅ (1) 파일선택 위 "흰 박스" 제거 (전역 강제)
   - Streamlit DOM 구조상 래퍼(div) 안에 안 들어가는 케이스가 있어 전역으로 숨김
   ========================================================= */
div[data-testid="stTextInput"],
div[data-testid="stTextInputRoot"],
div[data-testid="stTextInputContainer"],
div[data-baseweb="base-input"],
div[data-baseweb="input"] {{
  display: none !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  border: 0 !important;
}}

/* ✅ Browse files 후 의미없는 문서표시(업로더 파일 리스트) 숨김 */
div[data-testid="stFileUploaderFile"] {{ display:none !important; }}
div[data-testid="stFileUploader"] ul {{ display:none !important; }}
div[data-testid="stFileUploader"] li {{ display:none !important; }}

/* ---------- Header ---------- */
.header-wrap{{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: var(--s3);
  box-shadow: var(--shadow);
}}
.header-topline{{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
}}
.brand-small{{
  font-size: 13px;
  font-weight: 900;
  color: #475467;
}}
.pro-btn a{{ text-decoration:none; }}
.pro-btn .pill{{
  background: var(--primary);
  color: #fff;
  padding: 12px 18px;
  border-radius: 12px;
  font-weight: 950;
  min-width: 160px;
  text-align:center;
  display:inline-block;
  box-shadow: 0 8px 18px rgba(17,24,39,.18);
}}
.pro-btn .pill:hover{{ filter: brightness(0.92); }}

/* ✅ (2) 제목 46pt */
.main-title{{
  margin-top: 10px;
  font-size: 46px;
  font-weight: 950;
  color: var(--text);
  text-align:center;
  line-height: 1.10;
}}

.sub-title{{
  margin-top: 10px;
  text-align:center;
  font-size: 18px;
  font-weight: 650;
  color: var(--danger);
}}

.guide{{
  margin-top: var(--s2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: var(--s2);
  text-align:center;
  background:#fff;
}}
.guide .guide-title{{
  font-size: 30px;
  font-weight: 950;
  color:#111827;
  margin-bottom: 14px;
}}
.guide .steps{{
  display:flex;
  justify-content:center;
  align-items:center;
  gap: 28px;
  flex-wrap: wrap;
}}
.guide .step{{
  font-size: 18px;
  font-weight: 850;
  color:#344054;
  white-space: nowrap;
}}

/* ---------- Top banner ---------- */
.top-banner-wrap{{
  margin: var(--s4) auto var(--s4) auto;
  max-width: 1320px;
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow:hidden;
  box-shadow: var(--shadow);
  height: {TOP_BANNER_H}px;
}}
.top-banner-wrap a{{ display:block; width:100%; height:100%; }}
.top-banner-wrap img{{
  width:100%;
  height:100%;
  object-fit: cover;
  object-position: center;
  display:block;
}}

/* ---------- Ads ---------- */
.ad-wrapper{{
  width:100%;
  display:flex;
  justify-content:center;
  margin-top: var(--s4);
}}
.ad-box{{
  width: 100%;
  max-width: {AD_W}px;
  height: auto;
  border:1px solid var(--border);
  border-radius:14px;
  overflow:hidden;
  background:#fff;
  box-shadow: var(--shadow);
}}
.ad-box a{{ display:block; width:100%; }}
.ad-box img{{
  width:100%;
  height:auto;
  object-fit: contain;  /* ✅ 가로 잘림 방지 */
  object-position: center;
  display:block;
}}

/* ---------- Work Area ---------- */
.section-card{{
  background:#fff;
  border:1px solid var(--border);
  border-radius:16px;
  box-shadow: var(--shadow);
  padding: var(--s3);
  margin-top: var(--s4);
}}
.section-title{{
  font-size: 22px;
  font-weight: 950;
  color: var(--text);
  margin-bottom: var(--s1);
}}
.small-muted{{
  font-size: 13px;
  color: var(--muted);
  font-weight: 800;
}}
.hr-soft{{
  height:1px;
  background: var(--border);
  margin: var(--s2) 0 var(--s2) 0;
}}

/* ---------- File uploader ---------- */
div[data-testid="stFileUploader"] label {{ display:none !important; }}
div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {{ display:none !important; }}
div[data-testid="stFileUploader"] > div {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  margin: 0 !important;
  min-height: 0 !important;
}}
div[data-testid="stFileUploaderDropzone"] {{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: #0b1220 !important;
  padding: 18px !important;
}}
div[data-testid="stFileUploaderDropzone"] * {{ color: #fff !important; }}
div[data-testid="stFileUploaderDropzone"] ul {{ display:none !important; }}
div[data-testid="stFileUploaderDropzone"] button {{
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  color: #fff !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
}}
div[data-testid="stFileUploaderDropzone"] button:hover {{
  background: rgba(255,255,255,.14) !important;
}}

/* 버튼 hover/active 블랙90 */
.stButton>button{{
  border-radius: 12px !important;
  font-weight: 950 !important;
  height: 54px !important;
  border: 0 !important;
  background: var(--primary) !important;
  color: #fff !important;
  transition: background .15s ease, filter .15s ease;
}}
.stButton>button:hover{{
  background: var(--primaryHover) !important;
  color: #fff !important;
}}
.stButton>button:active{{
  background: var(--primaryHover) !important;
  color:#fff !important;
  filter: brightness(0.95) !important;
}}
.stButton>button:focus{{
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(17,24,39,.12) !important;
}}

div[data-testid="stDownloadButton"] > button{{
  background: var(--primary) !important;
  color: #fff !important;
  border: 0 !important;
  height: 52px !important;
  border-radius: 12px !important;
  font-weight: 950 !important;
}}
div[data-testid="stDownloadButton"] > button:hover{{
  background: var(--primaryHover) !important;
  color: #fff !important;
}}

.file-name{{
  font-weight: 900;
  color: #344054;
  font-size: 14px;
  overflow:hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 520px;
}}
.small-btn button{{
  height: 40px !important;
  min-width: 44px !important;
  padding: 0 12px !important;
  border-radius: 10px !important;
  background: var(--primary) !important;
  color: #fff !important;
  font-weight: 950 !important;
}}
.small-btn button:hover{{
  background: var(--primaryHover) !important;
  color:#fff !important;
}}

.notice-box{{
  background: var(--greenBg);
  border: 1px solid var(--greenBorder);
  border-radius: 12px;
  padding: 14px 16px;
  margin-top: 14px;
  font-weight: 950;
  color: var(--greenText);
  font-size: 15px;
}}
.notice-box b{{ color: var(--greenText); }}

.marketing{{
  margin-top: var(--s4);
  background:#f6f7f9;
  border:1px solid var(--border);
  border-radius:14px;
  padding: var(--s3);
  text-align:center;
  box-shadow: var(--shadow);
}}
.marketing .headline{{
  text-align:center;
  font-size: 28px;
  font-weight: 950;
  color: var(--greenText);
  margin-bottom: 12px;
}}
.marketing .body{{
  color: var(--greenText);
  font-weight: 850;
  line-height: 1.65;
}}
.pro-strong{{
  font-size: 15.4px;
  font-weight: 900;
  color:#111827;
}}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================
def safe_open_image(file_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    return img

def bytes_hash(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def add_uploaded_files(uploaded) -> None:
    if not uploaded:
        return
    for uf in uploaded:
        if len(st.session_state["files"]) >= MAX_FILES:
            break
        file_bytes = uf.read()
        h = bytes_hash(file_bytes)
        if h in st.session_state["seen_hashes"]:
            continue
        try:
            img = safe_open_image(file_bytes)
        except Exception:
            continue
        st.session_state["files"].append((uf.name, file_bytes, img))
        st.session_state["seen_hashes"].add(h)

def move_file(idx: int, direction: int) -> None:
    files = st.session_state["files"]
    new_idx = idx + direction
    if 0 <= idx < len(files) and 0 <= new_idx < len(files):
        files[idx], files[new_idx] = files[new_idx], files[idx]
        st.session_state["files"] = files

def rebuild_seen_hashes() -> None:
    st.session_state["seen_hashes"] = {bytes_hash(b) for (_n, b, _i) in st.session_state["files"]}

def remove_file(idx: int) -> None:
    files = st.session_state["files"]
    if 0 <= idx < len(files):
        files.pop(idx)
        st.session_state["files"] = files
        rebuild_seen_hashes()

def request_reset() -> None:
    st.session_state[RESET_FLAG_KEY] = True
    st.rerun()

def img_to_data_uri(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "png" if ext == "png" else "jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{b64}"

def render_ad_box(img_path: str) -> None:
    uri = img_to_data_uri(img_path)
    st.markdown('<div class="ad-wrapper">', unsafe_allow_html=True)
    if uri:
        st.markdown(
            f"""
<div class="ad-box">
  <a href="{MISHARP_URL}" target="_blank" rel="noopener">
    <img src="{uri}" alt="ad">
  </a>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

def resize_to_width(im: Image.Image, target_w: int) -> Image.Image:
    if im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    if w == target_w:
        return im
    new_h = max(1, int(h * (target_w / float(w))))
    return im.resize((target_w, new_h), Image.LANCZOS)

def build_stacked_image_fixed_width(images: List[Image.Image], gap: int, target_w: int) -> Image.Image:
    resized = [resize_to_width(im, target_w) for im in images]
    total_h = sum(im.size[1] for im in resized) + gap * (len(resized) - 1 if len(resized) > 1 else 0)
    canvas = Image.new("RGB", (target_w, total_h), (255, 255, 255))
    y = 0
    for im in resized:
        canvas.paste(im, (0, y))
        y += im.size[1] + gap
    return canvas

# =========================================================
# HEADER
# =========================================================
st.markdown(
    f"""
<div class="header-wrap">
  <div class="header-topline">
    <div class="brand-small">MISHARP DETAIL PAGE MAKER V1 - FREE VERSION</div>
    <div class="pro-btn">
      <a href="{PRO_APPLY_URL}" target="_blank" rel="noopener"><span class="pill">PRO신청</span></a>
    </div>
  </div>

  <div class="main-title">MS 쇼핑몰 상세페이지 자동 생성기</div>
  <div class="sub-title">상세페이지 이미지를 자동으로 생성하여 디자이너의 단순업무시간을 대폭 줄여드립니다.</div>

  <div class="guide">
    <div class="guide-title">*사용방법*</div>
    <div class="steps">
      <div class="step">1) 이미지 업로드(최대 10개)</div>
      <div class="step">2) 이미지 간격(0~300px) 조정</div>
      <div class="step">3) 생성하기 버튼 클릭 → 하단 저장하기 버튼 클릭하면 완성</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# TOP BANNER
# =========================================================
top_uri = img_to_data_uri(TOP_BANNER_PATH)
if top_uri:
    st.markdown(
        f"""
<div class="top-banner-wrap">
  <a href="{MISHARP_URL}" target="_blank" rel="noopener">
    <img src="{top_uri}" alt="top banner">
  </a>
</div>
""",
        unsafe_allow_html=True,
    )

# =========================================================
# MAIN LAYOUT
# =========================================================
left_col, center_col, right_col = st.columns([1.2, 3, 1.2], gap="large")

with left_col:
    render_ad_box(AD_LEFT_PATH)

with right_col:
    render_ad_box(AD_RIGHT_PATH)

with center_col:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">파일선택</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted">JPG/PNG 파일을 업로드하세요. 최대 10개까지 가능합니다.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hr-soft"></div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "이미지 업로드",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key=current_uploader_key(),  # ✅ nonce 기반 키
    )
    if uploaded:
        add_uploaded_files(uploaded)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    cA, cB = st.columns([2, 1.2], gap="medium")
    with cA:
        gap = st.slider("이미지 간격 (0~300PX)", 0, 300, 50)
    with cB:
        generate_clicked = st.button("생성하기 (JPG)", use_container_width=True)

    if generate_clicked:
        st.session_state["just_generated"] = False
        if len(st.session_state["files"]) == 0:
            st.warning("먼저 이미지를 업로드해주세요.")
        else:
            imgs = [t[2] for t in st.session_state["files"]]
            result_img = build_stacked_image_fixed_width(imgs, gap, OUTPUT_WIDTH)
            buf = io.BytesIO()
            result_img.save(buf, format="JPEG", quality=95)
            st.session_state["result_bytes"] = buf.getvalue()
            st.session_state["result_filename"] = "detail_page.jpg"
            st.session_state["just_generated"] = True

    if st.session_state.get("just_generated", False):
        st.markdown(
            """
<div class="notice-box">
  <b>생성 완료!</b> 이제 아래 <b>[저장하기]</b> 버튼으로 다운로드하세요.
</div>
""",
            unsafe_allow_html=True,
        )

    if st.session_state.get("result_bytes"):
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.download_button(
            label="저장하기",
            data=st.session_state["result_bytes"],
            file_name=st.session_state["result_filename"],
            mime="image/jpeg",
            use_container_width=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size:16px;'>업로드 파일명</div>", unsafe_allow_html=True)

    if len(st.session_state["files"]) == 0:
        st.info("아직 업로드된 파일이 없습니다.")
    else:
        for i, (name, _bts, _img) in enumerate(st.session_state["files"]):
            row_cols = st.columns([6, 1.2, 1.2, 1.2], gap="small")
            with row_cols[0]:
                st.markdown(f"<div class='file-name'>{i+1}. {name}</div>", unsafe_allow_html=True)
            with row_cols[1]:
                st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
                if st.button("▼", key=f"down_{i}", use_container_width=True):
                    move_file(i, +1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with row_cols[2]:
                st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
                if st.button("▲", key=f"up_{i}", use_container_width=True):
                    move_file(i, -1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with row_cols[3]:
                st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
                if st.button("X", key=f"remove_{i}", use_container_width=True):
                    remove_file(i)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='small-muted' style='margin-top: 18px;'>*FREE 버전에서 미리보기는 지원되지 않습니다.</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 26px;'></div>", unsafe_allow_html=True)

    reset_cols = st.columns([1, 1, 1])
    with reset_cols[2]:
        st.button("초기화", use_container_width=True, on_click=request_reset)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 박스들 (이전 구성 유지)
# =========================================================
st.markdown("<div style='height: var(--s4);'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="section-card">
  <div class="section-title">MS 상세페이지 생성기 사용안내</div>
  <div style="color:#344054; font-weight:750; line-height:1.85; font-size:14px;">
    1. 사전 보정을 끝낸 상세피이지용 이미지를 파일선택에서 선택(최대 10개 가능/5개 정도 권장)<br>
    2. 이미지 간격 버튼 이용해 이미지간 세로 간격 조정(0~300PX까지 선택가능 / 1개 상세페이지당 일괄 적용됨)<br>
    &nbsp;&nbsp;&nbsp;가로는 900PX로 고정되며, 업로드한 이미지는 좌우여백없이 배치됩니다.<br>
    3. 업로드 파일 명 옆 상하버튼, 삭제 버튼 이용해 이미지 순서 정리<br>
    4. [생성하기] 버튼 클릭 → 생성완료 후 [저장하기] 버튼으로 상세페이지 JPG파일 다운로드<br>
    4. 본 프리버전에서 상세페이지 내 텍스트를 구성하고자 할 경우, 텍스트 편집된 이미지를 추가하는 방식으로 활용하세요.<br>
    5. 새로운 작업을 시작할 때는 초기화 클릭
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height: var(--s4);'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="marketing">
  <div class="headline">20년차 온라인쇼핑몰 대표가 직접 만든 상세페이지 자동화툴</div>
  <div class="body">
    MS 상세페이지 생성기는 20년차 여성의류 인터넷 쇼핑몰 대표가 사내에서 사용하기 위해 직접 제작한 프로그램으로<br>
    실제 온라인 쇼핑몰 디자인 작업에 적용하고 있으며, 디자이너의 요구사항을 최대한 반영하여 구현한 최고의 툴입니다.<br>
    MS 업무툴로 단순업무 시간은 줄이고 상세페이지의 퀄리티는 더 높이세요.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height: var(--s4);'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="section-card">
  <div class="section-title">PSD(고급개체 레이어)가 필요하신가요?</div>
  <div style="color:#344054; font-weight:800; line-height:1.85; font-size:14px;">
    <span class="pro-strong">MS PRO는 수정 가능한 상세페이지 PSD 다운로드가 가능합니다. (레이어/고급개체 기반)</span><br><br>
    <span style="color:#e60012; font-weight:950;">→ PSD로 빠르고 해상도 높은 작업이 필요할 때</span><br>
    <span style="color:#e60012; font-weight:950;">→ 고급개체(SMART OBJECTS) 레이어 작업이 필요할 때</span><br>
    <span style="color:#e60012; font-weight:950;">→ 반복적인 템플릿이 필요할 때</span><br>
    <span style="color:#e60012; font-weight:950;">→ 업로드 파일 미리보기 제공 등 좀 더 다양한 기능이 필요할 때</span><br><br>
    <span class="pro-strong">MS PRO는 상세페이지 웹디자이너에게 최고의 도구가 되어줍니다.</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height: var(--s4);'></div>", unsafe_allow_html=True)

st.markdown(
    "<div class='section-title' style='font-size:24px; font-weight:950; margin-top:0;'>PRO버전은 디자이너를 위한 가장 효율적인 툴을 함께 제공합니다.</div>",
    unsafe_allow_html=True
)

st.markdown("<div style='height: var(--s2);'></div>", unsafe_allow_html=True)

t1, t2, t3 = st.columns(3, gap="medium")
with t1:
    st.markdown(
        """
<div class="section-card" style="margin-top:0;">
  <div style="font-size:16px; font-weight:950; color:#101828; margin-bottom:8px;">GIF 자동 생성기</div>
  <div style="font-size:13px; color:#667085; font-weight:780; line-height:1.55;">
    여러 이미지를 업로드하면 고화질 GIF를 자동으로 생성합니다.<br>
    프레임 간격/속도 최적화로 ‘움직이는 배너’ 제작 시간을 확 줄여드립니다.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with t2:
    st.markdown(
        """
<div class="section-card" style="margin-top:0;">
  <div style="font-size:16px; font-weight:950; color:#101828; margin-bottom:8px;">썸네일 메이커</div>
  <div style="font-size:13px; color:#667085; font-weight:780; line-height:1.55;">
    쇼핑몰 썸네일 규격에 맞춰 자동 리사이즈/중앙정렬을 지원합니다.<br>
    여백/크롭 문제를 최소화해 ‘바로 업로드 가능한 썸네일’을 만들어드립니다.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
with t3:
    st.markdown(
        """
<div class="section-card" style="margin-top:0;">
  <div style="font-size:16px; font-weight:950; color:#101828; margin-bottom:8px;">이미지 자르기 툴</div>
  <div style="font-size:13px; color:#667085; font-weight:780; line-height:1.55;">
    상세페이지용 고정비율 컷팅과 흰여백 제거를 빠르게 처리합니다.<br>
    피사체 중심 유지 기준으로 작업 효율을 극대화합니다.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
<div style="text-align:center; margin-top: var(--s4);">
  <a href="{PRO_APPLY_URL}" target="_blank" rel="noopener"
     style="background: var(--primary); color:#fff; padding: 14px 42px; border-radius: 14px;
            font-weight: 950; font-size: 18px; text-decoration:none; display:inline-block;
            box-shadow: 0 10px 24px rgba(17,24,39,.22);">
    PRO 신청하기
  </a>
</div>

<div style="margin-top: var(--s3); text-align:center; background:#fff; border:1px solid var(--border);
            border-radius:14px; padding: var(--s3); box-shadow: var(--shadow);">
  <div style="font-size: 16px; font-weight: 950; color: var(--text);">사용 및 PRO 문의</div>
  <div style="font-size: 20px; font-weight: 950; color: var(--danger); margin-top: 6px;">misharpmail@naver.com</div>
</div>

<div style="margin-top: var(--s3); text-align:center; font-size: 13px; color:#98A2B3; font-weight: 700;">
  © 2006-2026 MISHARP. All Rights Reserved.
</div>
""",
    unsafe_allow_html=True,
)
