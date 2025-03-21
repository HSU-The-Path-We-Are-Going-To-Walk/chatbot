from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from datetime import datetime
import time

from config import LLM, DATABASE  

store = {}
session_id = "abc123"
last_interaction_time = time.time() 
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def initialize_modules():
    global kakao_places, path_sk,nearby_busstop_match, bus_arrive_time
    import kakao_places
    import path_sk
    import nearby_busstop_match
    import bus_arrive_time
    
    print(f"현재 날짜 및 시간: {current_date}")
    
    return kakao_places, path_sk

def detect_intent_and_extract_destination(user_message):

    prompt = f"""
    사용자의 메시지를 분석하여 의도와 목적지를 파악하세요.
    
    반환 형식 예시:
    - 길찾기: "의도: 길찾기, 목적지: 울진고등학교"
    - 버스 노선: "의도: 버스 노선, 목적지: 연호체육공원"
    - 위치 찾기: "의도: 위치 찾기, 목적지: 편의점"
    - 기타: "의도: 기타"
    
    사용자 입력: "{user_message}"
    """
    
    try:
        result = LLM.invoke(prompt).content

        if "의도: 길찾기" in result:
            intent = "길찾기"
        elif "의도: 버스 노선" in result:
            intent = "버스 노선"
        elif "의도: 위치 찾기" in result:
            intent = "위치 찾기"
        else:
            intent = None

        if "목적지:" in result:
            destination = result.split("목적지:")[-1].strip()
            destination = destination.replace('"', '').replace("'", "")
            destination = destination.rstrip('".\',:;')

        return intent, destination
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        print(f"🔍 원본 응답: {result if 'result' in locals() else '없음'}")
        return None, None

def find_path(destination):
    try:
        result = kakao_places.search_keyword_top1(destination)
        
        print(f"🔍 검색된 장소 결과: {result}")
        place_name, x, y = result

        print(f"🔍 검색된 장소: {place_name}, 좌표: ({x}, {y})")  
        directions = path_sk.get_transit_route(x, y)
        return directions, place_name

    except Exception as e:
        print(f"❌ 경로 찾기 중 오류 발생: {str(e)}")  
        return f"경로 찾기 중 오류 발생: {str(e)}"
    
def find_places(destination):
    try:
        results = kakao_places.search_keyword_top3(destination)

        if not results:
            print("⚠️ 검색된 장소가 없습니다.")
            return []

        print("✅ 장소 찾기 결과:")
        for idx, (place_name, x, y) in enumerate(results, start=1):
            print(f"   {idx}. {place_name} (X: {x}, Y: {y})")

        return results  # [(place_name1, x1, y1), (place_name2, x2, y2), (place_name3, x3, y3)]

    except Exception as e:
        print(f"❌ 장소 검색 중 오류 발생: {str(e)}")
        return []
    
def match_buses(destination):
    _, x, y = kakao_places.search_keyword_top1(destination)
    nearby_bus_info = nearby_busstop_match.get_nearby_bus_info(y, x)

    # 주변 정류장이 없을 경우 처리
    if nearby_bus_info.get("status") == "주변_정류장_없음":
        print("🚫 주변 정류장이 없습니다. 길찾기 수행.")
        return [], []  # ✅ 항상 두 개의 값 반환

    match_bus_numbers = []

    # 정류장 리스트를 순회하면서 버스 번호 추출
    for station in nearby_bus_info.get("bus_stations", []):
        bus_numbers = station.get("bus_numbers", [])
        if isinstance(bus_numbers, list):
            match_bus_numbers.extend(bus_numbers)
    
    match_bus_numbers = [str(num) for num in match_bus_numbers]

    arrival_info = bus_arrive_time.get_bus_arrival_info()

    # 두 리스트를 비교하여 일치하는 버스만 필터링
    matching_arrivals = []
    for bus_info in arrival_info:
        if not isinstance(bus_info, (list, tuple)) or len(bus_info) < 2:
            continue

        bus_number = str(bus_info[0])
        arrival_time = bus_info[1]
        
        print(f"🔍 비교: 노선버스 {bus_number} vs 주변버스 {match_bus_numbers}")
        
        bus_number_int = str(bus_info[0])
        arrival_time = bus_info[1]
        
        if bus_number_int in match_bus_numbers:
            bus_arrival_info = {
                "버스번호": bus_number,
                "도착예정시간": f"{arrival_time}분 후",
                "도착시간(분)": arrival_time
            } 
            matching_arrivals.append(bus_arrival_info)
    
    matching_arrivals.sort(key=lambda x: x["도착시간(분)"])
    
    return match_bus_numbers, matching_arrivals


