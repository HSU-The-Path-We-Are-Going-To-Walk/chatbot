import requests

def get_address(query):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1
    }

    response = requests.get(url, params=params)

    # 응답이 실패하면 오류 메시지 출력
    if response.status_code != 200:
        print("❌ API 요청 실패:", response.text)
        return None

    data = response.json()

    # 검색 결과가 없을 경우
    if not data:
        print("❌ 해당 장소를 찾을 수 없습니다.")
        return None

    # 첫 번째 검색 결과 가져오기
    address_info = data[0]
    
    # 도로명 주소 가져오기 (없으면 None)
    road_address = address_info.get("display_name", "❌ 도로명 주소 없음")
    
    # 위도, 경도 가져오기
    latitude = address_info.get("lat", "❌ 위도 없음")
    longitude = address_info.get("lon", "❌ 경도 없음")

    return road_address, latitude, longitude

# 🔍 테스트 실행
query = "울진초등학교"
result = get_address(query)

if result:
    print(f"🔍 검색한 장소: {query}")
    print(f"📍 도로명 주소: {result[0]}")
    print(f"🌍 위도: {result[1]}, 경도: {result[2]}")
