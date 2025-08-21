
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    question: str = Field(..., description="User's question")


class ChatResponse(BaseModel):
    final_answer: str
    trace: Optional[Dict[str, Any]] = None


class NumerologyRequest(BaseModel):
    user_name: str = Field(..., description="Họ và tên đầy đủ")
    birthday: str = Field(..., description="Ngày sinh dạng dd/mm/yyyy")
    question: str = Field(..., description="Câu hỏi của người dùng")


class NumerologyResponse(BaseModel):
    indicators: Dict[str, Any]
    selected_indicators: List[str]
    numbers: Dict[str, Any]
    meanings: Dict[str, Any]
    docs: Dict[str, Any]
    milestone_info: Optional[Dict[str, Any]] = None


class TradingRequest(BaseModel):
    question: str = Field(..., description="Câu hỏi của người dùng")
    excel_path: Optional[str] = Field(None, description="Đường dẫn file Excel dữ liệu giao dịch (optional)")


class TradingResponse(BaseModel):
    success: bool
    focused_report: Optional[str] = None
    trading_data: Optional[Dict[str, Any]] = None
    analysis_needs: Optional[Dict[str, Any]] = None
    data_summary: Optional[Dict[str, Any]] = None
    issues: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
