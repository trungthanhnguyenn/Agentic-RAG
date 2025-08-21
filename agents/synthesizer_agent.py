from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import get_openai_llm
from tools.context_validator_tool import ContextValidator
from tools.pattern_analyzer_tool import PatternAnalyzer


def _read_prompt() -> str:
    base_dir = Path(__file__).resolve().parents[1]
    prompt_path = base_dir / "prompts" / "synthesizer_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def _enhance_with_advanced_analysis(numerology_data: str, trading_data: str, question: str) -> dict:
    """
    Enhance the synthesis with advanced analysis using the new tools.
    
    Args:
        numerology_data: Numerology analysis results
        trading_data: Trading analysis results
        question: User's original question
        
    Returns:
        Dictionary with enhanced analysis
    """
    enhanced_data = {
        "numerology": numerology_data,
        "trading": trading_data,
        "question": question,
        "context_validation": None,
        "pattern_analysis": None,
        "enhanced_insights": []
    }
    
    try:
        # Initialize tools
        context_validator = ContextValidator()
        pattern_analyzer = PatternAnalyzer()
        
        # Extract structured data from responses (simplified parsing)
        # In a real implementation, you'd have structured data from the agents
        numerology_parsed = _parse_numerology_response(numerology_data)
        trading_parsed = _parse_trading_response(trading_data)
        
        if numerology_parsed and trading_parsed:
            # Perform context validation
            validation_results = context_validator.validate_consistency(
                numerology_parsed, trading_parsed
            )
            enhanced_data["context_validation"] = validation_results
            
            # Generate and test hypotheses
            hypotheses = pattern_analyzer.generate_hypotheses(
                numerology_parsed, trading_parsed
            )
            tested_hypotheses = pattern_analyzer.test_hypotheses(
                hypotheses, trading_parsed
            )
            insights = pattern_analyzer.generate_insights(tested_hypotheses)
            enhanced_data["pattern_analysis"] = {
                "hypotheses": tested_hypotheses,
                "insights": insights
            }
            
            # Generate enhanced insights
            enhanced_data["enhanced_insights"] = _generate_enhanced_insights(
                validation_results, insights, numerology_parsed, trading_parsed
            )
    
    except Exception as e:
        print(f"Warning: Advanced analysis failed: {e}")
        enhanced_data["enhanced_insights"] = ["Advanced analysis temporarily unavailable"]
    
    return enhanced_data


def _parse_numerology_response(response: str | dict) -> dict:
    """Prefer structured dict; fallback to legacy regex if needed."""
    if isinstance(response, dict):
        return response
    # Keep minimal fallback; encourage structured outputs from numerology agent
    return {}


def _parse_trading_response(response: str | dict) -> dict:
    """Prefer structured dict produced by trading agent; fallback empty."""
    if isinstance(response, dict):
        return response
    return {}


def _generate_enhanced_insights(validation_results: dict, pattern_insights: list, 
                               numerology_data: dict, trading_data: dict) -> list:
    """Generate enhanced insights combining all analysis."""
    insights = []
    
    # Add context validation insights
    if validation_results and not validation_results.get("is_consistent", True):
        insights.append("⚠️ **PHÁT HIỆN SỰ KHÔNG NHẤT QUÁN:**")
        for inconsistency in validation_results.get("inconsistencies", []):
            insights.append(f"• {inconsistency['description']}")
        
        if validation_results.get("recommendations"):
            insights.append("\n**KHUYẾN NGHỊ CÂN BẰNG:**")
            for rec in validation_results["recommendations"]:
                insights.append(f"• {rec}")
    
    # Add pattern analysis insights
    if pattern_insights:
        insights.append("\n🔍 **PHÂN TÍCH MÔ HÌNH:**")
        for insight in pattern_insights:
            insights.append(f"• **{insight['title']}** (Độ tin cậy: {insight['confidence']:.1%})")
            insights.append(f"  {insight['description']}")
            for rec in insight.get('recommendations', []):
                insights.append(f"    - {rec}")
    
    # Add cross-analysis insights
    cross_insights = _generate_cross_analysis_insights(numerology_data, trading_data)
    if cross_insights:
        insights.append("\n🔗 **PHÂN TÍCH LIÊN KẾT:**")
        insights.extend(cross_insights)
    
    return insights


