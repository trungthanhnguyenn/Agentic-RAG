import os
import json
from typing import Dict, Any, List

from langgraph.graph import StateGraph, END

# Import START với fallback cho các phiên bản khác nhau
try:
    from langgraph.graph import START
except ImportError:
    try:
        from langgraph.constants import START
    except ImportError:
        try:
            from langgraph.graph.state import START
        except ImportError:
            START = "__start__"

from graph.state import AgentState
from agents.supervisor import smart_route_plan
from agents.context_enricher_agent import build_context_enricher
from agents.numerology_agent import build_numerology_agent
from agents.trading_agent import build_trading_agent
from agents.synthesizer_agent import build_synthesizer_agent
from agents.router_agent import route_and_execute
from app.config import get_openai_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


def build_smart_router():
    """Tạo LLM chain cho smart routing decisions"""
    system_prompt = """Bạn là SmartRouter trong hệ thống tư vấn đầu tư và thần số học.

## Nhiệm vụ:
Phân tích trạng thái hiện tại của hệ thống và quyết định agent tiếp theo cần được kích hoạt.

## Thông tin đầu vào:
- plan: Kế hoạch hiện tại với danh sách tasks
- current_state: Trạng thái hiện tại của hệ thống
- available_agents: Danh sách các agent có thể kích hoạt

## Quy tắc routing:
1. **Ưu tiên tasks pending**: Luôn chọn task có status "pending" đầu tiên
2. **Kiểm tra dependencies**: Đảm bảo các task phụ thuộc đã hoàn thành
3. **Error handling**: Nếu task trước đó failed, có thể skip hoặc retry
4. **Completion check**: Nếu tất cả tasks hoàn thành, chuyển đến final_node

## Output format:
Trả về JSON với cấu trúc:
```json
{
  "next_node": "tên_node_tiếp_theo",
  "reasoning": "lý do cho quyết định",
  "should_continue": true/false,
  "error_handling": "cách xử lý lỗi nếu có"
}
```

## Các node có thể chọn:
- "numerology_node": Khi cần NumerologyAgent
- "trading_node": Khi cần TradingAgent  
- "synthesizer_node": Khi cần SynthesizerAgent
- "final_node": Khi hoàn thành hoặc có lỗi
- "error_node": Khi cần xử lý lỗi đặc biệt

⚠️ CHỈ TRẢ VỀ JSON THUẦN TÚY, KHÔNG CHỨA KÝ TỰ "```json" HOẶC "```"
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Plan hiện tại: {plan}
Trạng thái hiện tại: {current_state}
Agent có sẵn: {available_agents}

Quyết định routing:""")
    ])

    chain = prompt | get_openai_llm() | StrOutputParser()
    return chain


def smart_route_node(state: AgentState) -> AgentState:
    """Node thông minh để quyết định routing dựa trên LLM reasoning"""
    try:
        chain = build_smart_router()
        
        # Chuẩn bị context cho LLM
        plan = state.get("plan", {})
        current_state = {
            "question": state.get("question", ""),
            "enrichment": state.get("enrichment", {}),
            "tool_output": state.get("tool_output", {}),
            "errors": [k for k, v in state.items() if k.startswith("error")]
        }
        available_agents = ["numerology_node", "trading_node", "synthesizer_node", "final_node"]
        
        # Gọi LLM để quyết định
        result = chain.invoke({
            "plan": json.dumps(plan, ensure_ascii=False),
            "current_state": json.dumps(current_state, ensure_ascii=False),
            "available_agents": json.dumps(available_agents, ensure_ascii=False)
        })
        
        # Parse kết quả
        try:
            routing_decision = json.loads(result.strip())
            return {"routing_decision": routing_decision}
        except json.JSONDecodeError:
            # Fallback to traditional logic
            return {"routing_decision": {"next_node": "final_node", "reasoning": "JSON parse failed"}}
            
    except Exception as e:
        # Fallback to traditional logic
        return {"routing_decision": {"next_node": "final_node", "reasoning": f"Error: {str(e)}"}}


def initial_node(state: AgentState) -> AgentState:
    """Khởi tạo state ban đầu"""
    return {}


def enricher_node(state: AgentState) -> AgentState:
    """Làm giàu ngữ cảnh câu hỏi trước khi routing"""
    agent = build_context_enricher()
    raw = agent.invoke({
        "question": state["question"],
        "user_name": state.get("user_name"),
        "birthday": state.get("birthday"),
        "excel_path": state.get("excel_path"),
    })
    
    # Parse JSON output
    import json
    enrichment: Dict[str, Any] = {}
    try:
        enrichment = json.loads(raw.strip())
    except Exception:
        # Fallback nếu parse JSON thất bại - SỬ DỤNG LLM REASONING
        try:
            fallback_chain = build_context_enrichment_fallback()
            fallback_result = fallback_chain.invoke({
                "question": state["question"],
                "raw_response": raw
            })
            enrichment = json.loads(fallback_result.strip())
        except Exception:
            # Final fallback với logic thông minh hơn
            enrichment = build_intelligent_fallback_enrichment(state["question"])
    
    return {"enrichment": enrichment}


