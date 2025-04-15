# RAG 체인 관리 모듈
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from datetime import datetime
import pytz
import time

class RAGChainManager:
    """RAG(Retrieval-Augmented Generation) 체인을 관리하는 클래스"""
    
    def __init__(self, llm, database, get_session_history_func):
        """RAGChainManager 초기화"""
        self.llm = llm
        self.database = database
        self.get_session_history = get_session_history_func
        self.history_aware_retriever = self.get_history_retriever()
        self.rag_chain = self.create_rag_chain()
    
    def get_retriever(self):
        """데이터베이스 검색기를 반환합니다."""
        search_kwargs = {"k": 2}
        return self.database.as_retriever(search_kwargs=search_kwargs)
    
    def get_history_retriever(self):
        """대화 기록을 고려한 검색기를 생성합니다."""
        retriever = self.get_retriever()
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
        
        return create_history_aware_retriever(self.llm, retriever, contextualize_q_prompt)
    
    def get_current_kst_time(self):
        """한국 시간(KST)으로 현재 시간을 반환합니다."""
        kst = pytz.timezone('Asia/Seoul')
        return datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    
    def get_system_prompt(self, current_date=None):
        """시스템 프롬프트를 생성합니다."""
        if current_date is None:
            current_date = self.get_current_kst_time()
            
        return (
            f"현재 시간은 정확히 {current_date}입니다. 시간 관련 질문이 있을 경우 반드시 이 시간을 기준으로 답변하세요.\n"
            "당신은 고흥군 버스정류장에서 사람들과 대화하는 친근한 AI 챗봇입니다.\n"
            "필요에 따라 공지 정보를 활용하여 답변하세요\n"
            "답변 생성시 공지 정보를 포함했다면 반드시 마지막 문장에 한 줄 띄고 url 링크를 포함하세요.\n"
            "반드시 존댓말로 대화하세요.\n"
            "사람들이 질문하기 전에 먼저 관심을 표현하고, 편안하게 대화를 이어갈 수 있도록 하세요.\n"
            "출력은 오디오로 제공되므로 마크다운 형식(예: `**강조**`, `- 리스트`, `[링크](url)`, ````코드````)을 사용하지 말고, 평범한 일상 대화처럼 부드럽고 자연스럽게 문장을 구성하세요.\n"
            "공지사항을 설명할 때는 반드시 중요한 내용만 짧게 한 문장으로 요약하세요.\n"
            "어려운 단어나 기술적인 표현을 피하고, 부드럽고 따뜻한 말투를 사용하세요.\n"
            f"다시 한번 강조하지만, 현재 정확한 시간은 {current_date}입니다.\n"
        )
    
    def create_rag_chain(self, current_date=None):
        """RAG 체인을 생성합니다."""
        if current_date is None:
            current_date = self.get_current_kst_time()
            
        system_prompt = self.get_system_prompt(current_date)
        
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
                ("ai", "{context}"),
            ]
        )
        
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        rag_chain = create_retrieval_chain(self.history_aware_retriever, question_answer_chain)
        
        return RunnableWithMessageHistory(
            rag_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        ).pick('answer')
    
    def get_ai_response(self, user_message, session_id):
        """RAG 체인을 사용하여 사용자 메시지에 대한 응답을 생성합니다."""
        # 현재 시간 정보 가져오기 (모든 질문에 대해 현재 시간 저장, 한국 시간 사용)
        current_date = self.get_current_kst_time()
        
        # 모든 질문에 대해 항상 최신 시간 정보를 포함한 RAG 체인 생성
        self.rag_chain = self.create_rag_chain(current_date)
        
        # 시스템 프롬프트에 시간 정보가 포함되어 있으므로, 추가 처리 없이 바로 응답 생성
        ai_response_stream = self.rag_chain.stream(
            {"input": user_message},
            config={"configurable": {"session_id": session_id}},
        )
        return ai_response_stream