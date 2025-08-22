class TimePrompt:
    """
    Prompt template class for time-related queries
    Provides structured prompts for LLM to understand and process time requests
    """
    
    @staticmethod
    def get_time_query_prompt():
        """
        Returns the main prompt template for time queries
        Instructs LLM to analyze time-related text and extract relevant information
        """
        return """
        Bạn là một chuyên gia về xử lý thời gian và ngày tháng.
        
        Nhiệm vụ của bạn là phân tích câu hỏi về thời gian và trả về thông tin chính xác.
        
        Hãy xác định:
        1. Thời gian được đề cập trong câu hỏi (ngày mai, 3 ngày nữa, hôm nay, v.v.)
        2. Loại hành động hoặc sự kiện cần thực hiện
        3. Tính toán ngày tháng cụ thể dựa trên thời gian hiện tại
        
        Trả về kết quả dưới dạng JSON với format:
        {
            "time_reference": "thời gian được đề cập",
            "action": "hành động cần thực hiện",
            "calculated_date": "ngày tháng được tính toán",
            "days_from_now": "số ngày từ hôm nay",
            "weekday": "thứ trong tuần"
        }
        
        Câu hỏi: {user_query}
        """
    
    @staticmethod
    def get_system_prompt():
        """
        Returns system prompt for function calling setup
        Defines the role and capabilities of the LLM
        """
        return """
        Bạn là trợ lý AI chuyên về xử lý thời gian và lập kế hoạch.
        Bạn có khả năng hiểu và phân tích các yêu cầu về thời gian một cách chính xác.
        Luôn trả về kết quả dưới dạng JSON có cấu trúc rõ ràng.
        """