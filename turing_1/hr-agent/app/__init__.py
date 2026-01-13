"""
HR Agent System - Complete Application Package

This is the main application package for the HR Agent System.
It contains all modules organized in a clean architecture:

Package Structure:
├── app/
│   ├── __init__.py                    # Package initialization
│   ├── main.py                         # FastAPI application entry point
│   ├── api/
│   │   └── routes.py                  # API endpoint definitions
│   ├── auth/
│   │   └── jwt_auth.py               # JWT authentication
│   ├── hr_functions/
│   │   ├── leave.py                  # Leave balance queries
│   │   ├── capex.py                  # Team budget/capex
│   │   └── org.py                    # Organization structure
│   └── llm/
│       └── ollama_client.py          # Ollama LLM integration

Architecture Overview:
1. FastAPI server on port 8001
2. JWT-based authentication
3. Router-based endpoint organization
4. Separation of concerns:
   - Authentication layer (auth/)
   - Business logic layer (hr_functions/)
   - LLM integration layer (llm/)
   - API layer (api/)

How to Run:
1. Ensure Ollama is running: ollama serve
2. Start FastAPI server: uvicorn app.main:app --port 8001 --reload

Documentation:
- See README.md for full documentation
- See .env.example for configuration
- Each module has detailed docstrings

Testing:
- Run tests: pytest tests/ -v
- See tests/ folder for test examples

Author: HR Agent Development Team
Version: 1.0.0
"""
