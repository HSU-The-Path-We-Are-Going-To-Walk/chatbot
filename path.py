import requests
import json
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

SK_OPEN_API = os.getenv("SK_OPEN_API")

# API URL
url = "https://apis.openapi.sk.com/transit/routes"

# 헤더 (appKey 포함)
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "appKey": SK_OPEN_API
}

# 바디 데이터
data = {
    "startX": "127.02550910860451",
    "startY": "37.63788539420793",
    "endX": "127.030406594109",
    "endY": "37.609094989686",
    "count": 1,
    "lang": 0,
    "format": "json"
}

# API 요청
response = requests.post(url, headers=headers, json=data)

# JSON 응답 처리
def extract_route_text(response_json):
    routes = response_json.get("metaData", {}).get("plan", {}).get("itineraries", [])
    
    directions = []
    for route in routes:
        legs = route.get("legs", [])
        for leg in legs:
            mode = leg.get("mode", "")
            start_name = leg.get("start", {}).get("name", "출발지")
            end_name = leg.get("end", {}).get("name", "도착지")
            route_desc = f"{start_name}에서 {end_name}까지 {mode} 이용"
            directions.append(route_desc)
    
    return "\n".join(directions)

if response.status_code == 200:
    result = response.json()
    route_text = extract_route_text(result)
    print("\n🚏 길 찾기 안내:\n")
    print(route_text)
else:
    print(f"❌ API 요청 실패: {response.status_code}")
    print(response.text)