def build_context_enrichment_fallback():
    """Tạo LLM chain để xử lý fallback cho context enrichment"""
    system_prompt = """Bạn là ContextEnrichmentFallback.

## Nhiệm vụ:
Khi ContextEnricherAgent trả về response không phải JSON hợp lệ, bạn cần:
1. Phân tích câu hỏi gốc
2. Phân tích response thô từ agent
3. Tạo ra enrichment JSON hợp lệ

## Output format:
```json
{
  "intent": "mục đích của câu hỏi",
  "needs": {
    "numerology": true/false,
    "trading": true/false,
    "synthesis": true/false
  },
  "missing_inputs": ["danh sách thông tin thiếu"],
  "suggested_questions": ["câu hỏi gợi ý"],
  "complexity": "low|moderate|high",
  "recommended_approach": "simple|single|combo"
}
```

⚠️ CHỈ TRẢ VỀ JSON THUẦN TÚY!"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Câu hỏi gốc: {question}
Response thô từ agent: {raw_response}

Tạo enrichment JSON:""")
    ])

    chain = prompt | get_openai_llm() | StrOutputParser()
    return chain


def build_intelligent_fallback_enrichment(question: str) -> Dict[str, Any]:
    """Tạo enrichment thông minh dựa trên semantic analysis"""
    system_prompt = """Bạn là IntelligentEnrichmentAnalyzer.

## Nhiệm vụ:
Phân tích câu hỏi để tạo enrichment JSON thông minh, không dựa vào từ khóa đơn giản.

## Phân tích semantic:
- Hiểu ý định thực sự của người dùng
- Xác định loại thông tin cần thiết
- Đánh giá độ phức tạp của câu hỏi
- Gợi ý cách tiếp cận phù hợp

## Output format:
```json
{
  "intent": "mô tả ý định chi tiết",
  "needs": {
    "numerology": true/false,
    "trading": true/false,
    "synthesis": true/false
  },
  "missing_inputs": ["thông tin cần bổ sung"],
  "suggested_questions": ["câu hỏi follow-up"],
  "complexity": "low|moderate|high",
  "recommended_approach": "simple|single|combo",
  "semantic_analysis": {
    "primary_focus": "numerology|trading|both",
    "confidence_level": "high|medium|low",
    "requires_personalization": true/false
  }
}
```

⚠️ CHỈ TRẢ VỀ JSON THUẦN TÚY!"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"Phân tích câu hỏi: {question}")
    ])

    chain = prompt | get_openai_llm() | StrOutputParser()
    
    try:
        result = chain.invoke({"question": question})
        return json.loads(result.strip())
    except Exception:
        # Final fallback
        return {
            "intent": "Phân tích câu hỏi",
            "needs": {"numerology": True, "trading": True, "synthesis": True},
            "missing_inputs": [],
            "suggested_questions": [],
            "complexity": "moderate",
            "recommended_approach": "combo"
        }


def router_node(state: AgentState) -> AgentState:
    """Lập kế hoạch routing dựa trên câu hỏi và enrichment"""
    plan = smart_route_plan(state["question"], state.get("enrichment"))
    
    # Khởi tạo completed_agents nếu chưa có
    if "completed_agents" not in state:
        state["completed_agents"] = []
    
    return {"plan": plan}


def numerology_node(state: AgentState) -> AgentState:
    """Chạy NumerologyAgent theo task-based plan với LLM reasoning"""
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    # Tìm task NumerologyAgent đang pending
    numerology_task = None
    for task in tasks:
        if task.get("agent") == "NumerologyAgent" and task.get("status") == "pending":
            numerology_task = task
            break
    
    if not numerology_task:
        return {}
    
    # Cập nhật task status thành "running"
    numerology_task["status"] = "running"
    
    try:
        # Chạy NumerologyAgent với context enhancement
        agent = build_numerology_agent()
        
        # Chuẩn bị input với reasoning context
        input_data = {
            "question": state["question"],
            "user_name": state.get("user_name"),
            "birthday": state.get("birthday"),
            "enrichment": state.get("enrichment", {}),
            "plan_context": numerology_task.get("action", "calculate_and_interpret")
        }
        
        result = agent.invoke(input_data)
        
        # Cập nhật task status thành "completed" và lưu kết quả
        numerology_task["status"] = "completed"
        numerology_task["result"] = result
        
        # Cập nhật tool_output
        tool_output = dict(state.get("tool_output", {}))
        tool_output["numerology"] = result
        
        return {
            "tool_output": tool_output
        }
        
    except Exception as e:
        # Cập nhật task status thành "failed"
        numerology_task["status"] = "failed"
        numerology_task["error"] = str(e)
        
        return {
            "error": f"NumerologyAgent failed: {str(e)}"
        }


def trading_node(state: AgentState) -> AgentState:
    """Chạy TradingAgent theo task-based plan với LLM reasoning"""
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    # Tìm task TradingAgent đang pending
    trading_task = None
    for task in tasks:
        if task.get("agent") == "TradingAgent" and task.get("status") == "pending":
            trading_task = task
            break
    
    if not trading_task:
        return {}
    
    # Cập nhật task status thành "running"
    trading_task["status"] = "running"
    
    try:
        # Chạy TradingAgent với context enhancement
        agent = build_trading_agent()
        
        # Chuẩn bị input với reasoning context
        input_data = {
            "question": state["question"],
            "excel_path": state.get("excel_path"),
            "enrichment": state.get("enrichment", {}),
            "plan_context": trading_task.get("action", "analyze_performance"),
            "numerology_context": state.get("tool_output", {}).get("numerology", "")
        }
        
        result = agent.invoke(input_data)
        
        # Cập nhật task status thành "completed" và lưu kết quả
        trading_task["status"] = "completed"
        trading_task["result"] = result
        
        # Cập nhật tool_output
        tool_output = dict(state.get("tool_output", {}))
        tool_output["trading"] = result
        
        return {
            "tool_output": tool_output
        }
        
    except Exception as e:
        # Cập nhật task status thành "failed"
        trading_task["status"] = "failed"
        trading_task["error"] = str(e)
        
        return {
            "error": f"TradingAgent failed: {str(e)}"
        }


def synthesizer_node(state: AgentState) -> AgentState:
    """Chạy SynthesizerAgent theo task-based plan với LLM reasoning"""
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    # Tìm task SynthesizerAgent đang pending
    synthesizer_task = None
    for task in tasks:
        if task.get("agent") == "SynthesizerAgent" and task.get("status") == "pending":
            synthesizer_task = task
            break
    
    if not synthesizer_task:
        return {}
    
    # Cập nhật task status thành "running"
    synthesizer_task["status"] = "running"
    
    try:
        # Chạy SynthesizerAgent với context enhancement
        agent = build_synthesizer_agent()
        
        # Lấy dữ liệu từ tool_output
        tool_output = state.get("tool_output", {})
        numerology_data = tool_output.get("numerology", "")
        trading_data = tool_output.get("trading", "")
        
        # Chuẩn bị input với reasoning context
        input_data = {
            "question": state["question"],
            "numerology": numerology_data,
            "trading": trading_data,
            "enrichment": state.get("enrichment", {}),
            "plan_context": synthesizer_task.get("action", "synthesize_and_report"),
            "task_status": {
                "numerology_completed": any(t.get("agent") == "NumerologyAgent" and t.get("status") == "completed" for t in tasks),
                "trading_completed": any(t.get("agent") == "TradingAgent" and t.get("status") == "completed" for t in tasks)
            }
        }
        
        result = agent.invoke(input_data)
        
        # Cập nhật task status thành "completed" và lưu kết quả
        synthesizer_task["status"] = "completed"
        synthesizer_task["result"] = result
        
        return {"final_answer": result}
        
    except Exception as e:
        # Cập nhật task status thành "failed"
        synthesizer_task["status"] = "failed"
        synthesizer_task["error"] = str(e)
        
        return {
            "error": f"SynthesizerAgent failed: {str(e)}"
        }


def final_node(state: AgentState) -> AgentState:
    """Trả về câu trả lời cuối cùng với LLM reasoning"""
    # Nếu đã có final_answer từ synthesizer, không cần làm gì thêm
    if state.get("final_answer"):
        return {}
    
    # Nếu không có final_answer, sử dụng LLM để tạo từ tool_output
    tool_output = state.get("tool_output", {})
    if tool_output:
        try:
            # Sử dụng LLM để tạo final answer thông minh
            final_answer = create_intelligent_final_answer(
                state["question"], 
                tool_output, 
                state.get("enrichment", {})
            )
            return {"final_answer": final_answer}
        except Exception:
            # Fallback
            if "numerology" in tool_output:
                final_answer = tool_output["numerology"]
            elif "trading" in tool_output:
                final_answer = tool_output["trading"]
            else:
                final_answer = "Không thể xử lý câu hỏi này."
            
            return {"final_answer": final_answer}
    
    # Fallback
    return {"final_answer": "Không thể xử lý câu hỏi này."}


def create_intelligent_final_answer(question: str, tool_output: Dict, enrichment: Dict) -> str:
    """Sử dụng LLM để tạo final answer thông minh"""
    system_prompt = """Bạn là FinalAnswerGenerator.

