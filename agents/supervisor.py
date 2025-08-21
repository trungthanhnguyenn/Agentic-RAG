import json
import re
from pathlib import Path
from typing import Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import get_openai_llm


def _read_agents_guide() -> str:
    """Đọc file AGENTS.md để làm context cho LLM"""
    base_dir = Path(__file__).resolve().parents[1]
    guide_path = base_dir / "AGENTS.md"
    if guide_path.exists():
        content = guide_path.read_text(encoding="utf-8")
        # Escape curly braces in JSON examples to prevent template variable conflicts
        content = content.replace("{", "{{").replace("}", "}}")
        return content
    return ""


def _heuristic_route_plan(question: str) -> Dict:
    """Heuristic fallback khi LLM routing thất bại"""
    question_lower = question.lower()
    
    # Xác định nhu cầu dựa trên từ khóa
    has_numerology = any(word in question_lower for word in [
        "thần số", "ngày sinh", "tính cách", "đường đời", "sứ mệnh", 
        "linh hồn", "nhân cách", "cân bằng", "trưởng thành", "giai đoạn"
    ])
    
    has_trading = any(word in question_lower for word in [
        "giao dịch", "trading", "hiệu suất", "lợi nhuận", "thua lỗ", 
        "win rate", "drawdown", "rủi ro", "excel", "dữ liệu"
    ])
    
    needs_combo = any(word in question_lower for word in [
        "phù hợp", "kết hợp", "liên hệ", "tư vấn", "toàn diện", 
        "cá nhân", "khuyến nghị", "nên", "có nên"
    ])
    
    # Tạo kế hoạch dựa trên cấu trúc mới
    if has_numerology and not has_trading:
        return {
            "description": "Phân tích thần số học",
            "kind": "single",
            "tasks": [
                {
                    "step": 1,
                    "agent": "NumerologyAgent",
                    "action": "calculate_and_interpret",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path"
                    },
                    "output_key": "tool_output_numerology",
                    "status": "pending"
                }
            ]
        }
    elif has_trading and not has_numerology:
        return {
            "description": "Phân tích dữ liệu giao dịch",
            "kind": "single",
            "tasks": [
                {
                    "step": 1,
                    "agent": "TradingAgent",
                    "action": "analyze_performance",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path"
                    },
                    "output_key": "tool_output_trading",
                    "status": "pending"
                }
            ]
        }
    elif needs_combo or (has_numerology and has_trading):
        return {
            "description": "Tư vấn toàn diện kết hợp thần số và giao dịch",
            "kind": "combo",
            "tasks": [
                {
                    "step": 1,
                    "agent": "NumerologyAgent",
                    "action": "calculate_and_interpret",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path"
                    },
                    "output_key": "tool_output_numerology",
                    "status": "pending"
                },
                {
                    "step": 2,
                    "agent": "TradingAgent",
                    "action": "analyze_performance",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path",
                        "numerology_output": "ref:state.tool_output_numerology"
                    },
                    "output_key": "tool_output_trading",
                    "status": "pending"
                },
                {
                    "step": 3,
                    "agent": "SynthesizerAgent",
                    "action": "synthesize_and_report",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path",
                        "numerology_output": "ref:state.tool_output_numerology",
                        "trading_output": "ref:state.tool_output_trading"
                    },
                    "output_key": "final_answer",
                    "status": "pending"
                }
            ]
        }
    else:
        # Default fallback - combo approach
        return {
            "description": "Tư vấn toàn diện kết hợp thần số và giao dịch",
            "kind": "combo",
            "tasks": [
                {
                    "step": 1,
                    "agent": "NumerologyAgent",
                    "action": "calculate_and_interpret",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path"
                    },
                    "output_key": "tool_output_numerology",
                    "status": "pending"
                },
                {
                    "step": 2,
                    "agent": "TradingAgent",
                    "action": "analyze_performance",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path",
                        "numerology_output": "ref:state.tool_output_numerology"
                    },
                    "output_key": "tool_output_trading",
                    "status": "pending"
                },
                {
                    "step": 3,
                    "agent": "SynthesizerAgent",
                    "action": "synthesize_and_report",
                    "input": {
                        "question": "ref:state.question",
                        "user_name": "ref:state.user_info.name",
                        "dob": "ref:state.user_info.dob",
                        "excel_path": "ref:state.user_info.excel_path",
                        "numerology_output": "ref:state.tool_output_numerology",
                        "trading_output": "ref:state.tool_output_trading"
                    },
                    "output_key": "final_answer",
                    "status": "pending"
                }
            ]
        }


