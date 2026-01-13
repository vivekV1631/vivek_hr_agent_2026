"""
OAuth2 Service Module

Handles OAuth2 authentication flows with Keycloak and GitHub.
Manages token exchange, user info retrieval, and session storage.
"""

import httpx
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .oauth2_config import (
    KEYCLOAK_AUTHORIZE_URL, KEYCLOAK_TOKEN_URL, KEYCLOAK_USERINFO_URL,
    KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, KEYCLOAK_REDIRECT_URI,
    GITHUB_AUTHORIZE_URL, GITHUB_TOKEN_URL, GITHUB_USERINFO_URL,
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI,
    SESSION_TIMEOUT, SESSION_STORAGE
)

class OAuth2Service:
    """
    Service class for OAuth2 authentication operations.
    Handles token exchange, user retrieval, and session management.
    """

    @staticmethod
    def get_keycloak_auth_url(state: str) -> str:
        """
        Generate Keycloak OAuth2 authorization URL.
        
        Args:
            state: CSRF protection token
            
        Returns:
            Keycloak authorization URL for user redirect
        """
        params = {
            "client_id": KEYCLOAK_CLIENT_ID,
            "redirect_uri": KEYCLOAK_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{KEYCLOAK_AUTHORIZE_URL}?{query_string}"

    @staticmethod
    async def exchange_keycloak_code(code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange Keycloak authorization code for access token.
        
        Args:
            code: Authorization code from Keycloak callback
            
        Returns:
            Token response with access_token and user info, or None if exchange fails
        """
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "client_id": KEYCLOAK_CLIENT_ID,
                    "code": code,
                    "redirect_uri": KEYCLOAK_REDIRECT_URI,
                    "grant_type": "authorization_code",
                }
                # Include client_secret only if configured (confidential client)
                if KEYCLOAK_CLIENT_SECRET:
                    data["client_secret"] = KEYCLOAK_CLIENT_SECRET

                response = await client.post(
                    KEYCLOAK_TOKEN_URL,
                    data=data,
                    headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Keycloak token exchange failed: {e}")
            return None

    @staticmethod
    async def get_keycloak_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """
        Fetch authenticated Keycloak user information using the userinfo endpoint.
        
        Args:
            access_token: Keycloak access token
        
        Returns:
            User profile data (dict) or None on failure
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    KEYCLOAK_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Keycloak user info retrieval failed: {e}")
            return None

    @staticmethod
    def get_github_auth_url(state: str) -> str:
        """
        Generate GitHub OAuth2 authorization URL.
        
        Args:
            state: CSRF protection token
            
        Returns:
            GitHub authorization URL for user redirect
        """
        params = {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": GITHUB_REDIRECT_URI,
            "scope": "user:email",
            "state": state,
            "allow_signup": "true"
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{GITHUB_AUTHORIZE_URL}?{query_string}"

    @staticmethod
    async def exchange_github_code(code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange GitHub authorization code for access token.
        
        Args:
            code: Authorization code from GitHub callback
            
        Returns:
            Token response with access_token, or None if exchange fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GITHUB_TOKEN_URL,
                    headers={"Accept": "application/json"},
                    data={
                        "client_id": GITHUB_CLIENT_ID,
                        "client_secret": GITHUB_CLIENT_SECRET,
                        "code": code,
                        "redirect_uri": GITHUB_REDIRECT_URI,
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"GitHub token exchange failed: {e}")
            return None

    @staticmethod
    async def get_github_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """
        Fetch authenticated GitHub user information.
        
        Args:
            access_token: GitHub access token
            
        Returns:
            GitHub user profile data, or None if retrieval fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GITHUB_USERINFO_URL,
                    headers={"Authorization": f"token {access_token}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"GitHub user info retrieval failed: {e}")
            return None

    @staticmethod
    def create_session(user_data: Dict[str, Any], provider: str) -> str:
        """
        Create and store user session.
        
        Args:
            user_data: User information to store in session
            provider: OAuth2 provider name (keycloak/github)
            
        Returns:
            Session ID (token) for session retrieval
        """
        session_id = str(uuid.uuid4())
        expiry = datetime.utcnow() + timedelta(seconds=SESSION_TIMEOUT)
        
        SESSION_STORAGE[session_id] = {
            "user_data": user_data,
            "provider": provider,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expiry.isoformat(),
            "access_token": user_data.get("access_token")
        }
        
        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data by session ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data if valid and not expired, None otherwise
        """
        if session_id not in SESSION_STORAGE:
            return None
        
        session = SESSION_STORAGE[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        # Check if session has expired
        if datetime.utcnow() > expires_at:
            del SESSION_STORAGE[session_id]
            return None
        
        return session

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        Delete a session (logout).
        
        Args:
            session_id: Session identifier to delete
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in SESSION_STORAGE:
            del SESSION_STORAGE[session_id]
            return True
        return False


def get_user_from_session(request) -> Optional[Dict[str, Any]]:
    """
    Extract user from Keycloak session cookie.
    Used by routes to get authenticated user info.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        User dict if valid session exists, None otherwise
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    
    session = OAuth2Service.get_session(session_id)
    if session:
        return {
            "uid": session.get("user_id"),
            "sub": session.get("user_id"),
            "email": session.get("email"),
            "provider": session.get("provider")
        }
    return None
