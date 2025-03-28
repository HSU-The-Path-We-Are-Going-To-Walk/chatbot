import requests
from dotenv import load_dotenv
import os

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def get_coordinates(address):
    url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
    params = {
        "query": address
    }
    headers = {
        "x-ncp-apigw-api-key-id": NAVER_CLIENT_ID,
        "x-ncp-apigw-api-key": NAVER_CLIENT_SECRET,
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 발생
        
        data = response.json()
        if data.get("status") == "OK" and data.get("addresses"):
            x = data["addresses"][0].get("x")
            y = data["addresses"][0].get("y")
            return x, y
        else:
            print("좌표 정보를 찾을 수 없습니다.")
            return None, None
    
    except requests.exceptions.RequestException as e:
        print(f"요청 중 오류 발생: {e}")
        return None, None
    except ValueError as e:
        print(f"JSON 파싱 오류: {e}")
        return None, None

# main 함수 추가
if __name__ == "__main__":
    test_address = "전남 고흥군 고흥읍 여산당촌길 19"
    x, y = get_coordinates(test_address)

    if x and y:
        print("\n📍 검색된 좌표:\n")
        print(f"x: {x}, y: {y}")
    else:
        print("❌ 좌표를 가져오는 데 실패했습니다.")