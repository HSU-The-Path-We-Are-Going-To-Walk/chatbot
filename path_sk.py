import requests
import json
from dotenv import load_dotenv
import os
import bus_arrive_time

# 환경 변수 로드
load_dotenv()

SK_OPEN_API = os.getenv("SK_OPEN_API")

# 고정된 시작 좌표
START_X = "127.294395"
START_Y = "34.620273"

def get_transit_route(end_x, end_y, count=1):
    url = "https://apis.openapi.sk.com/transit/routes"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "appKey": SK_OPEN_API
    }
    data = {
        "startX": START_X,
        "startY": START_Y,
        "endX": str(end_x),
        "endY": str(end_y),
        "count": count,
        "lang": 0,
        "format": "json"
    }

    response = requests.post(url, headers=headers, json=data)

    # print(response.content)
    
    if response.status_code == 200:
        result = response.json()
        
        # 출발지와 도착지가 너무 가까운 경우 처리
        if result.get("result", {}).get("status") == 11 and result.get("result", {}).get("message") == "출발지와 도착지가 너무 가까움":
            return "출발지와 도착지가 너무 가까움"
        # SK_OPEN_API 의 경로 검색 결과가 없을 경우 처리
        elif result.get("result", {}).get("status") == 14 and result.get("result", {}).get("message") == "검색 결과가 없음":
            return "검색 결과가 없습니다. 다시 시도해 주세요"
        
        return extract_route_text(result)
    else:
        print(f"❌ API 요청 실패: {response.status_code}")
        print(response.text)
        return None

def extract_route_text(response_json):
    routes = response_json.get("metaData", {}).get("plan", {}).get("itineraries", [])
    directions = []
    
    for route in routes:
        legs = route.get("legs", [])
        for leg in legs:
            mode = leg.get("mode", "")
            # start = leg.get("start", {})
            # end = leg.get("end", {})
            start_name = leg.get("start", {}).get("name", "출발지")
            end_name = leg.get("end", {}).get("name", "도착지")
            # start_x = start.get("lon", "")
            # start_y = start.get("lat", "")
            # end_x = end.get("lon", "")
            # end_y = end.get("lat", "")
            original_line = leg.get("route", "")
            
            if mode in {"WALK"}:
                route_desc = f"{start_name}에서 {end_name}까지 도보로 이용"
            else:
                route_desc = f"{start_name}에서 {end_name}까지 {original_line} 이용"
            
            directions.append(route_desc)
    
    return "\n".join(directions)

# 사용 예시
if __name__ == "__main__":
    end_x = "127.2894390116774"
    end_y = "34.60984283910635"
    
    route_result = get_transit_route(end_x, end_y)
    
    if route_result:
        print("\n🚏 길 찾기 안내:\n")
        print(route_result)
