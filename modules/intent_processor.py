# 의도 감지 및 목적지 추출 모듈
class IntentProcessor:
    """사용자 메시지에서 의도와 목적지를 감지하는 클래스"""
    
    def __init__(self, llm):
        """LLM을 사용하여 IntentProcessor 초기화"""
        self.llm = llm
    
    def detect_intent_and_extract_destination(self, user_message):
        """사용자 메시지를 분석하여 의도와 목적지를 추출합니다."""
        prompt = f"""
        사용자의 메시지를 분석하여 의도와 목적지를 파악하세요.
        
        반환 형식 예시:
        - 길찾기: "의도: 길찾기, 목적지: 울진고등학교"
        - 버스 노선: "의도: 버스 노선, 목적지: 연호체육공원"
        - 위치 찾기: "의도: 위치 찾기, 목적지: 편의점"
        - 기타: "의도: 기타"
        
        사용자 입력: "{user_message}"
        """
        
        try:
            result = self.llm.invoke(prompt).content
            
            intent = None
            destination = None
            
            if "의도: 길찾기" in result:
                intent = "길찾기"
            elif "의도: 버스 노선" in result:
                intent = "버스 노선"
            elif "의도: 위치 찾기" in result:
                intent = "위치 찾기"
            
            if "목적지:" in result:
                destination = result.split("목적지:")[-1].strip()
                destination = destination.replace('"', '').replace("'", "")
                destination = destination.rstrip('".\',:;')
            
            return intent, destination
        
        except Exception as e:
            print(f"❌ 의도 감지 중 오류 발생: {str(e)}")
            print(f"🔍 원본 응답: {result if 'result' in locals() else '없음'}")
            return None, None
