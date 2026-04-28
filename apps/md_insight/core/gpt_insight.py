import os
import streamlit as st
from openai import OpenAI
from utils.db import get_names_for_insight, get_summary_stats


def _get_openai_key():
    key = None
    try:
        key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass
    return key or os.getenv("OPENAI_API_KEY")


def _client_or_message():
    key = _get_openai_key()
    if not key:
        return None, "GPT 기능 안내: OPENAI_API_KEY 설정 필요"
    return OpenAI(api_key=key), None


def generate_insight():
    names = get_names_for_insight(limit=150)
    if not names:
        return "먼저 상품 RADAR 또는 경쟁사 RADAR에서 데이터를 수집해 주세요."

    client, message = _client_or_message()
    if message:
        return message

    stats = get_summary_stats()

    by_source = "\n".join([f"- {src}: {cnt}건" for src, cnt in stats["by_source"][:10]])
    by_category = "\n".join([f"- {cat}: {cnt}건" for cat, cnt in stats["by_category"][:30]])
    by_mall = "\n".join([f"- {mall}: {cnt}건" for mall, cnt in stats["by_mall"][:30]])

    prompt = f"""
아래는 최근 수집된 패션 상품 데이터입니다.

[전체 수집 개수]
{stats["total"]}건

[소스별 개수]
{by_source}

[카테고리별 개수]
{by_category}

[몰별 개수]
{by_mall}

[최근 상품명]
{"\\n".join(names)}

이 데이터만 바탕으로 한국어로 정리해 주세요.
추측은 하되, 데이터에서 읽히는 패턴 중심으로 작성하세요.

1. 핵심 키워드 7개
2. 반복되는 스타일/핏/소재 특징
3. 가격대 해석
4. 포털/경쟁사 기준 지금 강한 상품군
5. 다음 상품기획 제안 7개
6. 상세페이지/광고카피에 바로 쓸 표현 10개
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


def generate_sales_planner(keyword):
    client, message = _client_or_message()
    if message:
        return message

    prompt = f"""
주제: {keyword}

아래 형식으로만 작성하세요. 제목과 순서, 항목명을 반드시 유지하세요.

[상품기획서]

1. 기획 배경
- 

2. 타깃 고객
- 

3. 상품 컨셉
- 

4. 핵심 판매 포인트 (7개)
- 
- 
- 

5. 추천 소재/핏/컬러
- 

6. 가격 전략
- 

7. 상품명 제안 (7개)
1) 
2) 
3) 
4) 
5) 
6) 
7) 

8. 상세페이지 구성
- 

9. 광고 카피 (10개)
1) 
2) 
3) 
4) 
5) 
6) 
7) 
8) 
9) 
10) 

10. 숏폼 후킹 문구 (10개)
1) 
2) 
3) 
4) 
5) 
6) 
7) 
8) 
9) 
10) 

11. 리스크 및 보완
- 
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content