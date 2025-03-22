from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

class ChatHistoryManager:
    """대화 기록을 관리하는 클래스"""
    
    def __init__(self):
        """채팅 기록 저장소 초기화"""
        self.store = {}
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """세션 ID에 해당하는 대화 기록을 반환하거나 새로 생성합니다."""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def reset_session(self, session_id: str):
        """특정 세션의 대화 기록을 초기화합니다."""
        if session_id in self.store:
            del self.store[session_id]
            print("🔄 대화 기록이 초기화되었습니다.")