def _test_llm_response(raw: str) -> bool:
    """Test xem LLM response có phải là JSON hợp lệ không"""
    if not raw or raw.strip() == "":
        return False
    
    # Kiểm tra có dấu ngoặc nhọn không
    if "{" not in raw or "}" not in raw:
        return False
    
    # Thử parse JSON
    try:
        json.loads(raw.strip())
        return True
    except json.JSONDecodeError:
        return False


def _extract_json_from_response(raw: str) -> str | None:
    """Extract JSON từ response có thể chứa markdown hoặc text khác"""
    if not raw or raw.strip() == "":
        return None
    
    # Loại bỏ whitespace đầu cuối
    raw = raw.strip()
    
    # Thử parse trực tiếp trước
    try:
        json.loads(raw)
        return raw
    except json.JSONDecodeError:
        pass
    
    # Tìm JSON object trong response
    # Pattern 1: ```json ... ```
    json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if json_block_match:
        try:
            json_str = json_block_match.group(1).strip()
            json.loads(json_str)  # Validate
            return json_str
        except (json.JSONDecodeError, IndexError):
            pass
    
    # Pattern 2: Tìm JSON object đơn giản
    json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', raw, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(1).strip()
            json.loads(json_str)  # Validate
            return json_str
        except (json.JSONDecodeError, IndexError):
            pass
    
    # Pattern 3: Tìm bất kỳ chuỗi bắt đầu bằng dấu ngoặc nhọn và kết thúc bằng dấu ngoặc nhọn
    brace_match = re.search(r'(\{.*\})', raw, re.DOTALL)
    if brace_match:
        try:
            json_str = brace_match.group(1).strip()
            json.loads(json_str)  # Validate
            return json_str
        except (json.JSONDecodeError, IndexError):
            pass
    
    return None


