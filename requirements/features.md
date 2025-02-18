# 주요 기능 요구사항

## 1. 비디오 관리
- [x] 설정된 디렉토리의 비디오 파일 자동 스캔
- [x] 비디오 메타데이터 추출 (길이, 생성일)
- [x] 파일 변경 감지 및 자동 업데이트
- [x] 지원 포맷: mp4, avi, mkv, mov
- [x] 컨테이너 모드에서 호스트 경로 매핑

## 2. 썸네일 시스템
- [x] WebP 포맷 썸네일 자동 생성
- [x] 비동기 워커를 통한 썸네일 생성
- [x] 썸네일 크기, FPS 등 설정 가능
- [x] 썸네일 로딩 실패 시 대체 UI 표시

## 3. 태그 시스템
- [x] 비디오에 다중 태그 지원
- [x] 태그 기반 AND/OR 검색
- [x] info 파일에 태그 정보 저장
- [x] 태그 CRUD API

## 4. 설정 시스템
- [x] YAML 기반 설정 파일
- [x] 커맨드라인 설정 지원
- [x] DB 파일 위치 설정
- [x] 썸네일 설정 관리
- [x] 컨테이너 모드 설정

## 5. 프론트엔드
- [x] 반응형 디자인
- [x] 키보드 네비게이션
- [x] 태그 관리 UI
- [x] 페이지네이션

## 6. 플레이어 연동
- [x] TCP 소켓 기반 통신
- [x] 플랫폼별 기본 플레이어 실행
- [x] 비동기 소켓 서버 