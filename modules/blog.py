import streamlit as st

def render(shared):
    """Blog generator (prompt-first). No API keys required."""
    st.subheader("블로그 글 생성 (프롬프트 제공)")
    inp = shared.get("inputs", {})
    if not inp.get("상품명"):
        st.info("먼저 상단 공통 입력폼에서 상품 정보를 저장해 주세요.")
        return

    prompt = f"""너는 4050 여성 패션 쇼핑몰 '미샵'의 블로그 에디터다.
목표: 검색 유입과 구매 전환을 높이는 글을 쓴다.
톤: 전문가 지식을 대중적이고 캐주얼하게 전달. 이모지 삭제.
구성:
1) 최상단 요약 300자
2) 서론(공감+주제소개)
3) 중요 키워드 설명
4) 서술형+리스팅 병행
5) 관련 상품 제안(자사 상품 중심)
6) 최하단 3줄 요약
7) 관련 태그 키워드 20개

[상품 정보]
상품명: {inp.get('상품명','')}
가격: {inp.get('가격','')}
소재: {inp.get('소재','')}
핏/사이즈: {inp.get('핏','')} / {inp.get('사이즈','')}
컬러: {inp.get('컬러','')}
특장점: {inp.get('특장점5줄','')}
키워드: {inp.get('키워드','')}
금칙어: {inp.get('금칙어','')}

[요구]
- 글 전체는 4000자 내외
- 문단마다 자연스럽게 연결 문장 포함
- 단어 옆 ':' 사용 시 한 칸 띄움 (예: 키워드 : )
"""
    st.text_area("ChatGPT/LLM에 붙여넣을 프롬프트", value=prompt, height=320)
    if st.button("블로그 프롬프트 TXT로 저장", use_container_width=True):
        data = prompt.encode("utf-8")
        shared.setdefault("outputs", {})["blog_prompt"] = {
            "filename": "blog_prompt.txt",
            "data": data,
            "mime": "text/plain",
        }
        st.success("outputs에 저장되었습니다. 전체 ZIP에 포함됩니다.")
