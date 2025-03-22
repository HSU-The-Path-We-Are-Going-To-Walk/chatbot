import os
import requests
import xml.etree.ElementTree as ET
import pymysql
from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.getenv("SERVICE_KEY")

# MySQL 연결 정보
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4"
}

def get_bus_arrival_info(gpsLati, gpsLong, page_no='1', num_of_rows='10'):
    """
    주어진 GPS 좌표 주변의 버스 정류장 정보를 조회합니다.
    
    Args:
        gpsLati (float): 위도
        gpsLong (float): 경도
        page_no (str): 페이지 번호
        num_of_rows (str): 한 페이지당 결과 수
        
    Returns:
        list: (정류장 이름, 정류장 ID) 튜플로 구성된 리스트
    """
    # API 요청
    url = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList'
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        '_type': 'xml',
        'gpsLati': gpsLati,
        'gpsLong': gpsLong
    }
    
    response = requests.get(url, params=params)
    
    # 결과를 저장할 리스트
    bus_stations = []
    
    print(f"API 응답 코드: {response.status_code}")
    print(response.content)
    
    # XML 파싱
    try:
        root = ET.fromstring(response.content)
        
        # 데이터 추출
        for item in root.findall(".//item"):
            busstop_id = item.find("nodeid").text  # 정류장 ID
            busstop_name = item.find("nodenm").text  # 정류장 이름
            
            bus_stations.append((busstop_name, busstop_id))
            print(bus_stations)
        
        if not bus_stations:
            print("주변에 버스 정류장이 없습니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")
    
    return bus_stations

def get_bus_numbers_by_node_id(node_id):
    """
    특정 정류장 ID(node_id)를 통해 해당 정류장을 지나는 버스 번호 목록을 조회합니다.
    
    Args:
        node_id (str): 조회할 정류장 ID
        
    Returns:
        list: 해당 정류장을 지나는 버스 번호 목록
    """
    bus_numbers = []
    
    try:
        # MySQL 연결
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 쿼리 실행
        query = "SELECT DISTINCT bus_number FROM bus_stops WHERE node_id = %s"
        cursor.execute(query, (node_id,))
        
        # 결과 가져오기
        results = cursor.fetchall()
        
        # 결과 처리
        if results:
            bus_numbers = [result[0] for result in results]
            print(f"✅ 정류장 ID '{node_id}'를 지나는 버스: {', '.join(bus_numbers)}")
        else:
            print(f"❌ 정류장 ID '{node_id}'에 해당하는 버스를 찾을 수 없습니다.")
        
    except Exception as e:
        print(f"⚠️ 데이터베이스 조회 중 오류 발생: {e}")
    
    finally:
        # 연결 닫기
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("🔒 DB 연결 종료")
    
    return bus_numbers

def get_nearby_bus_info(gpsLati, gpsLong, page_no='1', num_of_rows='10'):
    """
    주어진 GPS 좌표 주변의 버스 정류장 정보와 각 정류장을 지나는 버스 번호를 조회합니다.
    
    Args:
        gpsLati (float): 위도
        gpsLong (float): 경도
        page_no (str): 페이지 번호
        num_of_rows (str): 한 페이지당 결과 수
        
    Returns:
        list: (정류장 이름, 정류장 ID, [버스 번호 리스트]) 튜플로 구성된 리스트
    """
    # 주변 버스 정류장 정보 가져오기
    bus_stations = get_bus_arrival_info(gpsLati, gpsLong, page_no, num_of_rows)
    print(bus_stations)

    if not bus_stations:
        return {
            "status" : "주변_정류장_없음",
            "message" : "해당 위치에서 가까운 정류장이 없습니다."
        }
    # 각 정류장별로 버스 번호 조회
    result = []
    
    for station_name, station_id in bus_stations:
        bus_numbers = get_bus_numbers_by_node_id(station_id)
        result.append({
            "station_name": station_name,
            "station_id": station_id,
            "bus_numbers": bus_numbers
        })

    return {
        "status": "주변_정류장_조회_완료",
        "bus_stations": result
    }

if __name__ == "__main__":
    gpsLati = 34.6073934
    gpsLong = 127.2810466

    nearby_bus_info = get_nearby_bus_info(gpsLati, gpsLong)

    if nearby_bus_info["status"] == "주변_정류장_없음":
        print("\n🚫 주변에 버스 정류장이 없습니다.")
    else:
        print("\n🚏 주변 버스 정류장 및 버스 정보:")
        for station in nearby_bus_info["bus_stations"]:
            print(f"정류장 이름: {station['station_name']}, 정류장 ID: {station['station_id']}")
            if station['bus_numbers']:
                print(f"  버스 번호: {', '.join(station['bus_numbers'])}")
            else:
                print("  버스 정보 없음")
            print("-" * 40)