## Nhiệm vụ:
Tạo câu trả lời cuối cùng thông minh dựa trên:
- Câu hỏi gốc của người dùng
- Kết quả từ các agent chuyên biệt
- Context enrichment

## Quy tắc:
1. Tổng hợp thông tin một cách logic
2. Đảm bảo trả lời đúng trọng tâm câu hỏi
3. Sử dụng ngôn ngữ tự nhiên và dễ hiểu
4. Thêm insights nếu có thể

## Output:
Trả về câu trả lời hoàn chỉnh bằng tiếng Việt."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Câu hỏi: {question}
Kết quả numerology: {numerology}
Kết quả trading: {trading}
Enrichment: {enrichment}

Tạo câu trả lời cuối cùng:""")
    ])

    chain = prompt | get_openai_llm() | StrOutputParser()
    
    result = chain.invoke({
        "question": question,
        "numerology": tool_output.get("numerology", ""),
        "trading": tool_output.get("trading", ""),
        "enrichment": json.dumps(enrichment, ensure_ascii=False)
    })
    
    return result


def should_continue(state: AgentState) -> str:
    """Quyết định agent tiếp theo cần chạy dựa trên LLM reasoning"""
    # Kiểm tra xem có routing_decision từ smart_route_node không
    routing_decision = state.get("routing_decision")
    if routing_decision and routing_decision.get("next_node"):
        return routing_decision["next_node"]
    
    # Fallback to traditional logic nếu không có smart routing
    plan = state.get("plan", {})
    tasks = plan.get("tasks", [])
    
    if not tasks:
        return "final_node"
    
    # Tìm task đầu tiên có status "pending"
    for task in tasks:
        if task.get("status") == "pending":
            agent = task.get("agent")
            if agent == "NumerologyAgent":
                return "numerology_node"
            elif agent == "TradingAgent":
                return "trading_node"
            elif agent == "SynthesizerAgent":
                return "synthesizer_node"
            else:
                return "final_node"
    
    # Tất cả tasks đã hoàn thành hoặc không có task pending
    return "final_node"


def build_graph():
    """Tạo LangGraph workflow với LLM reasoning"""
    
    # Tạo graph
    graph = StateGraph(AgentState)
    
    # Thêm nodes
    graph.add_node("initial_node", initial_node)
    graph.add_node("enricher_node", enricher_node)
    graph.add_node("router_node", router_node)
    graph.add_node("smart_route_node", smart_route_node)  # Node mới
    graph.add_node("numerology_node", numerology_node)
    graph.add_node("trading_node", trading_node)
    graph.add_node("synthesizer_node", synthesizer_node)
    graph.add_node("final_node", final_node)
    
    # Set entry point
    try:
        graph.set_entry_point("initial_node")
    except Exception:
        pass
    
    # Thêm edges
    graph.add_edge(START, "initial_node")
    
    # Backward compatibility edges
    try:
        graph.add_edge("__start__", "initial_node")
    except Exception:
        pass
    
    graph.add_edge("initial_node", "enricher_node")
    graph.add_edge("enricher_node", "router_node")
    graph.add_edge("router_node", "smart_route_node")  # Thêm smart routing
    
    # Conditional edges từ smart_route_node
    graph.add_conditional_edges(
        "smart_route_node",
        should_continue,
        {
            "numerology_node": "numerology_node",
            "trading_node": "trading_node",
            "synthesizer_node": "synthesizer_node",
            "final_node": "final_node"
        }
    )
    
    # Conditional edges từ các agent nodes
    graph.add_conditional_edges(
        "numerology_node",
        should_continue,
        {
            "trading_node": "trading_node",
            "synthesizer_node": "synthesizer_node",
            "final_node": "final_node"
        }
    )
    
    graph.add_conditional_edges(
        "trading_node",
        should_continue,
        {
            "numerology_node": "numerology_node",
            "synthesizer_node": "synthesizer_node",
            "final_node": "final_node"
        }
    )
    
    # Edges cuối
    graph.add_edge("synthesizer_node", "final_node")
    graph.add_edge("final_node", END)
    
    return graph.compile()


