import streamlit as st
from .gif_utils import build_gif_from_images
from .video_utils import build_gif_from_video_ffmpeg

# ===============================

def render(shared):
    """Embedded render function for Seller OS tabs.

    shared: dict-like for shared inputs & outputs.
    """
    st.markdown(
        """
    <style>
    footer {visibility: hidden;}
    div[data-testid="stAppViewContainer"] .main { padding-bottom: 90px; }

    .misharp-footer {
      position: fixed;
      left: 0;
      bottom: 0;
      width: 100%;
      padding: 12px 16px;
      background: rgba(0,0,0,0.78);
      color: rgba(255,255,255,0.92);
      border-top: 1px solid rgba(255,255,255,0.12);
      font-size: 12px;
      z-index: 999999;
      backdrop-filter: blur(6px);
    }
    </style>
    <div class="misharp-footer">© 2026 미샵(MISHARP) · 실무 자동화 도구</div>
    """,
        unsafe_allow_html=True,
    )

    st.title("미샵 GIF 생성기")
    st.caption("이미지→GIF / 동영상→GIF (웹용 최적화)")

    tab_img, tab_vid = st.tabs(["이미지 → GIF", "동영상 → GIF"])

    # ===============================
    # ✅ session_state 기본값
    # ===============================
    defaults = {
        "uploaded_items": [],      # [{"name":..., "bytes":...}, ...]
        "img_upload_token": None,  # 업로드가 '진짜 바뀐 경우'만 갱신
        "selected_idx": 0,         # ✅ 썸네일 선택 인덱스

        "vid_fps": 8,
        "vid_width": 450,
        "vid_colors": 64,
        "vid_dither": "none",
        "vid_loop": True,
        "vid_clip_on": True,
        "vid_clip_start": 0.0,
        "vid_clip_end": 3.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ===============================
    # Sidebar
    # ===============================
    with st.sidebar:
        st.header("이미지 → GIF 옵션 (포토샵급)")

        delay = st.slider("프레임 간격(초)", 0.5, 10.0, 1.0, 0.5, key="img_delay")
        loop_forever_img = st.checkbox("무한 루프(Forever)", value=True, key="img_loop")
        unify_canvas = st.checkbox("사이즈 섞이면 자동 통일(패딩)", value=True, key="img_unify")

        max_width_img = st.selectbox(
            "최대 가로폭",
            ["원본 유지", 450, 720, 900, 1080],
            index=1,  # ✅ 기본값 450
            key="img_max_width",
        )
        max_width_img_val = None if max_width_img == "원본 유지" else int(max_width_img)

        # ✅ 핵심: 포토샵 Save for Web 느낌 옵션
        img_colors = st.selectbox(
            "색상 수(팔레트)",
            [256, 128, 96, 64],
            index=0,  # ✅ 기본값 256
            key="img_colors",
        )
        img_dither = st.selectbox(
            "디더링",
            ["floyd_steinberg", "bayer", "none"],
            index=0,  # ✅ 기본값 floyd_steinberg
            key="img_dither",
        )

        if max_width_img == "원본 유지":
            st.warning("원본 유지 + GIF는(256색 제한) 사진이 어느 정도 뭉개질 수 있어요. 품질 우선이면 720~900 추천!")

        st.divider()
        st.header("동영상 → GIF 옵션 (초경량 기본)")

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("초경량", use_container_width=True, key="preset_ultra"):
                st.session_state.update(dict(vid_width=450, vid_fps=8, vid_colors=64, vid_dither="none"))
        with c2:
            if st.button("인스타", use_container_width=True, key="preset_insta"):
                st.session_state.update(dict(vid_width=540, vid_fps=10, vid_colors=96, vid_dither="none"))
        with c3:
            if st.button("고퀄", use_container_width=True, key="preset_hq"):
                st.session_state.update(dict(vid_width=720, vid_fps=12, vid_colors=128, vid_dither="floyd"))

        st.slider("FPS", 5, 20, step=1, key="vid_fps")
        st.selectbox("최대 가로폭", [360, 450, 540, 720, 900, "원본 유지"], key="vid_width")
        st.selectbox("색상수(팔레트)", [64, 96, 128, 256], key="vid_colors")
        st.selectbox("디더링", ["none", "floyd"], key="vid_dither")
        st.checkbox("무한 루프(Forever)", key="vid_loop")

        st.divider()
        st.checkbox("구간 자르기(추천)", key="vid_clip_on")
        if st.session_state.vid_clip_on:
            st.number_input("시작(초)", min_value=0.0, step=0.5, key="vid_clip_start")
            st.number_input("종료(초)", min_value=0.5, step=0.5, key="vid_clip_end")

        st.divider()
        st.caption("© 2026 미샵(MISHARP) · 실무 자동화 도구")

    # ===============================
    # TAB 1: 이미지 → GIF
    # ===============================
    with tab_img:
        st.subheader("이미지 → GIF")
        st.caption("업로드 후 썸네일에서 선택 → 아래 버튼으로 순서 이동/삭제. (한 줄 6개씩)")

        files = st.file_uploader(
            "이미지 여러 장 업로드 (JPG/PNG/GIF/WEBP/BMP/TIFF/PSD)",
            type=["jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff", "tif", "psd"],
            accept_multiple_files=True,
            key="img_uploader",
        )

        # ✅ 업로드가 '진짜 바뀐 경우에만' 갱신 (정렬 유지 핵심)
        if files:
            token = tuple((f.name, getattr(f, "size", None)) for f in files)
            if st.session_state.img_upload_token != token:
                st.session_state.img_upload_token = token
                st.session_state.uploaded_items = [{"name": f.name, "bytes": f.getvalue()} for f in files]
                st.session_state.selected_idx = 0

        if not st.session_state.uploaded_items:
            st.info("이미지를 업로드해 주세요.")
        else:
            items = list(st.session_state.uploaded_items)

            # selected_idx 안전 처리
            if st.session_state.selected_idx < 0:
                st.session_state.selected_idx = 0
            if st.session_state.selected_idx >= len(items):
                st.session_state.selected_idx = max(0, len(items) - 1)

            st.markdown("### 업로드된 이미지 순서 (썸네일 6개씩)")
            cols_per_row = 6
            thumb_w = 140

            # --- 썸네일 그리드 ---
            for row_start in range(0, len(items), cols_per_row):
                cols = st.columns(cols_per_row, gap="small")
                for j, col in enumerate(cols):
                    i = row_start + j
                    if i >= len(items):
                        break
                    with col:
                        try:
                            st.image(items[i]["bytes"], width=thumb_w)
                        except Exception:
                            st.write("미리보기 불가")

                        label = "✅" if i == st.session_state.selected_idx else "선택"
                        if st.button(label, key=f"pick_{i}", use_container_width=True):
                            st.session_state.selected_idx = i
                            st.rerun()

            st.divider()

            # --- 선택된 항목 조작(↑↓/삭제) ---
            i = st.session_state.selected_idx

            c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 6])
            with c1:
                st.write(f"선택: **{i+1}. {items[i]['name']}**")

            with c2:
                if st.button("⬆ 위로", disabled=(i == 0), use_container_width=True, key="sel_up"):
                    items[i - 1], items[i] = items[i], items[i - 1]
                    st.session_state.uploaded_items = items
                    st.session_state.selected_idx = i - 1
                    st.rerun()

            with c3:
                if st.button("⬇ 아래로", disabled=(i == len(items) - 1), use_container_width=True, key="sel_down"):
                    items[i + 1], items[i] = items[i], items[i + 1]
                    st.session_state.uploaded_items = items
                    st.session_state.selected_idx = i + 1
                    st.rerun()

            with c4:
                if st.button("🗑 삭제", use_container_width=True, key="sel_del"):
                    items.pop(i)
                    st.session_state.uploaded_items = items
                    st.session_state.selected_idx = max(0, min(i, len(items) - 1))
                    st.rerun()

            with c5:
                if st.button("🧹 목록 초기화", key="img_clear", use_container_width=True):
                    st.session_state.uploaded_items = []
                    st.session_state.img_upload_token = None
                    st.session_state.selected_idx = 0
                    st.rerun()

            st.caption("정렬 후 **GIF 만들기**를 누르면, 현재 순서대로 GIF가 생성됩니다.")
            st.divider()

            if st.button("GIF 만들기", type="primary", key="img_make"):
                ordered_pairs = [(x["name"], x["bytes"]) for x in st.session_state.uploaded_items]

                with st.spinner("포토샵급 고화질 GIF 생성 중..."):
                    gif_bytes = build_gif_from_images(
                        files=ordered_pairs,
                        delay_sec=float(delay),
                        loop_forever=bool(loop_forever_img),
                        unify_canvas=bool(unify_canvas),
                        max_width=max_width_img_val,
                        colors=int(img_colors),
                        dither=str(img_dither),
                    )

                if not gif_bytes:
                    st.error("GIF 생성 실패(입력 이미지가 비어있음).")
                else:
                    st.success("완료! 미리보기 & 다운로드")

                    # ✅ 너무 크게 뜨는 문제 방지
                    st.image(gif_bytes, width=450)

                    st.download_button(
                        "GIF 다운로드",
                        data=gif_bytes,
                        file_name="misharp_images.gif",
                        mime="image/gif",
                        key="img_download",
                    )

    # ===============================
    # TAB 2: 동영상 → GIF
    # ===============================
    with tab_vid:
        st.subheader("동영상 → GIF")
        st.caption("동영상은 용량 우선 최적화 (기본값: 450 / 8fps / 64 / none)")

        vfile = st.file_uploader(
            "동영상 업로드 (MP4/MOV/WEBM 등)",
            type=["mp4", "mov", "m4v", "avi", "webm"],
            accept_multiple_files=False,
            key="vid_uploader",
        )

        if st.button("동영상 GIF 만들기", type="primary", disabled=not vfile, key="vid_make"):
            if st.session_state.vid_clip_on and st.session_state.vid_clip_end <= st.session_state.vid_clip_start:
                st.error("구간 설정이 잘못되었습니다. (종료 > 시작)")
            else:
                max_width_vid_val = None if st.session_state.vid_width == "원본 유지" else int(st.session_state.vid_width)

                with st.spinner("동영상 → GIF 변환 중(팔레트 최적화 + 용량 절감)..."):
                    gif_bytes = build_gif_from_video_ffmpeg(
                        video_bytes=vfile.getvalue(),
                        fps=int(st.session_state.vid_fps),
                        max_width=max_width_vid_val,
                        loop_forever=bool(st.session_state.vid_loop),
                        start_sec=float(st.session_state.vid_clip_start) if st.session_state.vid_clip_on else None,
                        end_sec=float(st.session_state.vid_clip_end) if st.session_state.vid_clip_on else None,
                        colors=int(st.session_state.vid_colors),
                        dither=str(st.session_state.vid_dither),
                    )

                size_mb = len(gif_bytes) / (1024 * 1024)
                st.success(f"완료! (약 {size_mb:.1f} MB)")

                st.image(gif_bytes, width=450)

                st.download_button(
                    "GIF 다운로드",
                    data=gif_bytes,
                    file_name="misharp_video.gif",
                    mime="image/gif",
                    key="vid_download",
                )

                if size_mb > 20:
                    st.warning("용량이 큰 편입니다. **가로폭 360~450 / FPS 8~10 / 색상수 64** 로 낮추면 확 줄어듭니다.")