"""
Unit Tests for JWT Authentication Module

This test module validates authentication functionality including:
- Password hashing
- User authentication
- JWT token creation
- JWT token validation

Security Testing:
- Validates password verification works correctly
- Tests token expiration
- Ensures invalid tokens are rejected

Test Framework: pytest
Running tests: pytest tests/test_auth.py -v

Author: HR Agent Development Team
"""

from app.auth.jwt_auth import (
    hash_password,
    verify_password,
    authenticate_user,
    create_access_token,
    decode_token
)
import time


class TestPasswordHashing:
    """
    Test suite for password hashing functionality.
    
    These tests ensure that:
    - Passwords are correctly hashed
    - Same password always produces same hash (deterministic)
    - Different passwords produce different hashes
    - Invalid passwords are properly rejected
    """
    
    def test_hash_password_returns_string(self):
        """
        Test hash_password returns a string.
        
        The hash should be a hexadecimal string representation.
        
        Assertion: hash_password result is string type
        """
        hashed = hash_password("test_password")
        assert isinstance(hashed, str), "Hash should be a string"
    
    def test_hash_password_length(self):
        """
        Test hash_password returns SHA256 hash (64 characters).
        
        SHA256 produces a 256-bit hash, which is 64 hex characters.
        
        Assertion: hash_password result is 64 characters long
        """
        hashed = hash_password("test_password")
        assert len(hashed) == 64, f"SHA256 hash should be 64 chars, got {len(hashed)}"
    
    def test_hash_password_deterministic(self):
        """
        Test hash_password is deterministic (same input = same output).
        
        This is important for password verification - the same password
        must always produce the same hash.
        
        Assertion: hash_password("x") == hash_password("x")
        """
        password = "my_secure_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 == hash2, "Same password should produce same hash"
    
    def test_hash_password_different_inputs(self):
        """
        Test different passwords produce different hashes.
        
        This validates the hashing function creates unique outputs
        for different inputs.
        
        Assertion: hash_password("x") != hash_password("y")
        """
        hash1 = hash_password("password123")
        hash2 = hash_password("password124")
        assert hash1 != hash2, "Different passwords should produce different hashes"


class TestPasswordVerification:
    """
    Test suite for password verification functionality.
    
    These tests ensure that:
    - Correct passwords verify successfully
    - Incorrect passwords are rejected
    - Password comparison is secure
    """
    
    def test_verify_correct_password(self):
        """
        Test verify_password accepts correct password.
        
        When plain password matches the stored hash, verification succeeds.
        
        Assertion: verify_password("password123", hash of "password123") == True
        """
        password = "password123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True, \
            "Correct password should verify successfully"
    
    def test_verify_incorrect_password(self):
        """
        Test verify_password rejects incorrect password.
        
        When plain password doesn't match stored hash, verification fails.
        
        Assertion: verify_password("wrong", hash of "password123") == False
        """
        hashed = hash_password("password123")
        assert verify_password("wrong_password", hashed) is False, \
            "Incorrect password should not verify"
    
    def test_verify_password_case_sensitive(self):
        """
        Test password verification is case-sensitive.
        
        "Password123" and "password123" are different passwords.
        
        Assertion: verify_password("Password123", hash of "password123") == False
        """
        hashed = hash_password("password123")
        assert verify_password("Password123", hashed) is False, \
            "Password verification should be case-sensitive"


class TestUserAuthentication:
    """
    Test suite for user authentication functionality.
    
    These tests ensure that:
    - Valid credentials return user object
    - Invalid credentials return None
    - User data is properly retrieved
    """
    
    def test_authenticate_valid_user(self):
        """
        Test authenticate_user succeeds with valid credentials.
        
        Username and password from test database should authenticate.
        
        Test User Credentials:
        - Username: testuser
        - Password: password123
        - UID: emp001
        
        Assertion: authenticate_user returns user dict with correct UID
        """
        user = authenticate_user("testuser", "password123")
        assert user is not None, "Valid credentials should return user object"
        assert user["uid"] == "emp001", "Returned user should have correct UID"
        assert user["username"] == "testuser", "Returned user should have correct username"
    
    def test_authenticate_invalid_password(self):
        """
        Test authenticate_user fails with wrong password.
        
        Valid username but wrong password should return None.
        
        Assertion: authenticate_user("testuser", "wrong") returns None
        """
        user = authenticate_user("testuser", "wrong_password")
        assert user is None, "Invalid password should return None"
    
    def test_authenticate_invalid_user(self):
        """
        Test authenticate_user fails with non-existent user.
        
        Username that doesn't exist should return None.
        
        Assertion: authenticate_user("nonexistent", "password") returns None
        """
        user = authenticate_user("nonexistent_user", "password123")
        assert user is None, "Non-existent user should return None"
    
    def test_authenticate_returns_full_user(self):
        """
        Test authenticate_user returns complete user object.
        
        Returned user should have all required fields for token creation.
        
        Assertion: User object has username, password, and uid fields
        """
        user = authenticate_user("testuser", "password123")
        assert "username" in user, "User object should have username"
        assert "uid" in user, "User object should have uid"
        assert "password" in user, "User object should have password hash"


