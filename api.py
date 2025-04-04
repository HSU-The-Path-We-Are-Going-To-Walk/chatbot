from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Union, List, Optional, Dict
import uuid

from dto import (
    ChatRequest, GeneralResponse, LocationInfo, 
    PathInfo, BusInfo
)
from main import ChatbotApp
from prompt_manager import PromptManager
from external_apis.bus_arrive_time import get_bus_arrival_info

app = FastAPI(title="고흥 AI 챗봇 API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 구체적인 origin을 지정해야 합니다
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 챗봇 인스턴스 초기화
chatbot = ChatbotApp()
if not chatbot.initialize_modules():
    raise Exception("챗봇 초기화 실패")

# 현재 활성화된 세션 ID 저장
active_sessions = set()

@app.post("/start")
async def start_session():
    """새로운 세션을 시작합니다. 이미 세션이 있다면 무시합니다."""
    if active_sessions:
        return
    
    session_id = str(uuid.uuid4())
    active_sessions.add(session_id)

@app.post("/reset")
async def reset_session():
    """현재 세션을 초기화합니다."""
    # 새로운 세션 ID 생성
    new_session_id = str(uuid.uuid4())
    active_sessions.clear()  # 기존 세션 모두 제거
    active_sessions.add(new_session_id)
    
    # 챗봇의 대화 기록 초기화
    chatbot.history_manager.reset_session(chatbot.session_id)
    chatbot.session_id = new_session_id

@app.post("/chat", response_model=Union[GeneralResponse, LocationInfo, PathInfo, BusInfo])
async def chat(request: ChatRequest):
    try:
        # 세션 ID 유효성 검증
        if request.session_id:
            # 첫 요청이면 세션 ID를 활성 세션 목록에 추가
            if request.session_id not in active_sessions:
                active_sessions.add(request.session_id)
            
            chatbot.session_id = request.session_id
            
        # 의도 처리는 동일하게 진행
        intent, destination = chatbot.intent_processor.detect_intent_and_extract_destination(request.message)
        print(f"감지된 의도: {intent}, 목적지: {destination}")
        
        # 일반 대화
        if not intent:
            response = chatbot.get_rag_response(request.message)
            return GeneralResponse(
                response=response,
                success=True
            )
        
        # 위치 찾기
        elif intent == "위치 찾기" and destination:
            places = chatbot.place_searcher.find_places(destination)
            place_names = [place[0] for place in places[:3]]
            coordinates = [(float(place[1]), float(place[2])) for place in places[:3]]
            
            conversation = PromptManager.convert_to_conversation(
                ", ".join(place_names), 
                "위치"
            )
            
            return LocationInfo(
                places=place_names,
                coordinates=coordinates,
                conversation_response=conversation
            )
        
        # 길찾기
        elif intent == "길찾기" and destination:
            # request.message 대신 destination을 사용
            route_data, place_name = chatbot.path_finder.find_path(destination)
            formatted_result = chatbot.path_finder.format_path_result(route_data, place_name)
            
            conversation = PromptManager.convert_to_conversation(
                formatted_result["routes_text"],
                "경로"
            )
            
            return PathInfo(
                routes_text=formatted_result["routes_text"],
                coordinates=formatted_result["formatted_coordinates"],
                conversation_response=conversation
            )
        
        # 버스 노선 (한 줄로 나열)
        elif intent == "버스 노선" and destination:
            result = chatbot.bus_route_manager.process_bus_route(destination)
            
            if result["status"] == "버스_도착정보_있음":
                # 도착 정보를 DTO에 맞게 변환
                processed_arrival_times = []
                for info in result["arrival_info"]:
                    # 딕셔너리의 각 값을 문자열로 변환
                    processed_info = {
                        "버스번호": str(info["버스번호"]),
                        "도착예정시간": str(info["도착예정시간"]),
                        "도착시간(분)": str(info["도착시간(분)"])
                    }
                    processed_arrival_times.append(processed_info)
                
                conversation = f"{destination}(으)로 가는 버스는 {', '.join(result['match_buses'])}번이 있어요. "
                conversation += "곧 도착하는 버스를 알려드릴게요:\n"
                for info in processed_arrival_times:
                    conversation += f"{info['버스번호']}번 버스가 {info['도착예정시간']}에 도착 예정입니다.\n"
                
                return BusInfo(
                    available_buses=result["match_buses"],
                    arrival_times=processed_arrival_times,
                    conversation_response=conversation
                )
            
            elif result["status"] == "버스_도착정보_없음":
                conversation = f"{destination}(으)로 가는 버스는 {', '.join(result['match_buses'])}번이 있지만, 지금은 도착 예정인 버스가 없습니다."
                
                return BusInfo(
                    available_buses=result["match_buses"],
                    arrival_times=[],
                    conversation_response=conversation
                )
                
            elif result["status"] == "길찾기_수행":
                # 버스가 없는 경우 대체 경로 제공
                # 먼저 경로를 찾고 포맷팅
                route_data = result.get("route")
                place_name = result.get("place_name", destination)
                
                # 경로 데이터가 없거나 처리할 수 없는 형식인 경우
                if not route_data or isinstance(route_data, str):
                    formatted_result = {
                        "routes_text": f"{destination}까지 가는 버스가 없으며, 대체 경로도 찾을 수 없습니다.",
                        "formatted_coordinates": [[]]  # 빈 좌표 배열
                    }
                else:
                    # 경로 데이터가 있으면 포맷팅
                    formatted_result = chatbot.path_finder.format_path_result(route_data, place_name)
                
                path_info = PathInfo(
                    routes_text=formatted_result["routes_text"],
                    coordinates=formatted_result["formatted_coordinates"],
                    conversation_response=PromptManager.convert_to_conversation(
                        formatted_result["routes_text"],
                        "버스_경로"  # 타입을 버스_경로로 변경
                    )
                )
                
                return BusInfo(
                    available_buses=[],
                    arrival_times=[],
                    alternative_path=path_info,
                    conversation_response=PromptManager.convert_to_conversation(
                        formatted_result["routes_text"],
                        "버스_경로"  # 타입을 버스_경로로 변경
                    )
                )
            
            else:
                # 오류 발생 시
                return BusInfo(
                    available_buses=[],
                    arrival_times=[],
                    conversation_response=f"{destination}(으)로 가는 버스 정보를 조회하는 중 문제가 발생했습니다: {result.get('error_message', '알 수 없는 오류')}"
                )
        
        raise HTTPException(status_code=400, detail="처리할 수 없는 요청입니다.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/bus", response_model=List[Dict[str, Union[str, int]]])
async def get_bus_arrival():
    """
    특정 정류장의 버스 도착 정보를 조회합니다.
    
    - **city_code**: 도시 코드 (기본값: 36350)
    - **node_id**: 정류장 ID (기본값: TSB332000523)
    """
    try:
        # 기본값을 사용하여 버스 도착 정보 가져오기
        bus_arrivals = get_bus_arrival_info()  # 기본값 사용
        
        # 결과를 반환할 형식으로 변환
        result = [{"bus_number": bus[0], "arrival_minutes": bus[1]} for bus in bus_arrivals]
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 