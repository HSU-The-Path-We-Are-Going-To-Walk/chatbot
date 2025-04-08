# 길찾기 모듈
import external_apis.kakao_places as kakao_places  # 기존 모듈 재사용
import external_apis.path_sk as path_sk  # 기존 모듈 재사용
import json
import re

class PathFinder:
    """경로를 검색하고 결과를 포맷팅하는 클래스"""
    
    def find_path(self, destination):
        """목적지까지의 경로를 찾습니다."""
        try:
            result = kakao_places.search_keyword_top1(destination)
            
            print(f"🔍 검색된 장소 결과: {result}")
            place_name, x, y = result
            
            print(f"🔍 검색된 장소: {place_name}, 좌표: ({x}, {y})")
            directions = path_sk.get_transit_route(x, y)
            
            if isinstance(directions, dict) and "error" in directions:
                return directions['error'], place_name
            
            return directions, place_name
        
        except Exception as e:
            print(f"❌ 경로 찾기 중 오류 발생: {str(e)}")
            return f"경로 찾기 중 오류 발생: {str(e)}", None
    
    def format_path_result(self, route_data, place_name):
        """경로 데이터를 사용자에게 친숙한 형식으로 변환합니다."""
        print(f"🔍 경로 데이터: {route_data}")
        
        try:
            # 장소명으로 좌표 검색
            result = kakao_places.search_keyword_top1(place_name)
            if result and len(result) == 3:
                place_name, x, y = result
                print(f"🔍 좌표 검색 결과: {place_name}, X: {x}, Y: {y}")
                coordinates = [[float(x), float(y)]]  # 좌표를 2차원 배열로 변환
            else:
                print("⚠️ 좌표 검색 실패")
                coordinates = []
        except Exception as e:
            print(f"❌ 좌표 검색 중 오류: {str(e)}")
            coordinates = []
        
        # 출발지와 도착지가 너무 가까운 경우
        if route_data == "출발지와 도착지가 너무 가까움":
            routes_text = f"{place_name}은 현재 위치에서 가까운 거리에 있습니다. 도보로 이동 가능합니다."
            return {
                "place_name": place_name,
                "routes_text": routes_text,
                "formatted_coordinates": coordinates
            }
        
        # 검색 결과가 없는 경우
        elif route_data == "검색 결과가 없습니다. 다시 시도해 주세요" or route_data is None:
            routes_text = f"{place_name}까지의 경로를 찾을 수 없습니다. 다른 장소를 검색해 보시겠어요?"
            return {
                "place_name": place_name,
                "routes_text": routes_text,
                "formatted_coordinates": coordinates
            }
        
        # 오류 발생 경우
        elif isinstance(route_data, str) and route_data.startswith("경로 찾기 중 오류"):
            routes_text = f"{place_name}까지의 경로를 검색하는 중에 문제가 발생했습니다. 잠시 후 다시 시도해 주세요."
            return {
                "place_name": place_name,
                "routes_text": routes_text,
                "formatted_coordinates": coordinates
            }
        
        # 빈 경로 데이터
        elif not route_data or (isinstance(route_data, str) and route_data.strip() == ""):
            routes_text = f"{place_name}까지의 경로 정보가 없습니다."
            return {
                "place_name": place_name,
                "routes_text": routes_text,
                "formatted_coordinates": coordinates
            }
        
        # 경로 데이터가 리스트 형태인 경우 처리
        if isinstance(route_data, list):
            routes = []
            route_coordinates = []
            
            for idx, item in enumerate(route_data, start=1):
                if isinstance(item, tuple) and len(item) == 2:
                    description, coords = item
                    routes.append(f"{idx}. {description}.")
                    
                    # 각 좌표 쌍을 배열로 추가
                    for coord_pair in coords:
                        if isinstance(coord_pair, tuple) and len(coord_pair) == 2:
                            route_coordinates.append([float(coord_pair[0]), float(coord_pair[1])])
            
            routes_text = "\n".join(routes)
            
            # 경로 좌표가 없으면 목적지 좌표만 사용
            if not route_coordinates and coordinates:
                route_coordinates = coordinates
            
            return {
                "place_name": place_name,
                "routes_text": f"{place_name}까지의 경로:\n{routes_text}",
                "formatted_coordinates": route_coordinates
            }
        
        # 그 외 경우
        else:
            print(f"❌ 알 수 없는 형식의 경로 데이터")
            return {
                "place_name": place_name,
                "routes_text": "길찾기 결과를 표시할 수 없어요. 다시 시도해 주세요",
                "formatted_coordinates": coordinates
            }
