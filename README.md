# 고흥시 버스정류장 챗봇

고흥시 버스정류장에서 사람들과 대화하는 챗봇입니다.

## 주요 기능

- 사용자의 질문에 따른 적절한 답변 반환
- 크게 장소 관련 질문, 일상 대화 질문으로 나뉘어짐
- 장소 관련: 버스 도착 정보, 길찾기, 장소 찾기, 버스 노선
- 일상 대화 질문(공지 관련 질문)은 고흥시 공지사항들을 Retrieve 하여 답변 생성

## 기술 스택

- **백엔드**: FastAPI (Python)
- **RAG**: Langchain 프레임워크, Pinecone Vector DB
- **실시간 버스 도착 정보**: 공공데이터포털
- **길찾기**: 카카오 API, SK Open API
- **장소 찾기**: 카카오 API
- **버스 노선**: 카카오 API, 공공데이터포털
- **배포**: Docker

### 요구사항

- Docker 및 Docker Compose
- OPENAI API 키, PINECONE API 키, SK OPEN API 키, 공공데이터포탈 API 키, KAKAO API 키, 로컬 MYSQL DB 설정값 필요(호스트명, 유저명, 패스워드, DB명)

### 실행 방법

1. 저장소 클론
   ```bash
   git clone https://github.com/HSU-The-Path-We-Are-Going-To-Walk/chatbot.git
   ```

2. Docker Compose로 실행
   ```bash
   docker compose up --build
   ```

3. POSTMAN 실행
   http://localhost:8000/chat

  message에 질문 입력, session_id에 입력
  {
    "message" : "심심한데",
    "session_id" : "1234"
  }

## 라이센스

MIT 라이센스를 따릅니다. 세부 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
