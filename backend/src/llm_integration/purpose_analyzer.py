# src/llm_integration/purpose_analyzer.py

from .llm_client import LLMClient

class PurposeAnalyzer:
    """
    Uses an LLM to analyze and structure a user's description of code purpose.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def analyze_purpose(self, purpose_text: str) -> dict:
        """
        Extracts key components from the user's purpose description.
        """
        prompt = f"""
        You are a requirements analyst. Your task is to extract structured information from a user's description of a Python script's purpose.

        **User's Description:** "{purpose_text}"

        Analyze the description and respond with ONLY a JSON object with the following keys:
        - "main_functionality": A concise, one-sentence summary of what the code is supposed to do.
        - "key_algorithms": A list of any specific algorithms or techniques mentioned (e.g., "sorting", "recursion", "API call").
        - "inputs": A description of the expected inputs.
        - "outputs": A description of the expected outputs.

        If any information is not present, use "Not specified."
        """
        
        return self.llm_client.make_request(prompt, is_json_output=True)

if __name__ == '__main__':
    client = LLMClient()
    analyzer = PurposeAnalyzer(llm_client=client)
    
    user_purpose = "I think this code is supposed to be a recursive function that takes two numbers and finds their greatest common divisor. It should take integers as input and return a single integer."
    
    structured_purpose = analyzer.analyze_purpose(user_purpose)
    
    import json
    print(json.dumps(structured_purpose, indent=2))