def intent_func(intent, destination):
    if intent == "버스 노선":
        try: 
            print(f"🚌 '버스 노선' 의도 처리 시작")
            match_bus_numbers, matching_arrivals = match_buses(destination)
            if matching_arrivals:
                result = {
                    "status" : "버스_도착정보_있음",
                    "match_buses" : match_bus_numbers,
                    "arrival_info" : matching_arrivals
                }
                return result
            elif match_bus_numbers:
                result = {
                    "status" : "버스_도착정보_없음",
                    "match_buses" : match_bus_numbers
                }
                return result
            else:
                route, place_name = find_path(destination)
                result = {
                    "status" : "길찾기_수행",
                    "route" : route,
                    "place_name" : destination
                }
                return result
        except Exception as e:
            print(f"❌ 버스 노선 처리 중 오류 발생: {str(e)}")
            return f"버스 노선 처리 중 오류가 발생했습니다: {str(e)}", None
        
    elif intent == "길찾기" and destination:
        print(f"🚶 '길찾기' 의도 처리 시작")
        try:
            print(f"🔍 find_path() 호출...")
            directions, place_name = find_path(destination)
            print(f"🔍 find_path() 결과: {place_name} / {directions[:100]}...")
            return directions, place_name
        except Exception as e:
            print(f"❌ 길찾기 처리 중 오류 발생: {str(e)}")
            return f"길찾기 처리 중 오류가 발생했습니다: {str(e)}", None
    
    elif intent == "위치 찾기" and destination:
        print(f"📍 '위치 찾기' 의도 처리 시작")
        try:
            print(f"🔍 find_places() 호출...")
            places = find_places(destination)
            print(f"🔍 find_places() 결과: {places}")
            return places
        except Exception as e:
            print(f"❌ 장소명 검색 중 오류 발생: {str(e)}")
            return f"장소명 검색 중 오류가 발생했습니다: {str(e)}", None
    
    print("❌ 일치하는 의도 처리 로직 없음")
    return None, None

def intent_prompting(route_data, place_name):

    print(route_data)
    
    if route_data == "출발지와 도착지가 너무 가까움":
        return f"{place_name}은 현재 위치에서 가까운 거리에 있습니다. 도보로 이동 가능합니다."
    
    elif route_data == "검색 결과가 없습니다. 다시 시도해 주세요" or route_data is None:
        return f"{place_name}까지의 경로를 찾을 수 없습니다. 다른 장소를 검색해 보시겠어요?"
    
    elif isinstance(route_data, str) and route_data.startswith("경로 찾기 중 오류"):
        return f"{place_name}까지의 경로를 검색하는 중에 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."
    
    elif not route_data or route_data.strip() == "":
        return f"{place_name}까지의 경로 정보가 없습니다."

    prompt = f"""
    다음은 이동 경로 데이터입니다. 
    
    {route_data}

    🔹 **출력 규칙** 🔹
    1. "출발지"를 항상 "현재 위치"로 변경하세요.
    2. 도착지를 "{place_name}"으로 변경하세요.
    3. **모든 역 이름에는 '역'을 붙여야 합니다.**  
       - 예: 학림 → 학림역, 고흥터미널 → 고흥터미널역, 강남 → 강남역
    4. 잘못된 예시는 절대 출력하지 마세요.  
       - ❌ "고흥터미널에서 고흥터미널까지 도보 이동" (같은 장소에서 이동 X)
    5. 같은 번호의 대체 가능한 버스 정보를 삭제하지 마세요.
    6. 불필요한 문장은 제거하고 **순수한 길찾기 정보만 출력**하세요.

    🔹 **출력 예시** 🔹
    ✅ **올바른 출력**
    1. 현재 위치에서 고흥동초교역까지 도보 이동
    2. 고흥동초교역에서 고흥터미널역까지 농어촌:140 이용
    3. 고흥터미널역에서 고흥군청까지 도보 이동

    ❌ **잘못된 출력**
    - "학림에서 고흥터미널까지 농어촌:140 이용"  (🚫 '역'이 빠짐)
    - "고흥터미널에서 고흥터미널까지 도보로 이동" (🚫 같은 장소 반복 이동)
    """

    try:
        result = LLM.invoke(prompt).content
        return result.strip()
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return route_data


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

def reset_session(session_id: str):
    if session_id in store:
        del store[session_id]
        print("🔄 대화 기록이 초기화되었습니다.")

def reset_if_idle(timeout=60):
    global last_interaction_time, session_id
    if time.time() - last_interaction_time > timeout:
        reset_session(session_id)
        last_interaction_time = time.time()

def get_retriever():
    search_kwargs = {"k": 2}
    return DATABASE.as_retriever(search_kwargs=search_kwargs)

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

