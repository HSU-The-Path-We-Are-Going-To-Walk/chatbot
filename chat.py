from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from datetime import datetime
import time

# 🔹 config.py에서 전역 객체 가져오기
from config import LLM, DATABASE  

store = {}
session_id = "abc123"
last_interaction_time = time.time() # 마지막 입력 시간
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"현재 날짜 및 시간: {current_date}")

def log_time(func):
    """함수 실행 시간을 로깅하는 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"⏳ {func.__name__} 실행 시간: {elapsed_time:.4f}초")
        return result
    return wrapper

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 세션의 대화 기록을 삭제
def reset_session(session_id: str):
    if session_id in store:
        del store[session_id]
        print("🔄 대화 기록이 초기화되었습니다.")

def reset_if_idle(timeout=60):
    global last_interaction_time, session_id
    if time.time() - last_interaction_time > timeout:
        reset_session(session_id)
        last_interaction_time = time.time

# Pinecone 검색 설정 (전역 DATABASE 사용)
def get_retriever():
    search_kwargs = {"k": 2}
    return DATABASE.as_retriever(search_kwargs=search_kwargs)

# LLM 가져오기 (전역 LLM 사용)
def get_llm():
    return LLM

# 히스토리 기반 검색 설정
def get_history_retriever():
    retriever = get_retriever()
    
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is"
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    return create_history_aware_retriever(LLM, retriever, contextualize_q_prompt)

# RAG 체인 생성 (최초 1회 생성 후 재사용)
def create_rag_chain():
    history_aware_retriever = get_history_retriever()
    
    system_prompt = (
        f"오늘 날짜는 {current_date}입니다.\n"
        "당신은 울진군 버스정류장에서 어르신들과 대화하는 친근한 AI 챗봇입니다.\n"
        "어르신들이 질문하기 전에 먼저 관심을 표현하고, 편안하게 대화를 이어갈 수 있도록 하세요.\n"
        # "대화가 시작될 때에는 오늘은 어디 가시나요? 라고 물어보세요.\n" -> 트리거 발동시 먼저 대화할 내용
        "출력은 오디오로 제공되므로 마크다운 형식(예: `**강조**`, `- 리스트`, `[링크](url)`, ````코드````)을 사용하지 말고, 평범한 일상 대화처럼 부드럽고 자연스럽게 문장을 구성하세요."
        "버스 도착 정보를 제공할 때는 예상 도착 시간을 알려주고, 공지사항을 설명할 때는 반드시 중요한 내용만 짧게 한 줄로 요약하세요.\n"
        "어려운 단어나 기술적인 표현을 피하고, 부드럽고 따뜻한 말투를 사용하세요.\n"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            ("ai", "{context}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(LLM, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')

# ✅ RAG 체인을 전역으로 선언하여 재사용
RAG_CHAIN = create_rag_chain()

def get_ai_response(user_message, session_id):
    ai_response_stream = RAG_CHAIN.stream(
        {"input": user_message},
        config={"configurable": {"session_id": session_id}},
    )
    return ai_response_stream

def chat():
    global last_interaction_time
    print("🚏 울진 AI 챗봇 🤖 (종료: 'exit', 초기화: 'reset')")
    
    while True:
        reset_if_idle()
        user_input = input("👤: ")
        last_interaction_time = time.time() #입력이 들어오면 시간 갱신
        if user_input.lower() == "e":
            print("👋 챗봇을 종료합니다.")
            break
        elif user_input.lower() == "r":
            reset_session(session_id)
            continue # 새로운 입력을 받도록 반복문 유지

        ai_response = get_ai_response(user_input, session_id)
        print("🤖:", end=" ")
        for chunk in ai_response:
            print(chunk, end="", flush=True)
        print()

chat()
