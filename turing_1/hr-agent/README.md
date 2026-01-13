# HR Agent Prototype

A production-style HR Agent that integrates with a Large Language Model (LLM), supports secure authentication, and provides HR-related query responses through mocked SuccessFactors integrations.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Example Queries](#example-queries)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Security](#security)
- [Future Enhancements](#future-enhancements)

---

## ✨ Features

✅ **HR Agent Core** — Intelligent HR query handling via OpenAI-style `/v1/completions` API  
✅ **LLM Integration** — Uses Ollama with Llama3 (open-source, runs locally)  
✅ **JWT Authentication** — Secure token-based login  
✅ **OAuth2 Authentication** — Multi-provider support (Keycloak, GitHub)  
✅ **Secure Session Management** — Server-side session storage with expiration  
✅ **Mocked SuccessFactors APIs** — Realistic HR function responses without real SAP integration  
✅ **Modular Architecture** — Clear separation: auth, LLM, HR functions  
✅ **Multiple HR Functions:**
- Get organization members by UID
- Get team capex (compensation, bonus, etc.)
- Get leave balance
- General AI responses via Ollama

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client (UI/CLI)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            API Routes (/v1/completions)              │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────────┐
        ↓                ↓                     ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Auth       │  │ HR Functions │  │ LLM (Ollama)     │
│ (JWT + OAuth2)  │ (mocked SAP) │  │  (Llama3)        │
└──────────────┘  └──────────────┘  └──────────────────┘
```

### Component Details

- **FastAPI Server** — RESTful API for HR agent
- **Authentication** — Dual auth system:
  - JWT (username/password) via `/login`
  - OAuth2 (Keycloak/GitHub) via `/auth/keycloak/login` or `/auth/github/login`
- **Session Management** — Server-side session storage with expiration
- **HR Functions** — Mocked SuccessFactors API calls
  - `leave.py` — Leave balance queries
  - `capex.py` — Team compensation & bonus data
  - `org.py` — Organization member data
- **Ollama LLM** — Local open-source LLM for general queries

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Server | Uvicorn |
| LLM | Ollama + Llama3 |
| Authentication | JWT (PyJWT) |
| Language | Python 3.9+ |
| Package Manager | pip |

---

## 📦 Prerequisites

1. **Python 3.9+** installed
2. **Ollama** installed and running locally
   - Download: https://ollama.ai
   - Pull Llama3: `ollama pull llama3`
   - Start: `ollama serve` (runs on `http://localhost:11434`)
3. **Virtual Environment** (recommended)

---

## 🚀 Setup & Installation

### 1. Clone the Repository

```bash
cd /Users/vivek/Documents/Deekaha_docs\ /check/rag_proj/turing_1/hr-agent
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the project root:

```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=True
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

Or use the provided `.env.example`:

```bash
cp .env.example .env
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `supersecretkey` | JWT signing key (change in production) |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiration time |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3` | LLM model name |
| `DEBUG` | `False` | Debug mode |

---

## 🏃 Running the Application

### Step 1: Start Ollama (in a separate terminal)

```bash
ollama serve
```

Expected output:
```
2025-01-12 15:30:00 listening on 127.0.0.1:11434
```

### Step 2: Start FastAPI Server

```bash
cd /Users/vivek/Documents/Deekaha_docs\ /check/rag_proj/turing_1/hr-agent
source .venv/bin/activate
uvicorn app.main:app --port 8001 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

### Step 3: Test the Server

```bash
curl http://localhost:8001/
```

Expected response:
```json
{"status": "HR Agent Running"}
```

---

## 📡 API Endpoints

### JWT Authentication Endpoints

#### 1. Health Check
```bash
GET /
```
Response:
```json
{"status": "HR Agent Running"}
```

#### 2. Login (Get JWT Token)
```bash
POST /login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. HR Agent Completions (Main Endpoint)
```bash
POST /v1/completions
Authorization: Bearer <YOUR_TOKEN>
Content-Type: application/json

{
  "prompt": "Tell me my leave balance"
}
```

Response (if specific HR query):
```json
{
  "response": {
    "annual": 12,
    "sick": 5
  }
}
```

Response (if general query):
```json
{
  "response": "Generated response from Llama3 LLM..."
}
```

### OAuth2 Authentication Endpoints

#### 4. Get Available Providers
```bash
GET /auth/providers
```

Response:
```json
{
  "providers": {
    "keycloak": {
      "available": true,
      "url": "/auth/keycloak/login"
    },
    "github": {
      "available": true,
      "url": "/auth/github/login"
    }
  }
}
```

#### 5. GitHub OAuth2 Login
```bash
GET /auth/github/login
```
Redirects to GitHub authorization page. After user approves, GitHub redirects with session cookie.

#### 6. GitHub OAuth2 Callback (Automatic)
```bash
GET /auth/github/callback?code=<AUTH_CODE>&state=<STATE>
```
Handled automatically by server. Returns session cookie.

#### 7. Keycloak OAuth2 Login
```bash
GET /auth/keycloak/login
```
Redirects to Keycloak authorization page. After user approves, Keycloak redirects with session cookie.

#### 8. Get Current User Info
```bash
GET /auth/me
Cookie: session_id=<YOUR_SESSION_ID>
```

Response:
```json
{
  "authenticated": true,
  "provider": "github",
  "username": "your-github-username",
  "created_at": "2025-01-13T10:30:00"
}
```

#### 9. Logout
```bash
POST /auth/logout
Cookie: session_id=<YOUR_SESSION_ID>
```

Response:
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

## 💡 Example Queries

### 1. Get Leave Balance
```bash
curl -X POST http://localhost:8001/v1/completions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is my leave balance?"}'
```

### 2. Get Team Capex
```bash
curl -X POST http://localhost:8001/v1/completions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me team capex for comp and bonus"}'
```

### 3. Get Organization Members
```bash
curl -X POST http://localhost:8001/v1/completions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Who are the members of my organization?"}'
```

### 4. General AI Query
```bash
curl -X POST http://localhost:8001/v1/completions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain machine learning in simple terms"}'
```

### 5. OAuth2 GitHub Login
```bash
# Get list of available providers
curl http://localhost:8001/auth/providers

# Redirect to GitHub login
curl -i http://localhost:8001/auth/github/login

# After user authorizes, get current user info
curl -b "session_id=<session-id>" http://localhost:8001/auth/me
```

---

## 🔐 OAuth2 Setup

For detailed OAuth2 configuration (Keycloak + GitHub), see [OAUTH2_SETUP.md](OAUTH2_SETUP.md)

Quick start:
1. **GitHub**: Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in `.env`
2. **Keycloak**: Set `KEYCLOAK_CLIENT_SECRET` in `.env` (requires Keycloak server)

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Specific Module

```bash
pytest tests/test_hr_functions.py -v
```

---

## 📁 Project Structure

```
hr-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── auth/
│   │   └── jwt_auth.py         # JWT authentication logic
│   ├── hr_functions/
│   │   ├── leave.py            # Leave balance mocked API
│   │   ├── capex.py            # Team capex mocked API
│   │   └── org.py              # Organization members mocked API
│   └── llm/
│       └── ollama_client.py    # Ollama/Llama3 integration
├── tests/
│   ├── __init__.py
│   └── test_hr_functions.py    # Unit tests
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                     # This file
└── .gitignore                   # Git ignore rules
```

---

## 🔒 Security

### Best Practices Implemented

✅ **JWT Tokens** — Signed tokens for API authentication  
✅ **Password Hashing** — SHA256 hashing for stored passwords  
✅ **Environment Variables** — Sensitive data in `.env` (not in repo)  
✅ **Secret Key** — Change `SECRET_KEY` in production  

### Production Recommendations

- [ ] Use bcrypt or Argon2 for password hashing
- [ ] Implement Keycloak for OAuth2
- [ ] Add HTTPS/TLS
- [ ] Use environment-specific configurations
- [ ] Implement rate limiting
- [ ] Add request logging & monitoring
- [ ] Use production ASGI server (Gunicorn + Uvicorn)

---

## 🔮 Future Enhancements

1. **Vector Database (RAG)** — Add Chroma for context-aware responses
   - Store HR policies, guidelines and other company documents.
   - Retrieve relevant context and prepend to LLM prompts for accurate answers.

   Quick RAG setup (local, open-source):
   1. Install RAG dependencies:
      ```bash
      pip install chromadb sentence-transformers torch transformers
      ```      pip install chromadb sentence-transformers torch transformers
   2. Ingest sample company docs (creates data/company_policies/*.txt and stores embeddings):
      ```bashany docs (creates data/company_policies/*.txt and stores embeddings):
      python scripts/ingest_policies.py
      ```est_policies.py
   3. Verify Chroma DB directory `chroma_db` exists and is persisted after ingestion.      ```
   4. Start the app and ensure Ollama is running:
      ```bash
      uvicorn app.main:app --port 8001 --reload
      ollama serve
      ```
   5. Login via Keycloak (browser): `http://localhost:8001/auth/keycloak/login`
   6. Call completions endpoint; RAG will fetch relevant docs and augment prompt automatically:
      ```bash
      # after browser login (session cookie present)
      curl -b cookies.txt -H "Content-Type: application/json" \
        -d '{"prompt":"What is our leave policy?"}' \
        http://localhost:8001/v1/completions
      ```

   Implementation notes:
   - `app/rag/rag_service.py` implements Chroma ingestion and query helpers.
   - Use `scripts/ingest_policies.py` to create sample policy files and ingest them.
   - `get_relevant_context(query, top_k)` returns top-k docs; the completions route prepends these to the LLM prompt.

2. **OAuth2 with Keycloak** — Replace JWT with Keycloak integration
   - Support Google/GitHub/Microsoft login
   - Secure token/session storage

3. **Extended HR Functions** — Add more mocked APIs
   - Performance reviews
   - Training records
   - Payroll information

4. **Response Caching** — Cache frequently asked questions

5. **Analytics & Logging** — Track queries, responses, user activity

6. **API Documentation** — Swagger UI integration

---

## Acknowledgments

- FastAPI for the excellent web framework
- Ollama for local LLM support
- Meta for Llama3 model