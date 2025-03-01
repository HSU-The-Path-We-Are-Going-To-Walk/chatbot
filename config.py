# config.py (환경 설정 파일)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 🔹 LLM 인스턴스 (오픈AI 모델 사용)
LLM = ChatOpenAI(model="gpt-4o-mini")

# 🔹 임베딩 모델 (오픈AI 임베딩 사용)
EMBEDDING = OpenAIEmbeddings(model="text-embedding-3-large")

# 🔹 Pinecone 벡터 DB 인덱스
INDEX_NAME = "uljin-notice"
DATABASE = PineconeVectorStore.from_existing_index(index_name=INDEX_NAME, embedding=EMBEDDING)
