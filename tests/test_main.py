import pytest
from fastapi.testclient import TestClient
from backend.main import app 

client = TestClient(app)

# A sample valid Python code for testing
SAMPLE_CODE = "def hello():\n    print('Hello, World!')"

# --- Test Cases ---

def test_explain_code_success(mocker, monkeypatch):
    """
    Tests the /explain/ endpoint for a successful request (200 OK).
    It mocks the entire analysis pipeline to ensure the endpoint logic works.
    """
    # 1. Arrange
    # Ensuring the API key is set for the test environment
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")

    # Mocking the dependencies called within the endpoint
    mocker.patch("backend.main.ast.parse") # Mocks syntax validation to succeed
    mocker.patch("backend.main.TokenManager.validate_input_size", return_value=True)
    mocker.patch("backend.main.CodeAnalyzer.analyze", return_value={"summary": "mocked analysis"})
    mocker.patch(
        "backend.main.HierarchicalExplainer.generate_explanation",
        return_value="## Mocked Explanation\nThis is a test."
    )

    # 2. Act
    response = client.post("/explain/", json={"code": SAMPLE_CODE})
    
    # 3. Assert
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert data["explanation"] == "## Mocked Explanation\nThis is a test."

def test_explain_code_invalid_syntax(monkeypatch):
    """
    Tests that the endpoint returns a 400 Bad Request for invalid Python syntax.
    """
    # 1. Arrang
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    invalid_code = "def invalid syntax:"

    # 2. Act
    response = client.post("/explain/", json={"code": invalid_code})

    # 3. Assert
    assert response.status_code == 400
    assert "Invalid Python Code Syntax" in response.json()["detail"]

def test_explain_code_no_api_key(monkeypatch):
    """
    Tests that the endpoint returns a 500 Internal Server Error if the API key is missing.
    """
    # 1. Arrange
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    # 2. Act
    response = client.post("/explain/", json={"code": SAMPLE_CODE})

    # 3. Assert
    assert response.status_code == 500
    assert response.json()["detail"] == "API key is not configured on the server. Please set GEMINI_API_KEY."
        
def test_explain_code_input_too_large(mocker, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    mocker.patch("backend.main.ast.parse")
    mocker.patch("backend.main.TokenManager.validate_input_size", return_value=False)
    response = client.post("/explain/", json={"code": SAMPLE_CODE})
    assert response.status_code == 413
    assert response.json()["detail"] == "Input code exceeds the maximum allowed size."
    
from backend.src.llm_integration.llm_client import LLMClientError

def test_explain_code_llm_client_error(mocker, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    mocker.patch("backend.main.ast.parse")
    mocker.patch("backend.main.TokenManager.validate_input_size", return_value=True)
    # Make any LLMClient interaction raise an error
    mocker.patch(
        "backend.main.LLMClient.make_request",
        side_effect=LLMClientError("Mock LLM failure")
    )
    
    response = client.post("/explain/", json={"code": SAMPLE_CODE})
    assert response.status_code == 503
    assert "An error occurred with the AI model: Mock LLM failure" in response.json()["detail"]
    
def test_explain_code_with_purpose_success(mocker, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-api-key")
    mocker.patch("backend.main.ast.parse")
    mocker.patch("backend.main.TokenManager.validate_input_size", return_value=True)
    mocker.patch("backend.main.CodeAnalyzer.analyze", return_value={"summary": "mocked analysis"})
    mocker.patch("backend.main.PurposeAnalyzer.analyze_purpose", return_value={"structured_purpose": "mocked"})
    mocker.patch("backend.main.SemanticMatcher.generate_match_report", return_value={"match": 0.9})
    mocker.patch(
        "backend.main.HierarchicalExplainer.generate_explanation",
        return_value="## Mocked Explanation with Purpose\nThis is a test."
    )

    response = client.post("/explain/", json={"code": SAMPLE_CODE, "purpose": "Test purpose"})
    
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data
    assert data["explanation"] == "## Mocked Explanation with Purpose\nThis is a test."
    assert mocker.call("backend.main.PurposeAnalyzer.analyze_purpose").called
    assert mocker.call("backend.main.SemanticMatcher.generate_match_report").called