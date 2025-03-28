import requests
import pymysql
import os
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

# API 요청 URL
API_URL = "http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList"
CITY_CODE = "36350"
ROUTE_ID = "TSB332000278"  # 버스 노선 ID
BUS_NUMBER = "151"  # 버스 번호

# MySQL 테이블 생성 쿼리
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS bus_stops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bus_number VARCHAR(10),
    route_id VARCHAR(50),
    node_id VARCHAR(50),
    node_name VARCHAR(100),
    latitude DOUBLE,
    longitude DOUBLE,
    node_order INT
);
"""

# API 요청 파라미터
params = {
    "serviceKey": SERVICE_KEY,
    "numOfRows": 100,
    "cityCode": CITY_CODE,
    "routeId": ROUTE_ID,
    "_type": "json"
}

print("🚀 API 요청 중...")
response = requests.get(API_URL, params=params)
data = response.json()
items = data["response"]["body"]["items"]["item"]  # 정류장 리스트
print(f"✅ API 응답 완료! 정류장 개수: {len(items)}개")

# MySQL 연결 및 데이터 삽입
try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 테이블 생성
    cursor.execute(CREATE_TABLE_QUERY)
    print("✅ 테이블 확인 완료!")

    # 데이터 삽입
    INSERT_QUERY = """
    INSERT INTO bus_stops (bus_number, route_id, node_id, node_name, latitude, longitude, node_order)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    print("📝 데이터 삽입 중...")
    for item in items:
        values = (BUS_NUMBER, ROUTE_ID, item["nodeid"], item["nodenm"], item["gpslati"], item["gpslong"], item["nodeord"])
        cursor.execute(INSERT_QUERY, values)
        print(f"   ➡️ {item['nodeord']}번 정류장: {item['nodenm']} ({item['gpslati']}, {item['gpslong']})")

    # 변경 사항 저장
    conn.commit()
    print("✅ MySQL 데이터 삽입 완료!")

except Exception as e:
    print(f"⚠️ 오류 발생: {e}")

finally:
    cursor.close()
    conn.close()
    print("🔒 DB 연결 종료")
