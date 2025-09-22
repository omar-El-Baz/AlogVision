import os
import ast
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .src.code_analyzer import CodeAnalyzer
from .src.llm_integration.llm_client import LLMClient, LLMClientError
from .src.llm_integration.purpose_analyzer import PurposeAnalyzer
from .src.llm_integration.semantic_matcher import SemanticMatcher # Ensure this is imported
from .src.llm_integration.hierarchical_explainer import HierarchicalExplainer
from .src.token_manager import TokenManager

# Loading the secret API key from the .env file and initializing clients
load_dotenv()
llm_client = LLMClient()
token_manager = TokenManager()

# Initializing FastAPI App
app = FastAPI()


origins = [
    "http://localhost:8501", 
    "http://127.0.0.0.1:8501",  
    "https://alogvision.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods including POST and OPTIONS 
    allow_headers=["*"], # Allows all headers including Content-Type
)


# Defining Request Data Structure 
class ExplainRequest(BaseModel):
    code: str
    purpose: str | None = None 
    
# --- Create the API Endpoint ---
@app.post("/explain/")
async def explain_code(request: ExplainRequest):
    """
    This endpoint receives Python code and an optional purpose,
    then returns a detailed AI-generated explanation.
    """
    
    code_to_explain = request.code
    user_purpose = request.purpose
    
    
    # 1. Validate Code Syntax
    try:
        ast.parse(code_to_explain)
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Python Code Syntax: {e}")
    
    
    # 2. Validate API Key is available on the server
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="API key is not configured on the server. Please set GEMINI_API_KEY.")


    # 3. Validate Input Size
    if not token_manager.validate_input_size(code_to_explain):
        raise HTTPException(status_code=413, detail="Input code exceeds the maximum allowed size.")

    # 4. Execute the full analysis pipeline (your original logic)
    try:
        
        
        code_analyzer = CodeAnalyzer(code_to_explain)
        code_analysis = code_analyzer.analyze()
        
        structured_purpose = None
        match_report = None # Initialize match_report

        if user_purpose:
            purpose_analyzer = PurposeAnalyzer(llm_client)
            structured_purpose = purpose_analyzer.analyze_purpose(user_purpose)
            
            matcher = SemanticMatcher(llm_client)
            match_report = matcher.generate_match_report(structured_purpose, code_analysis) # Call the matcher

        explainer = HierarchicalExplainer(llm_client)
        explanation = explainer.generate_explanation(
            code_string=code_to_explain,
            code_analysis=code_analysis,
            validated_purpose=structured_purpose,
            match_report=match_report # Pass the match report to the explainer
        )

        # 5. Return the final result
        return {"explanation": explanation}

    except LLMClientError as e:
        raise HTTPException(status_code=503, detail=f"An error occurred with the AI model: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {e}")
