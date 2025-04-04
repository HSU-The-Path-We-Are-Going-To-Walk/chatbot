import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

load_dotenv()
SERVICE_KEY = os.getenv("SERVICE_KEY")

def get_bus_arrival_info(city_code='36350', node_id='TSB332000523', page_no='1', num_of_rows='10'):
    """
    버스 도착 정보를 조회하는 함수
    
    Parameters:
        city_code (str): 도시 코드
        node_id (str): 정류장 ID
        page_no (str): 페이지 번호
        num_of_rows (str): 한 페이지당 결과 수
        
    Returns:
        list: 버스 도착 정보 리스트 (버스번호, 도착예정시간(분))
    """
    
    # API 요청
    url = 'http://apis.data.go.kr/1613000/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList'
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        '_type': 'xml',
        'cityCode': city_code,
        'nodeId': node_id
    }
    
    response = requests.get(url, params=params)
    
    # print(response.text)

    # 결과를 저장할 리스트
    bus_arrivals = []
    
    # XML 파싱
    try:
        root = ET.fromstring(response.content)
        
        # 데이터 추출
        for item in root.findall(".//item"):
            prev_count = item.find("arrprevstationcnt").text
            bus_number = item.find("routeno").text
            arrival_time = item.find("arrtime").text
            arrival_minutes = int(arrival_time) // 60

            bus_arrivals.append((bus_number, arrival_minutes, prev_count))
            
        # 더미 데이터 => 시연 목적
        bus_arrivals.append((110, 10, 3))
        bus_arrivals.append((111, 15, 5))
        bus_arrivals.append((112, 5, 1))
        
        bus_arrivals.sort(key=lambda x: x[1])
    except Exception as e:
        print(f"오류 발생: {e}")
    
    return bus_arrivals

if __name__ == "__main__":
    arrivals = get_bus_arrival_info()
    
    # 도착 시간이 빠른 순서대로 정렬
    arrivals.sort(key=lambda x: x[1])
    
    # 정렬된 결과 출력
    for bus_number, arrival_minutes, prev_count in arrivals:
        print(f"버스 번호: {bus_number}, 남은 정거장 수: {prev_count} 예상 도착 시간: {arrival_minutes}분 후")