# src/llm_integration/llm_client.py

import os
import json
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import logging
from backend.src.utils.loggin_config import setup_logging

setup_logging()

# Define a custom exception for cleaner error handling
class LLMClientError(Exception):
    """Custom exception for LLM client errors."""
    pass

class LLMClient:
    """A centralized client for interacting with the LLM API."""
    def __init__(self, model_name: str = "gemini-1.5-flash-latest"): # Updated default model
        api_key = os.environ.get("GEMINI_API_KEY") # Changed to GEMINI_API_KEY
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable not set.")
            raise EnvironmentError("GEMINI_API_KEY environment variable not set.")
        
        genai.configure(api_key=api_key)
        self.client = genai
        self.model = model_name
        logging.info(f"LLMClient initialized with model: {self.model}")

    def make_request(self, prompt: str, is_json_output: bool = False) -> dict | str:
        """
        Makes a request to the LLM. Returns the response on success,
        and raises LLMClientError on failure.
        """
        logging.info("Making request to LLM...")
        try:
            model = self.client.GenerativeModel(self.model)
            
            generation_config = {
                "temperature": 0.2,
                "response_mime_type": "application/json" if is_json_output else "text/plain",
            }

            # Safety settings for Gemini (optional but recommended)
            # Adjust as needed for your application's tolerance
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            content = response.text
            
            if is_json_output:
                # Also validate JSON here
                return json.loads(content)
            return content
            
        except GoogleAPIError as e: # Changed error type
            logging.error(f"LLM API Error: {e}")
            raise LLMClientError(f"The LLM API returned an error: {e}") from e
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from LLM response: {e}. Response was: {content}")
            raise LLMClientError("The model returned invalid JSON.") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise LLMClientError(f"An unexpected error occurred: {e}") from e