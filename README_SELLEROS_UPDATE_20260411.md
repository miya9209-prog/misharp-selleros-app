
# MISHARP SELLER OS 수정본

이번 수정본 반영사항
- 좌측 메뉴를 대분류 제목 + 하위 메뉴 노출 구조로 개편
- 최신 `page-builder-main.zip` 레포로 `상세페이지 기획/설명작성` 교체
- 신규 앱 3종 추가
  - 챗봇 관리 (`apps/miya_manager`)
  - DB 생성기 (`apps/db_maker`)
  - 템플릿 생성 OS (`apps/template_os`)
- 각 페이지 하단 공통 푸터 문구 추가
- 기능별 사용법을 사이드바 메뉴 안의 별도 페이지로 이동

## 배포 순서
1. 기존 Seller OS 작업 폴더를 백업합니다.
2. 이 폴더 전체를 GitHub Desktop에서 기존 레포에 덮어씁니다.
3. 변경 파일이 잡히면 Commit -> Push 합니다.
4. Streamlit Cloud에서 Reboot 합니다.

## 주의
- 기존 PRO 코드 해시 목록은 유지했습니다.
- 새 앱은 Seller OS 내부에서 임베드 실행되도록 연결했습니다.
- 일부 서브앱은 원본 자체 UI/CSS를 가지고 있어서 내부 스타일은 각 앱 기준으로 보일 수 있습니다.
