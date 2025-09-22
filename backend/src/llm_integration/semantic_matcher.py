import json
from .llm_client import LLMClient

class SemanticMatcher:
    """
    Uses an LLM to compare a user's stated purpose with the actual code structure.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_match_report(self, structured_purpose: dict, code_analysis: dict) -> dict:
        """
        Compares the purpose and code analysis to generate a match report with a confidence score.
        """
        prompt = f"""
        You are a code validation expert. Your task is to determine if a Python script's implementation matches the user's stated purpose.

        **User's Stated Purpose (Structured):**
        ```json
        {json.dumps(structured_purpose, indent=2)}
        ```

        **Actual Code Structure Analysis (from AST):**
        ```json
        {json.dumps(code_analysis, indent=2)}
        ```

        Analyze both JSON objects. Does the code's structure (e.g., function names, dependencies, recursion) plausibly implement the user's purpose?
        
        Respond with ONLY a JSON object in the following format:
        {{
            "match_confidence": A float between 0.0 (no match) and 1.0 (perfect match).
            "reason": "A brief, one-sentence explanation for your confidence score, highlighting the key reason for the match or mismatch."
        }}
        """
        
        return self.llm_client.make_request(prompt, is_json_output=True)

if __name__ == '__main__':
    
    sample_purpose = {
        "main_functionality": "A recursive function to find the GCD.",
        "key_algorithms": ["recursion"],
        "inputs": "two integers",
        "outputs": "one integer"
    }
    sample_analysis = {
        "functions": {
            "rec": {
                "parameters": ["a", "b"],
                "dependencies": {"calls": ["rec"]} # Indicates recursion
            }
        }
    }

    client = LLMClient()
    matcher = SemanticMatcher(llm_client=client)
    match_report = matcher.generate_match_report(sample_purpose, sample_analysis)
    
    print(json.dumps(match_report, indent=2))