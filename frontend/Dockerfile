# Build stage
FROM node:18-alpine as build

# 작업 디렉토리 설정
WORKDIR /app

# 패키지 파일 복사 및 의존성 설치
COPY package*.json ./
RUN npm install

# 소스 코드 복사
COPY . .

# 프로덕션 빌드
RUN npm run build

# Production stage
FROM nginx:alpine

# nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 파일을 nginx로 복사
COPY --from=build /app/build /usr/share/nginx/html

# 80 포트 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]