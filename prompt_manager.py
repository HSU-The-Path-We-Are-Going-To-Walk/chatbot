from typing import List
import re

class PromptManager:
    @staticmethod
    def _convert_numbers_to_korean_ordinals(text: str) -> str:
        """숫자 형식(1., 2. 등)을 한국어 서수사(첫 번째, 두 번째 등)로 변환"""
        korean_ordinals = ['첫 번째', '두 번째', '세 번째', '네 번째', '다섯 번째', 
                          '여섯 번째', '일곱 번째', '여덟 번째', '아홉 번째', '열 번째']
        
        def replace_with_ordinal(match):
            num = int(match.group(1))
            if 1 <= num <= len(korean_ordinals):
                return f"{korean_ordinals[num-1]},"
            return f"{num}번째,"  # 10 이상의 숫자는 그냥 '숫자번째'로 표시
        
        # 마지막 쉼표는 제거
        result = re.sub(r'(\d+)\.', replace_with_ordinal, text)
        return result.rstrip(',')
    
    @staticmethod
    def convert_to_conversation(text: str, type: str) -> str:
        """형식적인 텍스트를 대화형으로 변환하는 프롬프트"""
        
        # 실제 프로덕션에서는 이 부분에 LLM 호출이 들어갈 것입니다
        # 여기서는 간단한 텍스트 변환 로직을 사용합니다
        if type == "경로":
            if "결과를 표시할 수 없어요" in text or "경로를 찾을 수 없습니다" in text:
                return f"죄송합니다. {text.replace('길찾기 결과를 표시할 수 없어요.', '목적지까지 가는 경로를 찾지 못했어요.')}"
            
            # "도보로 이용"을 "도보로 이동"으로 변경
            text = text.replace("도보로 이용", "도보로 이동")
            
            # 정규식을 사용하여 숫자 형식을 한국어 서수사로 변환
            modified_text = PromptManager._convert_numbers_to_korean_ordinals(text)
            return f"{modified_text} 하세요."
        
        elif type == "위치":
            if not text or text.strip() == "":
                return "죄송합니다. 해당 위치를 찾을 수 없습니다. 다른 키워드로 검색해 보시겠어요?"
            
            return f"제가 찾아본 결과, {text} 이 위치들이 있네요."
        
        elif type == "버스_경로":
            if "버스가 없으며" in text or "대체 경로도 찾을 수 없습니다" in text:
                return "죄송합니다. 해당 목적지까지 가는 버스 노선이 없고, 대체 경로도 찾을 수 없네요. 다른 방법으로 가는 방법을 찾아보시겠어요?"
            
            # 버스 경로에 대한 더 친절한 응답으로 변경
            if "버스가 없습니다" in text:
                # "도보로 이용"을 "도보로 이동"으로 변경
                clean_text = text.replace('가는 버스가 없습니다. 대신 길찾기 결과를 알려드립니다.', '').replace("도보로 이용", "도보로 이동")
                modified_text = PromptManager._convert_numbers_to_korean_ordinals(clean_text)
                return f"죄송합니다. 해당 목적지까지 직접 가는 버스는 없네요. 대신 다른 방법으로 가는 경로를 알려드릴게요.\n{modified_text} 이렇게 가시면 됩니다."
            elif "경로:" in text:
                # 목적지와 경로 부분 분리
                destination = text.split("까지의 경로:")[0] if "까지의 경로:" in text else ""
                routes = text.split("경로:")[-1] if "경로:" in text else text
                
                # "도보로 이용"을 "도보로 이동"으로 변경
                routes = routes.replace("도보로 이용", "도보로 이동")
                
                # 정규식을 사용하여 숫자 형식을 한국어 서수사로 변환
                modified_routes = PromptManager._convert_numbers_to_korean_ordinals(routes)
                return f"{destination}까지 가는 경로를 안내해 드릴게요.\n{modified_routes} 이렇게 가시면 됩니다."
            
            return text
        
        # 기본 응답
        return text 