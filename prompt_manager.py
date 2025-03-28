from typing import List

class PromptManager:
    @staticmethod
    def convert_to_conversation(text: str, type: str) -> str:
        """형식적인 텍스트를 대화형으로 변환하는 프롬프트"""
        
        # 실제 프로덕션에서는 이 부분에 LLM 호출이 들어갈 것입니다
        # 여기서는 간단한 텍스트 변환 로직을 사용합니다
        if type == "경로":
            if "결과를 표시할 수 없어요" in text or "경로를 찾을 수 없습니다" in text:
                return f"죄송합니다. {text.replace('길찾기 결과를 표시할 수 없어요.', '목적지까지 가는 경로를 찾지 못했어요.')}"
            
            return f"{text.replace('1.', '먼저').replace('2.', '그다음에')} 이렇게 가시면 됩니다."
        
        elif type == "위치":
            if not text or text.strip() == "":
                return "죄송합니다. 해당 위치를 찾을 수 없습니다. 다른 키워드로 검색해 보시겠어요?"
            
            return f"제가 찾아본 결과, {text} 이 위치들이 있네요."
        
        elif type == "버스_경로":
            if "버스가 없으며" in text or "대체 경로도 찾을 수 없습니다" in text:
                return "죄송합니다. 해당 목적지까지 가는 버스 노선이 없고, 대체 경로도 찾을 수 없네요. 다른 방법으로 가는 방법을 찾아보시겠어요?"
            
            return text
        
        # 기본 응답
        return text 