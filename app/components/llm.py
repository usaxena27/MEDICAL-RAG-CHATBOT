import os
from langchain_groq import ChatGroq
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

def load_llm(model_name: str = "llama-3.1-8b-instant"):
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")

        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        logger.info("Loading LLM from Groq using LLaMA3 model...")

        llm = ChatGroq(
            model=model_name,
            temperature=0.3,
            max_tokens=256,
            groq_api_key=groq_api_key,
        )

        logger.info("LLM loaded successfully from Groq.")
        return llm

    except Exception as e:
        error_message = CustomException("Failed to load LLM from Groq", e)
        logger.error(str(error_message))
        raise error_message
