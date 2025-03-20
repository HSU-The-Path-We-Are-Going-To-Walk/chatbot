import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

SERVICE_KEY = os.getenv("SERVICE_KEY")

def get_bus_arrival_info(gpsLati, gpsLong, page_no='1', num_of_rows='10'):
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
    
    print(response.text)

    # XML 파싱
    try:
        root = ET.fromstring(response.content)
        
        # 데이터 추출
        for item in root.findall(".//item"):
            busstop_id = item.find("nodeid").text  # 정류장 ID
            busstop_name = item.find("nodenm").text  # 정류장 이름

            bus_stations.append((busstop_name, busstop_id))
            
    except Exception as e:
        print(f"오류 발생: {e}")
    
    return bus_stations

if __name__ == "__main__":
    # 예제: 특정 좌표(고흥터미널 근처 좌표)로 테스트
    gpsLati = 34.607249
    gpsLong = 127.280914

    bus_stations = get_bus_arrival_info(gpsLati, gpsLong)
    
    # 결과 출력
    print("🚏 주변 버스 정류장 정보:")
    for name, node_id in bus_stations:
        print(f"정류장 이름: {name}, 정류장 ID: {node_id}")