def _generate_cross_analysis_insights(numerology_data: dict, trading_data: dict) -> list:
    """Generate insights by cross-analyzing numerology and trading data."""
    insights = []
    
    # Life path vs trading performance
    if "life_path" in numerology_data:
        life_path = numerology_data["life_path"]
        
        # Analyze based on life path characteristics
        if life_path in [1, 5, 8]:  # High risk tolerance
            if trading_data.get("max_drawdown_pct", 0) < 10:
                insights.append("• Chỉ số đường đời của bạn cho thấy khả năng chấp nhận rủi ro cao, nhưng bạn đang giao dịch quá cẩn trọng. Có thể bạn đang bỏ lỡ cơ hội.")
            elif trading_data.get("max_drawdown_pct", 0) > 25:
                insights.append("• Chỉ số đường đời của bạn cho phép chấp nhận rủi ro cao, nhưng hãy đảm bảo rủi ro có kiểm soát và có kế hoạch phục hồi.")
        
        elif life_path in [2, 4, 6]:  # Low risk tolerance
            if trading_data.get("max_drawdown_pct", 0) > 15:
                insights.append("• Chỉ số đường đời của bạn cho thấy bạn nên giao dịch cẩn trọng. Hãy giảm khối lượng giao dịch để phù hợp với bản chất.")
            else:
                insights.append("• Chỉ số đường đời và phong cách giao dịch của bạn hoàn toàn phù hợp. Hãy tiếp tục duy trì sự cẩn trọng này.")
    
    # Personal day vs trading timing
    if "personal_day" in numerology_data:
        personal_day = numerology_data["personal_day"]
        
        # Personal day 1-3: Good for new trades
        if personal_day in [1, 2, 3]:
            insights.append("• Ngày cá nhân của bạn thuận lợi cho việc mở lệnh mới. Hãy tận dụng cơ hội này.")
        # Personal day 4-6: Good for management
        elif personal_day in [4, 5, 6]:
            insights.append("• Ngày cá nhân của bạn thuận lợi cho việc quản lý lệnh hiện có. Hãy tập trung vào việc điều chỉnh stop loss và take profit.")
        # Personal day 7-9: Good for analysis
        elif personal_day in [7, 8, 9]:
            insights.append("• Ngày cá nhân của bạn thuận lợi cho việc phân tích và lập kế hoạch. Hãy dành thời gian nghiên cứu thị trường.")
    
    # Balance vs emotional control
    if "balance" in numerology_data:
        balance = numerology_data["balance"]
        consecutive_losses = trading_data.get("max_consecutive_losses", 0)
        
        if balance <= 4 and consecutive_losses > 3:
            insights.append("• Chỉ số cân bằng của bạn cho thấy khả năng kiểm soát cảm xúc tốt, nhưng thực tế giao dịch lại cho thấy kiểm soát cảm xúc kém. Hãy rèn luyện khả năng này.")
        elif balance >= 7 and consecutive_losses <= 2:
            insights.append("• Chỉ số cân bằng của bạn cho thấy khả năng kiểm soát cảm xúc cần cải thiện, nhưng thực tế giao dịch lại rất tốt. Bạn đã vượt qua được thách thức này.")
    
    return insights


def build_synthesizer_agent():
    """Build an enhanced synthesizer agent with advanced analysis capabilities."""
    
    # Create the enhanced data preparation function
    def prepare_enhanced_data(input_dict: dict) -> dict:
        """Prepare enhanced data with advanced analysis."""
        numerology = input_dict.get("numerology", "")
        trading = input_dict.get("trading", "")
        question = input_dict.get("question", "")
        
        # Perform advanced analysis
        enhanced_data = _enhance_with_advanced_analysis(numerology, trading, question)
        
        # Format the enhanced insights for the prompt
        enhanced_insights_text = "\n".join(enhanced_data["enhanced_insights"]) if enhanced_data["enhanced_insights"] else "Không có insights nâng cao."
        
        return {
            "numerology": numerology,
            "trading": trading,
            "question": question,
            "enhanced_insights": enhanced_insights_text,
            "context_validation": enhanced_data.get("context_validation"),
            "pattern_analysis": enhanced_data.get("pattern_analysis")
        }
    
    # Create the enhanced prompt
    enhanced_prompt = ChatPromptTemplate.from_messages([
        ("system", _read_prompt()),
        ("human", """
Câu hỏi: {question}

=== PHÂN TÍCH THẦN SỐ HỌC ===
{numerology}

=== PHÂN TÍCH GIAO DỊCH ===
{trading}

=== INSIGHTS NÂNG CAO ===
{enhanced_insights}

Hãy tổng hợp tất cả thông tin trên để tạo ra câu trả lời cuối cùng, ưu tiên:
1. Sử dụng insights nâng cao để đưa ra lời khuyên cụ thể
2. Kết hợp thông tin từ cả hai nguồn một cách logic
3. Đưa ra khuyến nghị thực tiễn dựa trên phân tích toàn diện
4. Trả lời bằng tiếng Việt, súc tích và hữu ích
        """),
    ])
    
    llm = get_openai_llm()
    
    # Create the enhanced chain
    from langchain_core.runnables import RunnableLambda
    
    prepare_data = RunnableLambda(prepare_enhanced_data)
    
    chain = (
        prepare_data | 
        enhanced_prompt | 
        llm | 
        StrOutputParser()
    )
    
    return chain


