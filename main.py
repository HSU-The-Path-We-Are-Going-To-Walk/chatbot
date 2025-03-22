# main.py - 메인 애플리케이션 파일
from datetime import datetime
import time

from modules.config import LLM, DATABASE
from modules.chat_history import ChatHistoryManager
from modules.intent_processor import IntentProcessor
from modules.path_finder import PathFinder
from modules.place_searcher import PlaceSearcher
from modules.bus_matcher import BusRouteManager
from modules.rag_chain import RAGChainManager


class ChatbotApp:
    """챗봇 애플리케이션의 메인 클래스"""
    
    def __init__(self):
        self.session_id = "abc123"
        self.last_interaction_time = time.time()
        self.current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_manager = ChatHistoryManager()
        self.rag_manager = None
        self.intent_processor = None
        self.path_finder = None
        self.place_searcher = None
        self.bus_route_manager = None
    
    def initialize_modules(self):
        """모든 필요한 모듈을 초기화합니다."""
        print(f"현재 날짜 및 시간: {self.current_date}")
        
        try:
            # 모듈 초기화
            self.intent_processor = IntentProcessor(LLM)
            self.path_finder = PathFinder()
            self.place_searcher = PlaceSearcher()
            self.bus_route_manager = BusRouteManager(self.path_finder)
            self.rag_manager = RAGChainManager(LLM, DATABASE, self.current_date, self.history_manager.get_session_history)
            
            print("✅ 모든 모듈이 성공적으로 초기화되었습니다.")
            return True
        except Exception as e:
            print(f"❌ 모듈 초기화 중 오류 발생: {str(e)}")
            return False
    
    def reset_if_idle(self, timeout=60):
        """일정 시간 동안 상호작용이 없으면 세션을 초기화합니다."""
        if time.time() - self.last_interaction_time > timeout:
            self.history_manager.reset_session(self.session_id)
            self.last_interaction_time = time.time()
    
    def process_user_input(self, user_input):
        """사용자 입력을 처리하고 적절한 응답을 반환합니다."""
        self.last_interaction_time = time.time()
        
        # 특수 명령어 처리
        if user_input.lower() == "e":
            return "exit"
        elif user_input.lower() == "r":
            self.history_manager.reset_session(self.session_id)
            return "reset"
        
        try:
            # 의도 및 목적지 추출
            intent, destination = self.intent_processor.detect_intent_and_extract_destination(user_input)
            print(f"🎯 감지된 의도: {intent if intent else '알 수 없음'}")
            print(f"📍 추출된 목적지: {destination if destination else '없음'}")
            
            # 의도에 따른 처리
            if intent is not None:
                return self.process_intent(intent, destination)
            else:
                # RAG 체인을 통한 일반 응답
                return self.get_rag_response(user_input)
        
        except Exception as e:
            error_msg = f"처리 중 오류가 발생했습니다: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def process_intent(self, intent, destination):
        """감지된 의도에 따라 적절한 기능을 실행합니다."""
        if intent == "위치 찾기" and destination:
            return self.process_location_search(destination)
        
        elif intent == "길찾기" and destination:
            return self.process_path_finding(destination)
        
        elif intent == "버스 노선" and destination:
            return self.process_bus_route(destination)
        
        return "의도를 처리할 수 없습니다."
    
    def process_location_search(self, destination):
        """위치 찾기 처리를 수행합니다."""
        places = self.place_searcher.find_places(destination)
        
        if places:
            formatted_places = []
            for idx, (place_name, x, y) in enumerate(places, start=1):
                formatted_places.append(f"{idx}. {place_name}")
            
            places_text = "\n".join(formatted_places)
            return f"'{destination}' 검색 결과:\n{places_text}"
        else:
            return f"'{destination}'에 대한 검색 결과가 없습니다."
    
    def process_path_finding(self, destination):
        """길찾기 처리를 수행합니다."""
        route_data, place_name = self.path_finder.find_path(destination)
        formatted_result = self.path_finder.format_path_result(route_data, place_name or destination)
        
        place = formatted_result.get("place_name", "")
        routes = formatted_result.get("routes_text", "")
        coords = formatted_result.get("formatted_coordinates", "")
        
        return f"{routes}\n{coords}"
    
    def process_bus_route(self, destination):
        """버스 노선 정보 처리를 수행합니다."""
        result = self.bus_route_manager.process_bus_route(destination)
        status = result.get("status")
        
        if status == "버스_도착정보_있음":
            match_buses = result.get("match_buses")
            arrival_info = result.get("arrival_info")
            
            bus_list = ", ".join([str(bus) for bus in match_buses])
            arrival_text = "\n".join([f"{info['버스번호']}번 버스: {info['도착예정시간']}" for info in arrival_info])
            
            return f"'{destination}'(으)로 가는 버스: {bus_list}\n\n현재 도착 정보:\n{arrival_text}"
        
        elif status == "버스_도착정보_없음":
            match_buses = result.get("match_buses")
            bus_list = ", ".join([str(bus) for bus in match_buses])
            
            return f"'{destination}'(으)로 가는 버스: {bus_list}\n\n현재 도착 예정인 버스가 없습니다."
        
        elif status == "길찾기_수행":
            route_data = result.get("route")
            place_name = result.get("place_name")
            
            formatted_result = self.path_finder.format_path_result(route_data, place_name or destination)
            routes = formatted_result.get("routes_text", "")
            coords = formatted_result.get("formatted_coordinates", "")
            
            return f"{destination}(으)로 가는 버스가 없습니다. 대신 길찾기 결과를 알려드립니다.\n{routes}\n{coords}"
        
        return "버스 노선 정보를 처리할 수 없습니다."
    
    def get_rag_response(self, user_input):
        """RAG 체인을 사용하여 일반 응답을 생성합니다."""
        try:
            ai_response = self.rag_manager.get_ai_response(user_input, self.session_id)
            response_text = "".join([chunk for chunk in ai_response])
            return response_text
        except Exception as e:
            error_msg = f"응답 생성 중 오류가 발생했습니다: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def run(self):
        """챗봇 애플리케이션의 메인 실행 루프"""
        print("🚏 고흥 AI 챗봇 🤖 (종료: 'e', 초기화: 'r')")
        
        if not self.initialize_modules():
            print("❌ 초기화에 실패했습니다. 프로그램을 종료합니다.")
            return
        
        while True:
            self.reset_if_idle()
            user_input = input("👤: ")
            
            response = self.process_user_input(user_input)
            
            if response == "exit":
                print("👋 챗봇을 종료합니다.")
                break
            elif response == "reset":
                print("🔄 대화 기록이 초기화되었습니다.")
                continue
            else:
                print(f"🤖: {response}")


if __name__ == "__main__":
    app = ChatbotApp()
    app.run()