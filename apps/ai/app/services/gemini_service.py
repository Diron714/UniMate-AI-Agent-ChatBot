"""
Gemini AI Service Integration
Enhanced with retry logic and error handling
"""
import os
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if not already loaded
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    import warnings
    warnings.warn("google.generativeai not available. Some features may not work.")
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

# Initialize Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key and genai:
    genai.configure(api_key=api_key)
elif not api_key:
    logger.warning("GEMINI_API_KEY not found in environment variables")
elif not genai:
    logger.warning("google.generativeai package not available")

def get_gemini_model(model_name: str = "models/gemini-2.5-flash"):
    """
    Get Gemini model instance with error handling
    
    Args:
        model_name: Name of the Gemini model to use
    
    Returns:
        GenerativeModel instance or None if error
    """
    try:
        if not api_key:
            logger.error("GEMINI_API_KEY is not configured")
            return None
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logger.error(f"Error initializing Gemini model {model_name}: {e}")
        return None

def generate_response(
    prompt: str,
    context: Optional[List[Dict]] = None,
    tools: Optional[List] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> str:
    """
    Generate response using Gemini with retry logic
    
    Args:
        prompt: User prompt/message
        context: Optional conversation context
        tools: Optional tools for function calling
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        Generated response text or error message
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            model = get_gemini_model()
            if not model:
                return "AI service is currently unavailable. Please check configuration."
            
            # Build conversation history
            if context:
                # Format context for Gemini
                conversation = []
                for msg in context:
                    if msg.get("role") == "user":
                        conversation.append({"role": "user", "parts": [msg.get("content", "")]})
                    elif msg.get("role") == "assistant":
                        conversation.append({"role": "model", "parts": [msg.get("content", "")]})
                conversation.append({"role": "user", "parts": [prompt]})
            else:
                conversation = [{"role": "user", "parts": [prompt]}]
            
            # Generate with retry logic
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            if tools:
                # If tools are provided, use function calling
                # Note: This is a simplified version - full tool integration is in LangChain
                response = model.generate_content(
                    conversation,
                    generation_config=generation_config
                )
            else:
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            
            if response and response.text:
                return response.text
            else:
                logger.warning(f"Empty response from Gemini on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                return "I received an empty response. Please try again."
                
        except Exception as e:
            last_error = e
            error_msg = str(e)
            logger.warning(f"Error generating response (attempt {attempt + 1}/{max_retries}): {error_msg}")
            
            # Check if it's a transient error (rate limit, network, etc.)
            is_transient = any(keyword in error_msg.lower() for keyword in [
                "rate limit", "quota", "timeout", "network", "connection", "503", "429"
            ])
            
            if is_transient and attempt < max_retries - 1:
                # Wait before retrying with exponential backoff
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            elif not is_transient:
                # Non-transient error, don't retry
                logger.error(f"Non-transient error: {error_msg}")
                break
    
    # All retries failed
    logger.error(f"Failed to generate response after {max_retries} attempts. Last error: {last_error}")
    return "I apologize, but I encountered an error processing your request. Please try again later."

