from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.trading_tool import (
    calculate_trade_index,
    print_trade_report,
    read_trading_excel,
    analyze_user_question,
    generate_focused_report,
    get_trading_data_from_excel,
)
from tools.data_validator_tool import DataValidator

from app.config import get_openai_llm


def _read_prompt() -> str:
    base_dir = Path(__file__).resolve().parents[1]
    prompt_path = base_dir / "prompts" / "trading_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def _prepare_trading_data(input_dict: dict) -> dict:
    """
    Prepare trading data for analysis based on user input.
    
    Args:
        input_dict: Dictionary containing question and optional excel_path
        
    Returns:
        Dictionary with prepared data for the agent
    """
    question = input_dict.get("question", "")
    excel_path = input_dict.get("excel_path") or input_dict.get("file_path")  # Support both keys
    
    try:
        # Validate profile lightly if provided
        validator = DataValidator()
        if input_dict.get("profile"):
            prof = input_dict["profile"]
            validator.validate_profile(prof.get("user_name"), prof.get("birthday"))

        # Get trading data from Excel file
        df = get_trading_data_from_excel(excel_path)

        # Validate dataframe shape quickly
        validation = validator.validate_excel_dataframe(df)
        if not validation["is_valid"]:
            return {
                "question": question,
                "error": "invalid_trading_data",
                "issues": validation["issues"],
                "suggestions": validation["suggestions"],
                "success": False,
            }
        
        # Analyze what the user wants to know
        analysis_needs = analyze_user_question(question)
        
        # Calculate comprehensive trading metrics
        trading_result = calculate_trade_index(df)
        
        # Generate focused report based on user needs
        focused_report = generate_focused_report(trading_result, analysis_needs)
        
        # Create a comprehensive summary for the agent (structured JSON)
        data_summary = {
            "total_trades": trading_result["trades"],
            "total_profit": trading_result["net_profit"],
            "win_rate": trading_result["win_rate_pct"],
            "avg_profit_per_trade": trading_result["avg_profit_per_trade"],
            "profit_factor": trading_result["profit_factor"],
            "max_drawdown": trading_result["max_drawdown_pct"],
            "max_consecutive_losses": trading_result["max_consecutive_losses"],
            "best_trade": trading_result["best_trade"],
            "worst_trade": trading_result["worst_trade"],
            "available_columns": list(df.columns) if hasattr(df.columns, '__iter__') else [],
            "symbols_traded": list(df['symbol'].unique()) if 'symbol' in df.columns else [],
            "time_range": {
                "earliest": df['close_time'].min() if 'close_time' in df.columns else None,
                "latest": df['close_time'].max() if 'close_time' in df.columns else None
            } if 'close_time' in df.columns else None
        }
        
        # Flatten the data structure for the prompt template
        prompt_data = {
            "question": question,
            "total_trades": data_summary["total_trades"],
            "total_profit": data_summary["total_profit"],
            "win_rate": data_summary["win_rate"],
            "avg_profit_per_trade": data_summary["avg_profit_per_trade"],
            "profit_factor": data_summary["profit_factor"],
            "max_drawdown": data_summary["max_drawdown"],
            "max_consecutive_losses": data_summary["max_consecutive_losses"],
            "focused_report": focused_report,
            "trading_data": trading_result,  # structured JSON payload
            "analysis_needs": analysis_needs,
            "data_summary": data_summary,
            "success": True
        }
        
        return prompt_data
        
    except Exception as e:
        return {
            "question": question,
            "error": str(e),
            "error_type": "data_processing_error",
            "success": False
        }


def build_trading_agent():
    """
    Build a trading agent that can intelligently analyze trading data.
    
    The agent will:
    1. Read Excel files with trading history
    2. Analyze user questions to determine what they want to know
    3. Generate focused reports based on user needs
    4. Handle errors gracefully and explain limitations
    """
    
    # Create a prompt that guides the agent to use the prepared data intelligently
    prompt = ChatPromptTemplate.from_messages([
        ("system", _read_prompt()),
        ("human", """
Câu hỏi: {question}

Dữ liệu giao dịch đã được phân tích và chuẩn bị sẵn:

📊 TÓM TẮT DỮ LIỆU:
- Tổng số lệnh: {total_trades}
- Tổng lợi nhuận: {total_profit:,.2f}
- Tỷ lệ thắng: {win_rate}%
- Lợi nhuận trung bình/lệnh: {avg_profit_per_trade:,.2f}
- Hệ số lợi nhuận: {profit_factor}
- Sụt giảm tối đa: {max_drawdown}%
- Số lệnh thua liên tiếp tối đa: {max_consecutive_losses}

📈 BÁO CÁO TẬP TRUNG:
{focused_report}

💡 HƯỚNG DẪN:
1. Sử dụng số liệu cụ thể từ dữ liệu trên để trả lời
2. Trả lời ngắn gọn, súc tích, tập trung vào câu hỏi của user
3. Luôn đưa ra khuyến nghị thực tiễn dựa trên phân tích
4. Nếu có lỗi: giải thích rõ ràng và đưa ra gợi ý khắc phục
5. Nếu câu hỏi ngoài phạm vi: xin lỗi và giải thích giới hạn

Hãy trả lời bằng tiếng Việt, sử dụng dữ liệu cụ thể đã có sẵn.
        """),
    ])
    
    llm = get_openai_llm()
    
    # Create a chain that prepares data first, then processes with LLM
    from langchain_core.runnables import RunnableLambda
    
    prepare_data = RunnableLambda(_prepare_trading_data)
    
    chain = (
        prepare_data | 
        prompt | 
        llm | 
        StrOutputParser()
    )
    
    return chain


def build_simple_trading_agent():
    """
    Build a simpler trading agent for basic queries.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", _read_prompt()),
        ("human", "Câu hỏi: {question}\n\nDữ liệu giao dịch: {data}"),
    ])
    
    llm = get_openai_llm()
    return prompt | llm | StrOutputParser()


