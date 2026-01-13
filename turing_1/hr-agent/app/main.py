"""
HR Agent System - Main Application Entry Point

This module initializes the FastAPI application and configures all routes.
It serves as the central hub for the HR Agent system that handles:
- Authentication (Keycloak OAuth2 only)
- HR data queries (leave balance, capex, organization members)
- General AI responses (via Ollama/Llama3 LLM)

Authentication Flow:
1. User visits /auth/keycloak/login
2. Redirected to Keycloak login page
3. After login, redirected to /auth/keycloak/callback with auth code
4. Session cookie is set automatically
5. User can now access /v1/completions with session cookie

Author: HR Agent Development Team
Version: 1.0.0
"""

from fastapi import FastAPI
from api.routes import router
from auth.oauth2_routes import oauth2_router

# ============================================================================
# FastAPI Application Initialization
# ============================================================================
# Create the FastAPI application instance with metadata
# This will be used by Uvicorn to run the server
app = FastAPI(
    title="HR Agent System",
    description="An intelligent HR Agent with Keycloak OAuth2 authentication",
    version="1.0.0"
)

# ============================================================================
# Router Configuration
# ============================================================================
# Include all API routes from the routes module
# Routes include: /v1/completions (protected endpoint)
app.include_router(router)

# Include OAuth2 routes for Keycloak authentication
# Endpoints: /auth/keycloak/login, /auth/keycloak/callback, /auth/me, /auth/logout, /auth/providers
app.include_router(oauth2_router)

# ============================================================================
# Health Check Endpoint
# ============================================================================
@app.get("/")
def health():
    """
    Health check endpoint to verify the server is running.
    
    This endpoint is useful for:
    - Load balancer health checks
    - Monitoring and alerting systems
    - Quick verification that the API is operational
    
    Returns:
        dict: Status message indicating the server is running
    
    Example:
        GET / → {"status": "HR Agent Running"}
    """
    return {"status": "HR Agent Running"}
