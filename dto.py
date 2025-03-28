from typing import List, Optional, Tuple, Any
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class PlaceInfo(BaseModel):
    name: str
    x: float
    y: float

class LocationSearchResponse(BaseModel):
    intent: str = "위치 찾기"
    destination: str
    places: List[PlaceInfo]
    success: bool
    message: str

class RouteInfo(BaseModel):
    routes_text: str
    coordinates: str

class PathFindingResponse(BaseModel):
    intent: str = "길찾기"
    destination: str
    route_info: Optional[RouteInfo]
    success: bool
    message: str

class BusArrivalInfo(BaseModel):
    bus_number: str
    arrival_time: str

class BusRouteResponse(BaseModel):
    intent: str = "버스 노선"
    destination: str
    matched_buses: List[str]
    arrival_info: Optional[List[BusArrivalInfo]]
    route_info: Optional[RouteInfo]  # 버스가 없을 경우 길찾기 결과 제공
    success: bool
    message: str

class GeneralResponse(BaseModel):
    response: str
    success: bool

class LocationInfo(BaseModel):
    places: List[str]  # 검색된 장소명들
    coordinates: List[Tuple[float, float]]  # 좌표들
    conversation_response: str  # 프롬프트로 생성된 대화형 응답

class PathInfo(BaseModel):
    routes_text: str  # 형식적인 경로 텍스트
    coordinates: List[List[float]]  # 좌표들 배열로 변경
    conversation_response: str  # 프롬프트로 생성된 대화형 응답

class BusInfo(BaseModel):
    available_buses: List[str]  # 이용 가능한 버스 번호들
    arrival_times: List[dict[str, str]]  # 버스별 도착 시간 정보
    alternative_path: Optional[PathInfo] = None  # 버스가 없을 경우의 대체 경로
    conversation_response: str  # 프롬프트로 생성된 대화형 응답 