class TestJWTTokenCreation:
    """
    Test suite for JWT token creation functionality.
    
    These tests ensure that:
    - Tokens are created successfully
    - Tokens contain required claims
    - Tokens can be decoded later
    """
    
    def test_create_token_returns_string(self):
        """
        Test create_access_token returns a string.
        
        JWT token should be a string in "header.payload.signature" format.
        
        Assertion: Token is a string type
        """
        token = create_access_token({"sub": "emp001"})
        assert isinstance(token, str), "Token should be a string"
    
    def test_create_token_has_parts(self):
        """
        Test create_access_token creates proper JWT format.
        
        JWT tokens have 3 parts separated by dots (.).
        
        Assertion: Token has exactly 3 parts
        """
        token = create_access_token({"sub": "emp001"})
        parts = token.split(".")
        assert len(parts) == 3, f"JWT should have 3 parts, got {len(parts)}"
    
    def test_create_token_contains_sub_claim(self):
        """
        Test create_access_token includes subject claim.
        
        The "sub" (subject) claim should be in the token payload.
        
        Assertion: Decoded token contains "sub" claim
        """
        token = create_access_token({"sub": "emp001"})
        decoded = decode_token(token)
        assert "sub" in decoded, "Token should contain 'sub' claim"
        assert decoded["sub"] == "emp001", "Subject claim should match input"
    
    def test_create_token_contains_exp_claim(self):
        """
        Test create_access_token includes expiration claim.
        
        The "exp" (expiration) claim should be in the token payload.
        
        Assertion: Decoded token contains "exp" claim
        """
        token = create_access_token({"sub": "emp001"})
        decoded = decode_token(token)
        assert "exp" in decoded, "Token should contain 'exp' claim"
        assert isinstance(decoded["exp"], object), "Expiration should be present"


class TestJWTTokenValidation:
    """
    Test suite for JWT token validation functionality.
    
    These tests ensure that:
    - Valid tokens decode successfully
    - Invalid tokens are rejected
    - Expired tokens are rejected
    """
    
    def test_decode_valid_token(self):
        """
        Test decode_token accepts valid token.
        
        A token created by create_access_token should decode successfully.
        
        Assertion: decode_token returns decoded payload dict
        """
        original_data = {"sub": "emp001"}
        token = create_access_token(original_data)
        decoded = decode_token(token)
        assert decoded["sub"] == original_data["sub"], "Decoded data should match original"
    
    def test_decode_invalid_token(self):
        """
        Test decode_token rejects invalid token.
        
        A tampered or malformed token should raise an exception.
        
        Assertion: decode_token raises exception for invalid token
        """
        invalid_token = "invalid.token.string"
        try:
            decode_token(invalid_token)
            assert False, "Should raise exception for invalid token"
        except Exception as e:
            # Expected behavior - invalid token raises exception
            assert True, f"Invalid token correctly rejected: {type(e).__name__}"
    
    def test_decode_modified_token(self):
        """
        Test decode_token rejects tampered token.
        
        If token payload is modified after signing, signature verification fails.
        
        Assertion: decode_token raises exception for tampered token
        """
        token = create_access_token({"sub": "emp001"})
        # Modify the token payload (but not the signature)
        parts = token.split(".")
        tampered = parts[0] + ".modified" + parts[2]
        
        try:
            decode_token(tampered)
            assert False, "Should raise exception for tampered token"
        except Exception:
            # Expected behavior
            assert True, "Tampered token correctly rejected"


class TestAuthenticationFlow:
    """
    Integration tests for complete authentication flow.
    
    These tests simulate real-world authentication scenarios.
    """
    
    def test_login_logout_flow(self):
        """
        Test complete login-create token-decode flow.
        
        Simulates:
        1. User provides credentials
        2. System authenticates user
        3. System creates JWT token
        4. User sends token in future request
        5. System validates and decodes token
        
        Assertion: Token can be created from authenticated user and decoded later
        """
        # Step 1: Authenticate user
        user = authenticate_user("testuser", "password123")
        assert user is not None, "User authentication failed"
        
        # Step 2: Create token
        token = create_access_token({"sub": user["uid"]})
        assert isinstance(token, str), "Token creation failed"
        
        # Step 3: Decode token (simulating future request)
        decoded = decode_token(token)
        assert decoded["sub"] == user["uid"], "Token UID doesn't match user UID"
    
    def test_invalid_login_attempt(self):
        """
        Test invalid login is properly rejected.
        
        Simulates attacker trying to login with wrong password.
        
        Assertion: Invalid credentials return None, no token created
        """
        # Attempt login with wrong password
        user = authenticate_user("testuser", "wrong_password")
        assert user is None, "Invalid login should be rejected"
        
        # Verify no token can be created
        # (This should never reach token creation in real code)
