# 챗봇 시스템

고흥시 버스정류장의 사용자와 대화하는 챗봇 시스템입니다.

## 주요 기능

- 사용자의 질문 의도를 파악하여 적절한 대답
- 사용자의 질문은 크게 장소 질문/일상 및 공지 질문으로 나뉘어집니다.
- 장소 질문은 장소 찾기, 길찾기, 버스 노선 질문으로 나뉘어 적절하게 답변합니다.
- 공지 기반 질문은 크롤링/임베딩된 Pinecone 벡터 DB의 인덱스로 RAG에 기반하여 답변합니다.

![image](https://github.com/user-attachments/assets/ef84dfdf-6282-4f11-8878-ea47481e9ea4)


## 기술 스택

- **백엔드**: FastAPI (Python)
- **RAG 구축**: Langchain Framework, Pinecone Vector DB
- **장소 찾기**: 카카오 API
- **길찾기**: 카카오 API, SK Open API
- **버스 노선**: 카카오 API, 공공데이터포털  
- **배포**: Docker

### 요구사항

- Docker 및 Docker Compose
- Kakao API 키
- SK OPEN API 키
- OpenAI API 키

### 실행 방법

1. 저장소 클론
   ```bash
   git clone https://github.com/HSU-The-Path-We-Are-Going-To-Walk/chatbot.git
   ```

2. Docker Compose로 실행
   ```bash
   docker compose up --build
   ```

3. 웹 브라우저에서 접속: http://localhost:9000

## 시스템 구성

- 일상(정서) 답변 및 공지 기반 답변 시 단순 답변 포함
- 장소 찾기 답변 시 가장 가까운 상위 3개의 장소명, 좌표값 반환
- 길찾기 답변 시 화면에 띄울 정형화된 텍스트, 챗봇이 응답할 답변, 길찾기 경로의 각 좌표값들 반환
- 버스 노선 답변 시 DB에 목적지 주변 정류소가 존재하면 해당 버스 번호들, 도착 정보 반환, 주변 정류소가 없으면 길찾기 결과 반환
