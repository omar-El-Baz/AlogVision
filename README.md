# AlgoVision
<p align="center">
    <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python Version">
    <img src="https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/Docker-Compose-blue?logo=docker" alt="Docker">
    <img src="https://img.shields.io/badge/JavaScript-ES6-yellow?logo=javascript" alt="JavaScript">
</p>

AlogVision is a web-based tool designed to demystify Python code for learners and developers. It goes beyond simple syntax descriptions by providing a multi-layered analysis that covers the "why," "how," and "what's next." It leverages the power of Google's Gemini LLM combined with static code analysis to act as a personal AI programming tutor.
### **Live Demo**
[AlogVision Live](https://alogvision.onrender.com/)

---

## ✨ Features

* **Hierarchical Explanations**: Get a multi-layered explanation covering everything from the high-level summary to a line-by-line analysis.
* **Purpose-Driven Analysis**: Provide the intended purpose of your code and get a validation report on how well the code aligns with your goal.
* **🧩 AST-Powered Analysis**: The backend uses Python's Abstract Syntax Tree (AST) module to perform a deep, static analysis of the code's structure, functions, and dependencies, providing rich context to the AI.
* **⏱️ Complexity Analysis**: Automatically receive Time and Space Complexity (Big O) estimations to understand your code's performance.
* **Educational Focus**: Explanations are designed to be educational, helping you understand not just *what* the code does, but *why* and *how*.
* **🐳 Dockerized & Ready-to-Deploy**: The entire application is containerized with Docker, ensuring a smooth setup and consistent environment.
---

## 🚀 How It Works

The application follows a modern client-server architecture, containerized for easy deployment and scalability.

1.  **Frontend**: A static web application built with HTML, CSS, and vanilla JavaScript provides the user interface.
2.  **Backend API**: A robust REST API built with **FastAPI** receives the code, performs static analysis, and orchestrates the AI-powered explanation generation.
3.  **AI Integration**: The backend communicates with Google's **Gemini** model to generate the detailed, human-like explanations.
4.  **Containerization**: The entire application is containerized using **Docker** and orchestrated with **Docker Compose** for consistent and isolated environments.

---

## 🛠️ Tech Stack

**Backend:**
* Python 3.11
* FastAPI
* Uvicorn
* Pydantic
* Google Generative AI SDK

**Frontend:**
* HTML5, CSS3, JavaScript
* Marked.js

**Development & Deployment:**
* Docker & Docker Compose
* Pytest
* HTTPX

---

## 🏁 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

* Docker and Docker Compose installed on your machine.
* A Google Gemini API Key.

### Installation & Running the Application

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/omar-El-Baz/AlogVision.git](https://github.com/omar-El-Baz/AlogVision.git)
    cd AlogVision
    ```

2.  **Create the environment file:**
    Create a file named `.env` in the project root and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

3.  **Build and run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the application:**
    * The **frontend** will be available at `http://localhost:8501`.
    * The **backend** API will be running at `http://localhost:8000`.

---

## 🧪 Testing

The project includes a robust suite of tests for the backend API to ensure reliability and proper error handling. The tests use pytest and FastAPI's TestClient to simulate requests and validate the responses.

```bash
pip install -r requirements-dev.txt
```
Then run pytest from the root of the project:

```bash
pytest
```
### Test Suite Coverage

The test suite covers the following critical scenarios:

* **✅ Successful Requests:** Verifies that the API returns a `200 OK` status and a valid explanation for both simple requests and requests that include a user-defined purpose.

* **🚫 Invalid Syntax:** Ensures the API correctly identifies syntactically incorrect Python code and returns a `400 Bad Request` error.

* **🔑 Missing API Key:** Confirms that the server returns a `500 Internal Server Error` if the `GEMINI_API_KEY` is not configured, preventing the application from running in a misconfigured state.

* **📦 Payload Too Large:** Checks that the API returns a `413 Payload Too Large` error if the input code exceeds the token limit defined in the `TokenManager`.

* **🤖 AI Service Failure:** Simulates an error from the Gemini API and verifies that the server handles it gracefully by returning a `503 Service Unavailable` error.


## 📂 Project Structure

```
AlogVision/
├── backend/
│   ├── src/
│   │   ├── llm_integration/
│   │   ├── utils/
│   │   ├── code_analyzer.py
│   │   └── token_manager.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── tests/
│   └── test_main.py
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

**Omar El-Baz** - omar.elsayed.elbaz@gmail.com
