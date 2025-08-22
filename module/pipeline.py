import json
# Optional imports - will fallback to local calculation if not available
try:
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from .client import LangChainClient
    CLIENT_AVAILABLE = True
except ImportError:
    CLIENT_AVAILABLE = False

from .prompt import TimePrompt
from .time_tools import TimeCalculator

class TimeProcessingPipeline:
    """
    Main pipeline class for processing time-related queries
    Orchestrates the workflow from input to JSON output
    """
    
    def __init__(self):
        """Initialize pipeline components"""
        self.use_llm = False
        self.client = None
        
        # Only try LLM if dependencies are available
        if LANGCHAIN_AVAILABLE and CLIENT_AVAILABLE:
            try:
                self.client = LangChainClient().get_client()
                self.use_llm = True
            except Exception:
                self.use_llm = False
                print("Warning: LLM client not available, using local time calculation only")
        else:
            print("Warning: LangChain dependencies not available, using local time calculation only")
        
        self.time_calculator = TimeCalculator()
        self.prompt_templates = TimePrompt()
    
    def process_query(self, user_query):
        """
        Process user query and return structured time information
        
        Args:
            user_query (str): User's time-related question
            
        Returns:
            str: JSON string with time information
        """
        # Always try local calculation first for reliability
        try:
            local_result = self._create_fallback_response(user_query)
            return local_result
        except Exception as e:
            # If local calculation fails, try LLM as fallback
            if self.use_llm:
                return self._try_llm_processing(user_query)
            else:
                # Return error response if both methods fail
                error_response = {
                    "error": f"Local calculation failed: {str(e)}",
                    "time_reference": "unknown",
                    "action": "error_occurred",
                    "calculated_date": "unknown",
                    "days_from_now": "unknown",
                    "weekday": "unknown",
                    "calculation_type": "error"
                }
                return json.dumps(error_response, ensure_ascii=False, indent=2)
    
    def _try_llm_processing(self, user_query):
        """
        Try to process query using LLM as fallback
        
        Args:
            user_query (str): User's time-related question
            
        Returns:
            str: JSON string with time information
        """
        if not self.use_llm or not self.client:
            return self._create_fallback_response(user_query)
            
        try:
            # Get system and user prompts
            system_prompt = self.prompt_templates.get_system_prompt()
            user_prompt = self.prompt_templates.get_time_query_prompt().format(
                user_query=user_query
            )
            
            # Create messages for LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Get LLM response
            response = self.client.invoke(messages)
            llm_response = response.content
            
            # Try to extract JSON from LLM response
            try:
                # Look for JSON content in the response
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                
                if json_start != -1 and json_end != 0:
                    json_content = llm_response[json_start:json_end]
                    # Validate JSON
                    json.loads(json_content)
                    return json_content
                else:
                    # Fallback: create structured response using enhanced time calculator
                    return self._create_fallback_response(user_query)
                    
            except json.JSONDecodeError:
                # If LLM response is not valid JSON, create fallback
                return self._create_fallback_response(user_query)
                
        except Exception as e:
            # If LLM fails, fall back to local calculation
            print(f"LLM processing failed: {e}, falling back to local calculation")
            return self._create_fallback_response(user_query)
    
    def _create_fallback_response(self, user_query):
        """
        Create fallback response using enhanced time calculator
        This is the primary method for reliable time calculation
        
        Args:
            user_query (str): Original user query
            
        Returns:
            str: JSON string with calculated time information
        """
        # Extract time reference from query
        time_reference = self._extract_time_reference(user_query)
        
        # Get date information using enhanced time calculator
        date_info = self.time_calculator.get_date_info(time_reference)
        
        # Create structured response
        response = {
            "time_reference": date_info["time_reference"],
            "action": self._extract_action(user_query),
            "calculated_date": date_info["calculated_date"],
            "days_from_now": date_info["days_from_now"],
            "weekday": date_info["weekday"],
            "calculation_type": date_info.get("calculation_type", "local_calculation")
        }
        
        return json.dumps(response, ensure_ascii=False, indent=2)
    
    def _extract_time_reference(self, query):
        """Extract time reference from user query for enhanced parsing"""
        # The enhanced time calculator can handle complex patterns directly
        # So we just return the full query for parsing
        return query
    
    def _extract_action(self, query):
        """Extract action from user query"""
        query_lower = query.lower()
        
        if "trading" in query_lower or "giao dịch" in query_lower or "trade" in query_lower:
            return "trading"
        elif "làm gì" in query_lower:
            return "planning"
        elif "hẹn" in query_lower:
            return "appointment"
        elif "nên" in query_lower:
            return "recommendation"
        else:
            return "general_activity"