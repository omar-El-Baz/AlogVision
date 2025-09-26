import ast
import os
import logging
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from backend.src.utils.loggin_config import setup_logging

setup_logging()

# Custom exception for token manager errors
class TokenManagerError(Exception):
    """Custom exception for TokenManager errors."""
    pass

class TokenManager:
    """
    Manages token counting, input validation, and intelligent, AST-based code chunking
    for Gemini models.
    """
    def __init__(self, model_name: str = "gemini-1.5-pro-001", max_tokens: int = 1_000_000):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable not set for TokenManager.")
            raise EnvironmentError("GEMINI_API_KEY environment variable not set. Cannot initialize TokenManager for Gemini.")
        
        genai.configure(api_key=api_key)
        self._genai_model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        self.max_tokens = max_tokens
        logging.info(f"TokenManager initialized with Gemini model '{self.model_name}' and max_tokens={self.max_tokens}")

    def estimate_tokens(self, text: str) -> int:
        """Estimates the number of tokens in a given text using the Gemini API."""
        try:
            response = self._genai_model.count_tokens(text)
            return response.total_tokens
        except GoogleAPIError as e:
            logging.error(f"Failed to count tokens via Gemini API: {e}")
            raise TokenManagerError(f"Failed to count tokens using Gemini API: {e}. Please check your API key and network connection.") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred during token counting: {e}")
            raise TokenManagerError(f"An unexpected error occurred during token counting: {e}") from e

    def validate_input_size(self, code: str) -> bool:
        """Checks if the code is within the acceptable token limit."""
        try:
            token_count = self.estimate_tokens(code)
            is_valid = token_count <= self.max_tokens
            if not is_valid:
                logging.error(f"Input validation failed: {token_count} tokens > {self.max_tokens} limit.")
            return is_valid
        except TokenManagerError as e:
            logging.error(f"Could not validate input size due to token counting error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to estimate token count for input validation: {e}")

    def chunk_code_intelligently(self, code: str) -> list[str]:
        """
        Splits large code into smaller chunks using the AST to preserve
        function and class boundaries.
        """
        if self.validate_input_size(code):
            return [code]

        logging.info("Code exceeds max tokens, attempting intelligent chunking...")
        
        try:
            tree = ast.parse(code)
            lines = code.splitlines()
            chunks = []
            current_chunk_lines = []
            current_chunk_tokens = 0

            # Iterate over top-level nodes (functions, classes, imports, etc.)
            for node in tree.body:
                # Get the full source text of the node
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', start_line)
                node_lines = lines[start_line:end_line]
                node_text = "\n".join(node_lines)
                
                # Use Gemini-specific token estimation for each node
                node_tokens = self.estimate_tokens(node_text)

                # If a single node is too large, it becomes its own chunk (a necessary evil)
                # Given Gemini 1.5 Flash's 1M token context, this is less likely for single Python nodes
                if node_tokens > self.max_tokens:
                    logging.warning(f"A single code block (e.g., function) starting on line {node.lineno} exceeds the token limit ({node_tokens} > {self.max_tokens}). It will be sent as a single large chunk.")
                    if current_chunk_lines: # Adding the previous chunk first
                        chunks.append("\n".join(current_chunk_lines))
                    chunks.append(node_text)
                    current_chunk_lines = []
                    current_chunk_tokens = 0
                    continue

                # If adding this node exceeds the limit, finalize the current chunk
                if current_chunk_tokens + node_tokens > self.max_tokens and current_chunk_lines:
                    chunks.append("\n".join(current_chunk_lines))
                    current_chunk_lines = []
                    current_chunk_tokens = 0
                
                current_chunk_lines.extend(node_lines)
                current_chunk_tokens += node_tokens

            # Add the last remaining chunk
            if current_chunk_lines:
                chunks.append("\n".join(current_chunk_lines))
            
            logging.info(f"Code was split into {len(chunks)} intelligent chunks.")
            return chunks

        except SyntaxError as e:
            logging.error(f"Cannot chunk code due to syntax error: {e}")
            logging.warning("Falling back to naive line-based chunking due to AST parsing failure.")
            lines = code.splitlines()
            return ["\n".join(lines[i:i + 100]) for i in range(0, len(lines), 100)]
        except TokenManagerError as e:
            logging.error(f"Failed to chunk code due to token counting error: {e}")
            raise TokenManagerError(f"Failed to chunk code due to token counting error: {e}") from e


    def preprocess_code(self, code: str) -> str:
        """Cleans code by removing extra whitespace for token efficiency.
           This is less critical with 1M token context, but still good practice."""
        lines = [line for line in code.splitlines() if line.strip()]
        return "\n".join(lines)