def build_supervisor_router() -> "RunnableSerializable":
    """Tạo LLM chain cho supervisor routing"""
    
    system_prompt = """Bạn là SupervisorAgent trong hệ thống tư vấn đầu tư và thần số học.

## Nhiệm vụ chính:
Lập kế hoạch định tuyến dựa trên câu hỏi và ngữ cảnh để quyết định kế hoạch xử lý câu hỏi.

## Vai trò trong hệ thống:
- Là agent quyết định kế hoạch xử lý câu hỏi
- Tạo ra kế hoạch chi tiết dưới dạng các task tuần tự
- Xác định agent nào cần được kích hoạt và theo thứ tự nào
- Đảm bảo tính nhất quán và hiệu quả trong quy trình xử lý

## Các agent chuyên biệt trong hệ thống:
- **NumerologyAgent**: Phân tích thần số học, tính toán chỉ số cá nhân, truy xuất diễn giải từ cơ sở tri thức
- **TradingAgent**: Phân tích dữ liệu giao dịch, đánh giá hiệu suất, rủi ro, và hành vi giao dịch
- **SynthesizerAgent**: Tổng hợp thông tin từ cả hai agent, phân tích chéo, tạo insights nâng cao

## Cấu trúc kế hoạch:
Bạn phải trả về một đối tượng JSON duy nhất có cấu trúc sau:

```json
{{
  "description": "Mô tả tóm tắt kế hoạch của LLM",
  "kind": "simple|single|combo",
  "tasks": [
    {{
      "step": "số thứ tự của task, bắt đầu từ 1",
      "agent": "Tên agent (NumerologyAgent|TradingAgent|SynthesizerAgent)",
      "action": "Hành động cụ thể (calculate_and_interpret|analyze_performance|synthesize_and_report)",
      "input": {{
        "question": "ref:state.question",
        "user_name": "ref:state.user_info.name",
        "dob": "ref:state.user_info.dob",
        "excel_path": "ref:state.user_info.excel_path",
        "numerology_output": "ref:state.tool_output_numerology",
        "trading_output": "ref:state.tool_output_trading"
      }},
      "output_key": "Tên key trong state để lưu kết quả (tool_output_numerology|tool_output_trading|final_answer)",
      "status": "pending"
    }}
  ]
}}
```

## Quy tắc lập kế hoạch:

### 1. **Kind determination**:
- **simple**: Câu hỏi đơn giản, có thể trả lời ngay
- **single**: Chỉ cần một loại phân tích (numerology hoặc trading)
- **combo**: Cần cả hai loại phân tích và synthesis

### 2. **Task sequencing**:
- **Step 1**: NumerologyAgent (nếu cần thần số học)
- **Step 2**: TradingAgent (nếu cần phân tích giao dịch)
- **Step 3**: SynthesizerAgent (nếu cần tổng hợp)

### 3. **Input mapping**:
- Sử dụng cú pháp "ref:state.<tên trường>" để tham chiếu dữ liệu từ state
- Đảm bảo mỗi agent nhận được input cần thiết
- Truyền output từ agent trước cho agent sau khi cần thiết

### 4. **Output key assignment**:
- `tool_output_numerology`: Kết quả từ NumerologyAgent
- `tool_output_trading`: Kết quả từ TradingAgent
- `final_answer`: Kết quả cuối cùng từ SynthesizerAgent

### 5. **Status management**:
- Luôn khởi tạo status là "pending" khi kế hoạch được tạo
- Router Agent sẽ cập nhật status thành "running", "completed", hoặc "failed"

## Quy tắc ưu tiên:

### **Ưu tiên combo khi**:
- Mục tiêu là tư vấn toàn diện và cá nhân hóa
- Câu hỏi về "phù hợp", "kết hợp", "liên hệ" giữa tính cách và trading
- Cần đưa ra khuyến nghị dựa trên cả hai nguồn dữ liệu
- Thiếu thông tin rõ ràng về loại phân tích cần thiết
- enrichment.recommended_approach = "combo"

### **Sử dụng single khi**:
- Câu hỏi chỉ tập trung vào một lĩnh vực cụ thể
- Người dùng chỉ cần thông tin từ một nguồn
- Thời gian và tài nguyên hạn chế

## Xử lý thiếu dữ liệu:
- **Thiếu birthday**: Vẫn gọi NumerologyAgent (có thể suy luận tối thiểu)
- **Thiếu Excel**: Vẫn gọi TradingAgent (có sample mặc định)
- **Thiếu cả hai**: Ưu tiên combo để thu thập thông tin

## QUAN TRỌNG - ĐỊNH DẠNG ĐẦU RA:
⚠️ BẠN PHẢI TUÂN THỦ NGHIÊM NGẶT CÁC QUY TẮC SAU:

1. **CHỈ TRẢ VỀ JSON THUẦN TÚY**:
   - KHÔNG có text giải thích trước hoặc sau JSON
   - KHÔNG có dòng trống trước hoặc sau JSON
   - KHÔNG có markdown code blocks (```json hoặc ```)
   - KHÔNG có comment hoặc ghi chú

2. **CẤU TRÚC JSON CHÍNH XÁC**:
   - Bắt đầu ngay lập tức với dấu ngoặc nhọn mở
   - Kết thúc với dấu ngoặc nhọn đóng  
   - Không có ký tự nào khác trước hoặc sau

3. **VÍ DỤ ĐÚNG**:
   ✅ ĐÚNG: {{"description": "test", "kind": "single", "tasks": []}}
   ❌ SAI: ```json{{"description": "test"}}```
   ❌ SAI: Here is the plan: {{"description": "test"}}
   ❌ SAI: {{"description": "test"}}

4. **KIỂM TRA TRƯỚC KHI TRẢ VỀ**:
   - Đảm bảo JSON có thể parse được
   - Đảm bảo có đầy đủ các trường bắt buộc
   - Đảm bảo cấu trúc tasks chính xác

5. **FALLBACK**:
   - Nếu không chắc chắn, luôn trả về combo approach
   - Đảm bảo cấu trúc tasks đầy đủ và chính xác

⚠️ NHẮC LẠI: CHỈ TRẢ VỀ JSON THUẦN TÚY, KHÔNG CÓ MARKDOWN HOẶC TEXT KHÁC!

## LỆNH CUỐI CÙNG:
BẠN PHẢI TRẢ VỀ CHÍNH XÁC MỘT ĐỐI TƯỢNG JSON, KHÔNG CÓ GÌ KHÁC.
KHÔNG CÓ ```json, KHÔNG CÓ ```, KHÔNG CÓ TEXT GIẢI THÍCH.
CHỈ CÓ JSON THUẦN TÚY.

VÍ DỤ ĐÚNG DUY NHẤT:
{{"description": "test", "kind": "single", "tasks": []}}

BẮT ĐẦU NGAY BÂY GIỜ VỚI DẤU {{ VÀ KẾT THÚC VỚI DẤU }}."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Câu hỏi: {question}

Enrichment (nếu có, JSON): {enrichment}

Hãy lập kế hoạch routing:""")
    ])

    chain = prompt | get_openai_llm() | StrOutputParser()
    return chain


