"""
OAuth2 Configuration and Provider Setup

Handles OAuth2 authentication with multiple providers:
- Keycloak (OpenID Connect)
- GitHub OAuth2

Stores configuration and utility functions for OAuth2 flows.
"""

import os
from typing import Optional

# ============================================================================
# Keycloak Configuration
# ============================================================================
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "hr-agent")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

# Keycloak OAuth2 endpoints
KEYCLOAK_AUTHORIZE_URL = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
KEYCLOAK_TOKEN_URL = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
KEYCLOAK_USERINFO_URL = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
KEYCLOAK_REDIRECT_URI = os.getenv("KEYCLOAK_REDIRECT_URI", "http://localhost:8001/auth/keycloak/callback")

# ============================================================================
# GitHub OAuth2 Configuration
# ============================================================================
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8001/auth/github/callback")

# ============================================================================
# Session Configuration
# ============================================================================
SESSION_TIMEOUT = 3600  # 1 hour in seconds
SESSION_STORAGE = {}  # In-memory session store (use Redis in production)

# ============================================================================
# Utility Functions
# ============================================================================

def is_keycloak_configured() -> bool:
    """Check if Keycloak is properly configured.
    Requires at least KEYCLOAK_CLIENT_ID and KEYCLOAK_SERVER_URL.
    Client secret is optional (public clients) but recommended for confidential clients.
    """
    return bool(KEYCLOAK_CLIENT_ID and KEYCLOAK_SERVER_URL)

def is_github_configured() -> bool:
    """Check if GitHub OAuth2 is properly configured"""
    return bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET)
