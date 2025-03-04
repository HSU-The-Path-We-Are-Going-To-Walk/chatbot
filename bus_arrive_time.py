import requests
import xml.etree.ElementTree as ET

import os

SERVICE_KEY = os.getenv("SERVICE_KEY")

# API 요청
url = 'http://apis.data.go.kr/1613000/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList'
params = {
    'serviceKey': SERVICE_KEY,
    'pageNo': '1',
    'numOfRows': '10',
    '_type': 'xml',
    'cityCode': '37420',
    'nodeId': 'TSB372000244'
}

response = requests.get(url, params=params)

# XML 파싱
root = ET.fromstring(response.content)

# 데이터 추출
for item in root.findall(".//item"):
    bus_number = item.find("routeno").text
    arrival_time = item.find("arrtime").text
    print(f"버스 번호: {bus_number}, 예상 도착 시간: {int(arrival_time) // 60}분 후")