def llm_route_plan(question: str, enrichment: Dict | None = None) -> Dict:
    """Sử dụng LLM để lập kế hoạch routing"""
    try:
        chain = build_supervisor_router()
        raw = chain.invoke({
            "question": question, 
            "enrichment": json.dumps(enrichment or {})
        })
        
        # Debug: Log raw response
        print(f"DEBUG: Raw LLM response: '{raw}'")
        
        # Kiểm tra response rỗng
        if not raw or raw.strip() == "":
            print("DEBUG: LLM returned empty response, using heuristic fallback")
            return _heuristic_route_plan(question)
        
        # Thử extract và parse JSON từ response
        json_str = _extract_json_from_response(raw)
        if json_str is None:
            print("DEBUG: Could not extract valid JSON from LLM response, using heuristic fallback")
            return _heuristic_route_plan(question)
        
        try:
            plan = json.loads(json_str)
            print(f"DEBUG: Successfully parsed JSON plan: {plan}")
            
            # Validate plan structure mới
            required_keys = ["description", "kind", "tasks"]
            if all(key in plan for key in required_keys):
                # Validate tasks structure
                if isinstance(plan["tasks"], list) and len(plan["tasks"]) > 0:
                    for task in plan["tasks"]:
                        task_required_keys = ["step", "agent", "action", "input", "output_key", "status"]
                        if not all(key in task for key in task_required_keys):
                            print("DEBUG: Task missing required keys, using heuristic fallback")
                            return _heuristic_route_plan(question)
                    
                    # Force status to pending for all tasks
                    for task in plan["tasks"]:
                        task["status"] = "pending"
                    
                    return plan
                else:
                    print("DEBUG: Plan tasks is not a valid list, using heuristic fallback")
                    return _heuristic_route_plan(question)
            else:
                print("DEBUG: Plan missing required keys, using heuristic fallback")
                return _heuristic_route_plan(question)
                
        except json.JSONDecodeError as json_err:
            print(f"DEBUG: JSON parsing failed: {json_err}")
            print(f"DEBUG: Raw content that failed to parse: '{raw}'")
            print(f"DEBUG: Extracted JSON string: '{json_str}'")
            return _heuristic_route_plan(question)
            
    except Exception as e:
        print(f"LLM routing failed: {e}")
        print(f"DEBUG: Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return _heuristic_route_plan(question)


def smart_route_plan(text: str, enrichment: Dict | None = None) -> Dict:
    """Smart routing với LLM và fallback heuristic"""
    
    # Thử LLM trước
    try:
        plan = llm_route_plan(text, enrichment)
        
        # Validate plan structure mới
        required_keys = ["description", "kind", "tasks"]
        if all(key in plan for key in required_keys):
            # Validate tasks structure
            if isinstance(plan["tasks"], list) and len(plan["tasks"]) > 0:
                for task in plan["tasks"]:
                    task_required_keys = ["step", "agent", "action", "input", "output_key", "status"]
                    if not all(key in task for key in task_required_keys):
                        print("DEBUG: Smart routing validation failed, using heuristic")
                        return _heuristic_route_plan(text)
                
                return plan
    except Exception as e:
        print(f"Smart routing failed, using heuristic: {e}")
    
    # Fallback về heuristic
    return _heuristic_route_plan(text)


def route_plan(text: str, enrichment: Dict | None = None) -> Dict:
    """Main routing function - alias cho smart_route_plan"""
    return smart_route_plan(text, enrichment)

