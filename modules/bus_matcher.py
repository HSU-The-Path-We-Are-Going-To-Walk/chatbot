# 버스 노선 정보 관리 모듈
import external_apis.kakao_places as kakao_places  # 기존 모듈 재사용
import external_apis.nearby_busstop_match as nearby_busstop_match  # 기존 모듈 재사용
import external_apis.bus_arrive_time as bus_arrive_time  # 기존 모듈 재사용

class BusRouteManager:
    """버스 노선 정보를 관리하는 클래스"""
    
    def __init__(self, path_finder):
        """BusRouteManager 초기화"""
        self.path_finder = path_finder
    
    def match_buses(self, destination):
        """목적지 주변의 버스 정류장 및 버스 정보를 찾습니다."""
        try:
            _, x, y = kakao_places.search_keyword_top1(destination)
            nearby_bus_info = nearby_busstop_match.get_nearby_bus_info(y, x)
            
            # 주변 정류장이 없을 경우 처리
            if nearby_bus_info.get("status") == "주변_정류장_없음":
                print("🚫 주변 정류장이 없습니다. 길찾기 수행.")
                return [], []  # 항상 두 개의 값 반환
            
            match_bus_numbers = []
            
            # 정류장 리스트를 순회하면서 버스 번호 추출
            for station in nearby_bus_info.get("bus_stations", []):
                bus_numbers = station.get("bus_numbers", [])
                if isinstance(bus_numbers, list):
                    match_bus_numbers.extend(bus_numbers)
            
            match_bus_numbers = [str(num) for num in match_bus_numbers]
            
            arrival_info = bus_arrive_time.get_bus_arrival_info()
            
            # 두 리스트를 비교하여 일치하는 버스만 필터링
            matching_arrivals = []
            for bus_info in arrival_info:
                if not isinstance(bus_info, (list, tuple)) or len(bus_info) < 2:
                    continue
                
                bus_number = str(bus_info[0])
                arrival_time = bus_info[1]
                
                if bus_number in match_bus_numbers:
                    bus_arrival_info = {
                        "버스번호": bus_number,
                        "도착예정시간": f"{arrival_time}분 후",
                        "도착시간(분)": arrival_time
                    }
                    matching_arrivals.append(bus_arrival_info)
            
            matching_arrivals.sort(key=lambda x: x["도착시간(분)"])
            
            return match_bus_numbers, matching_arrivals
        
        except Exception as e:
            print(f"❌ 버스 매칭 중 오류 발생: {str(e)}")
            return [], []
    
    def process_bus_route(self, destination):
        """버스 노선 정보를 처리합니다."""
        try:
            print(f"🚌 '버스 노선' 의도 처리 시작")
            match_bus_numbers, matching_arrivals = self.match_buses(destination)
            
            if matching_arrivals:
                result = {
                    "status": "버스_도착정보_있음",
                    "match_buses": match_bus_numbers,
                    "arrival_info": matching_arrivals
                }
                return result
            elif match_bus_numbers:
                result = {
                    "status": "버스_도착정보_없음",
                    "match_buses": match_bus_numbers
                }
                return result
            else:
                route, place_name = self.path_finder.find_path(destination)
                result = {
                    "status": "길찾기_수행",
                    "route": route,
                    "place_name": destination
                }
                return result
        
        except Exception as e:
            print(f"❌ 버스 노선 처리 중 오류 발생: {str(e)}")
            error_result = {
                "status": "오류",
                "error_message": f"버스 노선 처리 중 오류가 발생했습니다: {str(e)}"
            }
            return error_result