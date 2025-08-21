from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from app.config import get_openai_llm
from agents.numerology_agent import build_numerology_agent
from agents.trading_agent import build_trading_agent
from agents.synthesizer_agent import build_synthesizer_agent


def build_router_agent():
    """Tạo Router Agent để thực thi các task theo kế hoạch"""
    
    system_prompt = """Bạn là Router Agent trong hệ thống tư vấn đầu tư và thần số học.

Nhiệm vụ: Thực thi các task theo thứ tự và cập nhật trạng thái của chúng dựa trên kế hoạch từ Supervisor Agent.

## Quy tắc hoạt động:
1. Đọc kế hoạch từ `state.plan`
2. Chọn task đầu tiên có `status` là "pending"
3. Kích hoạt Agent chuyên biệt tương ứng
4. Cập nhật `status` của task thành "running" khi bắt đầu
5. Cập nhật `status` thành "completed" khi hoàn thành
6. Cập nhật `status` thành "failed" nếu có lỗi
7. Lặp lại cho đến khi tất cả task hoàn thành

## Các Agent chuyên biệt:
- **NumerologyAgent**: Xử lý câu hỏi thần số học, tính toán chỉ số cá nhân
- **TradingAgent**: Phân tích dữ liệu giao dịch, đánh giá hiệu suất
- **SynthesizerAgent**: Tổng hợp thông tin từ các agent khác

## Cấu trúc kế hoạch:
```json
{
  "description": "Mô tả kế hoạch",
  "kind": "simple|single|combo",
  "tasks": [
    {
      "step": 1,
      "agent": "NumerologyAgent|TradingAgent|SynthesizerAgent",
      "action": "hành động cụ thể",
      "input": {...},
      "output_key": "tên trường lưu kết quả",
      "status": "pending|running|completed|failed"
    }
  ]
}
```

## Output:
Trả về state đã được cập nhật với:
- Task status được cập nhật
- Kết quả từ các agent được lưu vào `tool_output_<agent_name>`
- Thông tin về task đã thực thi

Chỉ trả về JSON, không có text khác."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Kế hoạch hiện tại: {plan}
Thông tin người dùng: {user_info}
Câu hỏi: {question}

Hãy thực thi task tiếp theo và cập nhật trạng thái:""")
    ])

    chain = prompt | get_openai_llm() | StrOutputParser()
    return chain


def execute_task(task: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Thực thi một task cụ thể và cập nhật state
    
    Args:
        task: Task cần thực thi
        state: State hiện tại của hệ thống
        
    Returns:
        State đã được cập nhật
    """
    try:
        # Cập nhật status thành "running"
        task["status"] = "running"
        
        # Xác định agent cần sử dụng
        agent_name = task["agent"]
        action = task["action"]
        input_data = task["input"]
        output_key = task["output_key"]
        
        # Thực thi task dựa trên agent
        if agent_name == "NumerologyAgent":
            result = execute_numerology_task(action, input_data)
        elif agent_name == "TradingAgent":
            result = execute_trading_task(action, input_data)
        elif agent_name == "SynthesizerAgent":
            result = execute_synthesizer_task(action, input_data)
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        # Lưu kết quả vào state
        state[output_key] = result
        
        # Cập nhật status thành "completed"
        task["status"] = "completed"
        
        return state
        
    except Exception as e:
        # Cập nhật status thành "failed" nếu có lỗi
        task["status"] = "failed"
        task["error"] = str(e)
        
        # Lưu thông tin lỗi vào state
        error_key = f"error_{output_key}" if output_key else "error"
        state[error_key] = {
            "message": str(e),
            "task": task
        }
        
        return state


def execute_numerology_task(action: str, input_data: Dict[str, Any]) -> str:
    """Thực thi task của NumerologyAgent"""
    agent = build_numerology_agent()
    
    # Chuẩn bị input cho agent
    inputs = {
        "question": input_data.get("question", ""),
        "user_name": input_data.get("user_name", ""),
        "dob": input_data.get("dob", ""),
        "excel_path": input_data.get("excel_path", "")
    }
    
    # Gọi agent
    result = agent.invoke(inputs)
    return result


def execute_trading_task(action: str, input_data: Dict[str, Any]) -> str:
    """Thực thi task của TradingAgent"""
    agent = build_trading_agent()
    
    # Chuẩn bị input cho agent
    inputs = {
        "question": input_data.get("question", ""),
        "excel_path": input_data.get("excel_path", ""),
        "user_name": input_data.get("user_name", ""),
        "dob": input_data.get("dob", "")
    }
    
    # Gọi agent
    result = agent.invoke(inputs)
    return result


def execute_synthesizer_task(action: str, input_data: Dict[str, Any]) -> str:
    """Thực thi task của SynthesizerAgent"""
    agent = build_synthesizer_agent()
    
    # Chuẩn bị input cho agent
    inputs = {
        "question": input_data.get("question", ""),
        "numerology_output": input_data.get("numerology_output", ""),
        "trading_output": input_data.get("trading_output", ""),
        "user_name": input_data.get("user_name", ""),
        "dob": input_data.get("dob", "")
    }
    
    # Gọi agent
    result = agent.invoke(inputs)
    return result


def route_and_execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hàm chính để routing và thực thi các task
    
    Args:
        state: State hiện tại của hệ thống
        
    Returns:
        State đã được cập nhật sau khi thực thi
    """
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    # Tìm task đầu tiên có status "pending"
    pending_tasks = [task for task in tasks if task.get("status") == "pending"]
    
    if not pending_tasks:
        # Không có task nào pending, trả về state hiện tại
        return state
    
    # Thực thi task đầu tiên
    next_task = pending_tasks[0]
    updated_state = execute_task(next_task, state)
    
    return updated_state


def get_next_pending_task(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Lấy task tiếp theo cần thực thi
    
    Args:
        state: State hiện tại
        
    Returns:
        Task tiếp theo hoặc None nếu không có
    """
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    for task in tasks:
        if task.get("status") == "pending":
            return task
    
    return None


def is_all_tasks_completed(state: Dict[str, Any]) -> bool:
    """
    Kiểm tra xem tất cả task đã hoàn thành chưa
    
    Args:
        state: State hiện tại
        
    Returns:
        True nếu tất cả task đã hoàn thành
    """
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    if not tasks:
        return True
    
    for task in tasks:
        if task.get("status") not in ["completed", "failed"]:
            return False
    
    return True


def get_execution_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo báo cáo tổng quan về việc thực thi
    
    Args:
        state: State hiện tại
        
    Returns:
        Báo cáo tổng quan
    """
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    summary = {
        "total_tasks": len(tasks),
        "completed": 0,
        "failed": 0,
        "pending": 0,
        "running": 0,
        "errors": []
    }
    
    for task in tasks:
        status = task.get("status", "unknown")
        summary[status] = summary.get(status, 0) + 1
        
        if status == "failed":
            summary["errors"].append({
                "step": task.get("step"),
                "agent": task.get("agent"),
                "error": task.get("error", "Unknown error")
            })
    
    return summary
