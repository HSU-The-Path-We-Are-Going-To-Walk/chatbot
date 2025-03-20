import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

# 길찾기 검색, 버스 어디가요 시 사용됨 
def search_keyword_top1(query):
    """
    Kakao 로컬 검색 API를 사용하여 키워드 검색 결과 중 상위 1개의 place_name, x, y 좌표를 반환합니다.

    Parameters:
    query (str): 검색할 키워드

    Returns:
    list: [(place_name1, x1, y1), (place_name2, x2, y2), (place_name3, x3, y3)]
          검색된 장소 이름과 좌표 리스트 (검색 결과 없거나 오류 시 빈 리스트 반환)
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    
    params = {
        "query": query,
        "x": 127.289108,
        "y": 34.608177
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        data = response.json()
        
        if data.get("documents"):
            top_result = data["documents"][0]
            place_name = top_result.get("place_name")
            x = top_result.get("x")
            y = top_result.get("y")
            return place_name, x, y  # 튜플로 반환
        else:
            return None, None, None  # 검색 결과 없을 경우 None 반환
    
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {str(e)}")
        return None, None, None
    except json.JSONDecodeError:
        print("❌ JSON 파싱 실패")
        return None, None, None

# 장소 검색 시 사용됨
def search_keyword_top3(query):
    """
    Kakao 로컬 검색 API를 사용하여 키워드 검색 결과 중 상위 3개의 place_name, x, y 좌표를 반환합니다.
    
    Parameters:
    query (str): 검색할 키워드
    KAKAO_REST_API_KEY (str): Kakao REST API 키
    
    Returns:
    tuple: (place_name, x, y) - 검색된 장소 이름과 좌표 (검색 결과 없거나 오류 시 None 반환)
    """
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    
    params = {
        "query": query,
        "x": 127.289108,
        "y": 34.608177,
        "sort": "distance"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        data = response.json()
        
        results = []
        if data.get("documents"):
            for doc in data ["documents"][:3]:
                place_name = doc.get("place_name")
                x = doc.get("x")
                y = doc.get("y")
                results.append((place_name, x, y))
        
        return results
    
    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {str(e)}")
        return []
    except json.JSONDecodeError:
        print("❌ JSON 파싱 실패")
        return []


if __name__ == "__main__":
    query = "편의점"
    
    # search_keyword_top1 테스트
    print("🔍 search_keyword_top1 테스트")
    place_name, x, y = search_keyword_top1(query)

    if place_name:
        print("✅ 검색 결과 (상위 1개):")
        print(f"   장소 이름: {place_name}")
        print(f"   x 좌표: {x}")
        print(f"   y 좌표: {y}\n")
    else:
        print("⚠️ 검색 결과 없음 또는 오류 발생\n")

    # search_keyword_top3 테스트
    print("🔍 search_keyword_top3 테스트")
    search_results = search_keyword_top3(query)

    if search_results:
        print("✅ 검색 결과 (상위 3개):")
        for idx, (place, x, y) in enumerate(search_results, start=1):
            print(f"   {idx}. {place} (X: {x}, Y: {y})")
    else:
        print("⚠️ 검색 결과 없음 또는 오류 발생")