def create_rag_chain():
    history_aware_retriever = get_history_retriever()
    
    system_prompt = (
        f"오늘 날짜는 {current_date}입니다.\n"
        "당신은 고흥군 버스정류장에서 사람들과 대화하는 친근한 AI 챗봇입니다.\n"
        "필요에 따라 공지 정보를 활용하여 답변하세요\n"
        "반드시 존댓말로 대화하세요.\n"
        "사람들이 질문하기 전에 먼저 관심을 표현하고, 편안하게 대화를 이어갈 수 있도록 하세요.\n" # 트리거 연동 시 변경해야 할 부분
        "출력은 오디오로 제공되므로 마크다운 형식(예: `**강조**`, `- 리스트`, `[링크](url)`, ````코드````)을 사용하지 말고, 평범한 일상 대화처럼 부드럽고 자연스럽게 문장을 구성하세요.\n"
        "공지사항을 설명할 때는 반드시 중요한 내용만 짧게 한 문장으로 요약하세요.\n"
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

def get_ai_response(user_message, session_id, rag_chain):
    ai_response_stream = rag_chain.stream(
        {"input": user_message},
        config={"configurable": {"session_id": session_id}},
    )
    return ai_response_stream


##### chat #####


def chat():
    global last_interaction_time
    print("🚏 고흥 AI 챗봇 🤖 (종료: 'e', 초기화: 'r')")
    
    try:
        initialize_modules()
        rag_chain = create_rag_chain()
    except Exception as e:
        print(f"초기화 중 오류 발생: {str(e)}")
        return
    
    while True:
        reset_if_idle()
        user_input = input("👤: ")
        last_interaction_time = time.time() 
        
        if user_input.lower() == "e":
            print("👋 챗봇을 종료합니다.")
            break
        elif user_input.lower() == "r":
            reset_session(session_id)
            continue
        
        try:
            intent, destination = detect_intent_and_extract_destination(user_input)
            print(f"🎯 감지된 의도: {intent if intent else '알 수 없음'}")
            print(f"📍 추출된 목적지: {destination if destination else '없음'}")
            
            if intent is not None:
                # 특정 의도에 따른 처리
                result = intent_func(intent, destination)
                
                # 위치 찾기일 경우 (리스트 반환)
                if intent == "위치 찾기" and isinstance(result, list):
                    if result:
                        formatted_places = []
                        for idx, (place_name, x, y) in enumerate(result, start=1):
                            formatted_places.append(f"{idx}. {place_name}")
                        
                        places_text = "\n".join(formatted_places)
                        response = f"'{destination}' 검색 결과:\n{places_text}"
                        print(f"🤖: {response}")
                    else:
                        print(f"🤖: '{destination}'에 대한 검색 결과가 없습니다.")
                
                # 길찾기일 경우 (튜플 반환: route_data, place_name)
                elif intent == "길찾기" and isinstance(result, tuple) and len(result) == 2:
                    route_data, place_name = result
                    formatted_result = intent_prompting(route_data, place_name or destination)
                    print(f"🤖: {formatted_result}")
                
                # 버스 노선일 경우 (딕셔너리 반환)
                elif intent == "버스 노선" and isinstance(result, dict):
                    status = result.get("status")
                    
                    # 케이스 1: 일치하는 버스가 있고 도착 정보도 있는 경우
                    if status == "버스_도착정보_있음":
                        match_buses = result.get("match_buses")
                        arrival_info = result.get("arrival_info")
                        
                        bus_list = ", ".join([str(bus) for bus in match_buses])
                        arrival_text = "\n".join([f"{info['버스번호']}번 버스: {info['도착예정시간']}" for info in arrival_info])
                        
                        response = f"'{destination}'(으)로 가는 버스: {bus_list}\n\n현재 도착 정보:\n{arrival_text}"
                        print(f"🤖: {response}")
                    
                    # 케이스 2: 일치하는 버스는 있지만 도착 정보가 없는 경우
                    elif status == "버스_도착정보_없음":
                        match_buses = result.get("match_buses")
                        bus_list = ", ".join([str(bus) for bus in match_buses])
                        
                        response = f"'{destination}'(으)로 가는 버스: {bus_list}\n\n현재 도착 예정인 버스가 없습니다."
                        print(f"🤖: {response}")
                    
                    # 케이스 3: 일치하는 버스 목록도 없는 경우 - 길찾기 수행
                    elif status == "길찾기_수행":
                        route_data = result.get("route")
                        place_name = result.get("place_name")
                        
                        formatted_result = intent_prompting(route_data, place_name or destination)
                        print(f"🤖: {destination}(으)로 가는 버스가 없습니다. 대신 길찾기 결과를 알려드립니다.\n{formatted_result}")
                
                # 문자열 결과일 경우 (에러 메시지 등)
                elif isinstance(result, str):
                    print(f"🤖: {result}")
                
                # 예외 처리
                else:
                    print(f"🤖: 처리 결과를 표시할 수 없습니다.")
    
            else:
                print("챗봇 응답")
                # RAG 체인을 통한 응답 생성
                ai_response = get_ai_response(user_input, session_id, rag_chain)
                print("🤖:", end=" ")
                for chunk in ai_response:
                    print(chunk, end="", flush=True)
                print()
        except Exception as e:  
            print(f"🤖: 처리 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    chat()