# 프로젝트 개발 이력

## 1. 초기 설정
- FastAPI 기반 백엔드 서버 구축
- SQLite 데이터베이스 연결
- 기본 API 엔드포인트 구현

## 2. 비디오 관리 기능
- 비디오 파일 자동 스캔 구현
- 메타데이터 추출 (길이, 생성일)
- 파일 변경 감지 및 자동 업데이트

## 3. 썸네일 시스템
- WebP 포맷 썸네일 생성
- 비동기 워커 시스템 구현
- 썸네일 생성 최적화

## 4. 태그 시스템
- 태그 CRUD 기능 구현
- info 파일 기반 메타데이터 저장
- AND/OR 태그 검색 구현

## 5. 설정 시스템
- YAML 기반 설정 파일 구현
- 커맨드라인 설정 지원
- DB 파일 위치 설정 기능 추가

## 6. 프론트엔드 개발
- React + TypeScript 기반 UI 구현
- 비디오 상세 페이지 개발
- 태그 관리 UI 구현

## 7. 컨테이너화
- Docker 컨테이너 구성
- 볼륨 마운트 설정
- 컨테이너-호스트 경로 매핑

## 8. 플레이어 시스템
- TCP 소켓 기반 플레이어 모니터 구현
- 플랫폼별 기본 플레이어 실행 지원
- 비동기 소켓 서버 구현 