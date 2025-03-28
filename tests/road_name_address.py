import os
import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

ROAD_NAME_ADDRESS = os.getenv("ROAD_NAME_ADDRESS")

def get_road_name_address(keyword):
    """
    도로명 주소 API를 호출하여 주소 정보를 가져오는 함수
    :param keyword: 검색할 주소 키워드 (문자열)
    :return: 도로명 주소 문자열 또는 오류 메시지
    """
    url = "https://business.juso.go.kr/addrlink/addrLinkApi.do"
    params = {
        "currentPage": 1,
        "countPerPage": 1,
        "keyword": keyword,
        "confmKey": ROAD_NAME_ADDRESS,
        "firstSort": "road",
        "resultType": "json"  # JSON 형식으로 응답받기
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", {}).get("juso", [])
        
        if results:
            return results[0].get("roadAddr", "도로명 주소 없음")
        else:
            return "❌ 주소 데이터를 찾을 수 없습니다."
    else:
        return f"❌ API 요청 실패: {response.status_code}"

if __name__ == "__main__":
    test_keyword = "고흥종합복지센터"
    address_result = get_road_name_address(test_keyword)

    print("   ", test_keyword)
    print("📍 검색된 도로명 주소:")
    print(address_result)