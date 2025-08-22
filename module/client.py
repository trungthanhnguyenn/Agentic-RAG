import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

class LangChainClient:
    """
    Client class for LangChain configuration and initialization
    Handles OpenAI API configuration from environment variables
    """
    
    def __init__(self):
        """Initialize client with environment variables"""
        load_dotenv()
        
        # Get configuration from environment variables
        self.api_key = os.getenv("OPENAI_SDK_API_KEY")
        self.base_url = os.getenv("OPENAI_SDK_BASE_URL")
        self.model_name = os.getenv("OPENAI_SDK_MODEL")
        
        # Validate required environment variables
        if not all([self.api_key, self.base_url, self.model_name]):
            raise ValueError("Missing required environment variables: OPENAI_SDK_API_KEY, OPENAI_SDK_BASE_URL, OPENAI_SDK_MODEL")
        
        # Initialize ChatOpenAI client
        self.client = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name
        )
    
    def get_client(self):
        """Return the configured ChatOpenAI client"""
        return self.client