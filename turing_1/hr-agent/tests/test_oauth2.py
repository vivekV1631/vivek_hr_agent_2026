"""
OAuth2 Tests

Tests for OAuth2 authentication service and session management.
"""

import pytest
from app.auth.oauth2_service import OAuth2Service
from app.auth.oauth2_config import SESSION_STORAGE

def test_create_session():
    """Test session creation and storage"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "access_token": "test_token"
    }
    
    session_id = OAuth2Service.create_session(user_data, "github")
    
    # Verify session was created
    assert session_id is not None
    assert session_id in SESSION_STORAGE
    
    # Verify session data
    session = SESSION_STORAGE[session_id]
    assert session["provider"] == "github"
    assert session["user_data"]["username"] == "testuser"
    assert session["access_token"] == "test_token"

def test_get_session():
    """Test session retrieval"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com"
    }
    
    session_id = OAuth2Service.create_session(user_data, "keycloak")
    retrieved_session = OAuth2Service.get_session(session_id)
    
    # Verify session retrieval
    assert retrieved_session is not None
    assert retrieved_session["provider"] == "keycloak"
    assert retrieved_session["user_data"]["username"] == "testuser"

def test_get_nonexistent_session():
    """Test retrieving non-existent session"""
    session = OAuth2Service.get_session("nonexistent_id")
    assert session is None

def test_delete_session():
    """Test session deletion (logout)"""
    user_data = {"username": "testuser"}
    session_id = OAuth2Service.create_session(user_data, "github")
    
    # Delete session
    result = OAuth2Service.delete_session(session_id)
    assert result is True
    
    # Verify session is deleted
    assert OAuth2Service.get_session(session_id) is None

def test_delete_nonexistent_session():
    """Test deleting non-existent session"""
    result = OAuth2Service.delete_session("nonexistent_id")
    assert result is False

def test_keycloak_auth_url_generation():
    """Test Keycloak authorization URL generation"""
    state = "test_state_123"
    auth_url = OAuth2Service.get_keycloak_auth_url(state)
    
    # Verify URL components
    assert "client_id=" in auth_url
    assert "state=test_state_123" in auth_url
    assert "response_type=code" in auth_url

def test_github_auth_url_generation():
    """Test GitHub authorization URL generation"""
    state = "test_state_456"
    auth_url = OAuth2Service.get_github_auth_url(state)
    
    # Verify URL components
    assert "client_id=" in auth_url
    assert "state=test_state_456" in auth_url
    assert "scope=user:email" in auth_url
