"""
OAuth2 Authentication Routes

Provides endpoints for OAuth2 login, callback handling, and session management.
Supports Keycloak and GitHub providers.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
import uuid
from .oauth2_config import is_keycloak_configured, is_github_configured
from .oauth2_service import OAuth2Service

oauth2_router = APIRouter(prefix="/auth", tags=["OAuth2 Authentication"])

# ============================================================================
# Keycloak OAuth2 Endpoints
# ============================================================================

@oauth2_router.get("/keycloak/login")
async def keycloak_login():
    """
    Initiate Keycloak OAuth2 login flow.
    Redirects user to Keycloak authorization endpoint and stores a CSRF state cookie.
    """
    if not is_keycloak_configured():
        raise HTTPException(
            status_code=503,
            detail="Keycloak not configured. Set KEYCLOAK_CLIENT_ID and KEYCLOAK_SERVER_URL environment variables."
        )

    state = str(uuid.uuid4())  # CSRF protection token
    auth_url = OAuth2Service.get_keycloak_auth_url(state)

    response = RedirectResponse(url=auth_url)
    # store state in a short-lived HttpOnly cookie for CSRF protection
    response.set_cookie("oauth_state", state, httponly=True, secure=False)
    return response

@oauth2_router.get("/keycloak/callback")
async def keycloak_callback(request: Request, code: str = None, state: str = None):
    """
    Handle Keycloak OAuth2 callback.
    Exchange authorization code for access token, fetch user info and create session.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    # Validate state (CSRF)
    state_cookie = request.cookies.get("oauth_state")
    if not state or not state_cookie or state != state_cookie:
        raise HTTPException(status_code=400, detail="Invalid or missing state parameter")

    # Exchange code for token
    tokens = await OAuth2Service.exchange_keycloak_code(code)
    if not tokens or "access_token" not in tokens:
        raise HTTPException(status_code=500, detail="Token exchange failed")

    access_token = tokens.get("access_token")

    # Get Keycloak user info
    user_info = await OAuth2Service.get_keycloak_user_info(access_token)
    if not user_info:
        raise HTTPException(status_code=500, detail="Failed to retrieve user info")

    # Create session with user data
    user_data = {
        "access_token": access_token,
        "refresh_token": tokens.get("refresh_token"),
        "id_token": tokens.get("id_token"),
        "user_id": user_info.get("sub") or user_info.get("preferred_username"),
        "username": user_info.get("preferred_username") or user_info.get("username") or user_info.get("name"),
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "provider": "keycloak"
    }
    session_id = OAuth2Service.create_session(user_data, "keycloak")

    # Return session ID to client (store in secure cookie) and clear state cookie
    response = JSONResponse({
        "status": "success",
        "message": "Logged in with Keycloak",
        "provider": "keycloak",
        "session_id": session_id,
        "user": {
            "username": user_data.get("username"),
            "email": user_data.get("email")
        }
    })
    response.set_cookie("session_id", session_id, httponly=True, secure=False)
    response.delete_cookie("oauth_state")
    return response

# ============================================================================
# GitHub OAuth2 Endpoints
# ============================================================================

@oauth2_router.get("/github/login")
async def github_login():
    """
    Initiate GitHub OAuth2 login flow.
    Redirects user to GitHub authorization endpoint.
    """
    if not is_github_configured():
        raise HTTPException(
            status_code=503,
            detail="GitHub OAuth2 not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET."
        )
    
    state = str(uuid.uuid4())  # CSRF protection token
    auth_url = OAuth2Service.get_github_auth_url(state)
    return RedirectResponse(url=auth_url)

@oauth2_router.get("/github/callback")
async def github_callback(request: Request, code: str = None, state: str = None):
    """
    Handle GitHub OAuth2 callback.
    Exchange authorization code for access token and fetch user info.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    # Exchange code for token
    tokens = await OAuth2Service.exchange_github_code(code)
    if not tokens or "access_token" not in tokens:
        raise HTTPException(status_code=500, detail="Token exchange failed")
    
    access_token = tokens.get("access_token")
    
    # Get GitHub user info
    user_info = await OAuth2Service.get_github_user_info(access_token)
    if not user_info:
        raise HTTPException(status_code=500, detail="Failed to retrieve user info")
    
    # Create session with user data
    user_data = {
        "access_token": access_token,
        "user_id": user_info.get("id"),
        "username": user_info.get("login"),
        "email": user_info.get("email"),
        "name": user_info.get("name"),
        "provider": "github"
    }
    session_id = OAuth2Service.create_session(user_data, "github")
    
    # Return session ID to client (store in secure cookie)
    response = JSONResponse({
        "status": "success",
        "message": f"Logged in as {user_info.get('login')}",
        "provider": "github",
        "session_id": session_id,
        "user": {
            "username": user_info.get("login"),
            "email": user_info.get("email")
        }
    })
    response.set_cookie("session_id", session_id, httponly=True, secure=False)
    return response

# ============================================================================
# Session Management Endpoints
# ============================================================================

@oauth2_router.get("/me")
async def get_current_user(request: Request):
    """
    Get current authenticated user information.
    Requires valid session ID from cookies.
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = OAuth2Service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    
    return JSONResponse({
        "authenticated": True,
        "provider": session.get("provider"),
        "username": session.get("user_data", {}).get("username", "anonymous"),
        "created_at": session.get("created_at")
    })

@oauth2_router.post("/logout")
async def logout(request: Request):
    """
    Logout user by destroying session.
    """
    session_id = request.cookies.get("session_id")
    
    if session_id:
        OAuth2Service.delete_session(session_id)
    
    response = JSONResponse({
        "status": "success",
        "message": "Logged out successfully"
    })
    response.delete_cookie("session_id")
    return response

@oauth2_router.get("/providers")
async def get_available_providers():
    """
    Get list of available OAuth2 providers and their status.
    """
    return JSONResponse({
        "providers": {
            "keycloak": {
                "available": is_keycloak_configured(),
                "url": "/auth/keycloak/login"
            },
            "github": {
                "available": is_github_configured(),
                "url": "/auth/github/login"
            }
        }
    })
