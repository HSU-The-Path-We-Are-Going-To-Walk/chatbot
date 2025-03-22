# 장소 검색 모듈
import external_apis.kakao_places as kakao_places  # 기존 모듈 재사용

class PlaceSearcher:
    """장소를 검색하는 클래스"""
    
    def find_places(self, destination):
        """목적지를 검색하여 최대 3개의 장소를 반환합니다."""
        try:
            results = kakao_places.search_keyword_top3(destination)
            
            if not results:
                print("⚠️ 검색된 장소가 없습니다.")
                return []
            
            print("✅ 장소 찾기 결과:")
            for idx, (place_name, x, y) in enumerate(results, start=1):
                print(f"   {idx}. {place_name} (X: {x}, Y: {y})")
            
            return results  # [(place_name1, x1, y1), (place_name2, x2, y2), (place_name3, x3, y3)]
        
        except Exception as e:
            print(f"❌ 장소 검색 중 오류 발생: {str(e)}")
            return []