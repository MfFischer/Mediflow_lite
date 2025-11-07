"""
Security-focused tests for authentication and authorization.
"""
import pytest
from fastapi import status
from app.core.security import create_access_token, decode_token, get_password_hash, verify_password
from datetime import timedelta


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hash_and_verify(self):
        """Test that password hashing and verification works."""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)
    
    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTTokens:
    """Test JWT token creation and validation."""
    
    def test_create_and_decode_access_token(self):
        """Test access token creation and decoding."""
        data = {"sub": "testuser", "role": "doctor"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "doctor"
        assert decoded["type"] == "access"
    
    def test_expired_token_raises_error(self):
        """Test that expired tokens are rejected."""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(Exception):
            decode_token(token)
    
    def test_invalid_token_raises_error(self):
        """Test that invalid tokens are rejected."""
        with pytest.raises(Exception):
            decode_token("invalid.token.here")


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    def test_login_with_valid_credentials(self, client, db_session):
        """Test login with valid credentials."""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Create test user
        user = User(
            username="testdoctor",
            email="doctor@test.com",
            hashed_password=get_password_hash("password123"),
            role="doctor"
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testdoctor", "password": "password123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_with_invalid_credentials(self, client, db_session):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "wrongpass"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/patients/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_access_protected_endpoint_with_valid_token(self, client, db_session):
        """Test accessing protected endpoint with valid token."""
        from app.models.user import User
        from app.core.security import get_password_hash, create_access_token
        
        # Create test user
        user = User(
            username="testdoctor",
            email="doctor@test.com",
            hashed_password=get_password_hash("password123"),
            role="doctor"
        )
        db_session.add(user)
        db_session.commit()
        
        # Create token
        token = create_access_token({"sub": "testdoctor", "role": "doctor"})
        
        response = client.get(
            "/api/v1/patients/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK


class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def test_admin_can_access_user_management(self, client, db_session):
        """Test that admin can access user management."""
        from app.models.user import User
        from app.core.security import get_password_hash, create_access_token
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@test.com",
            hashed_password=get_password_hash("admin123"),
            role="admin"
        )
        db_session.add(admin)
        db_session.commit()
        
        token = create_access_token({"sub": "admin", "role": "admin"})
        
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_doctor_cannot_access_user_management(self, client, db_session):
        """Test that doctor cannot access user management."""
        from app.models.user import User
        from app.core.security import get_password_hash, create_access_token
        
        # Create doctor user
        doctor = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=get_password_hash("doctor123"),
            role="doctor"
        )
        db_session.add(doctor)
        db_session.commit()
        
        token = create_access_token({"sub": "doctor", "role": "doctor"})
        
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_attempt(self, client, db_session):
        """Test that SQL injection attempts are blocked."""
        from app.models.user import User
        from app.core.security import get_password_hash, create_access_token
        
        user = User(
            username="testuser",
            email="test@test.com",
            hashed_password=get_password_hash("password123"),
            role="doctor"
        )
        db_session.add(user)
        db_session.commit()
        
        token = create_access_token({"sub": "testuser", "role": "doctor"})
        
        # Attempt SQL injection in search parameter
        response = client.get(
            "/api/v1/patients/?search=' OR '1'='1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should not cause error, should be treated as normal search
        assert response.status_code == status.HTTP_200_OK
    
    def test_xss_attempt_in_patient_data(self, client, db_session):
        """Test that XSS attempts are sanitized."""
        from app.models.user import User
        from app.core.security import get_password_hash, create_access_token
        
        user = User(
            username="testuser",
            email="test@test.com",
            hashed_password=get_password_hash("password123"),
            role="doctor"
        )
        db_session.add(user)
        db_session.commit()
        
        token = create_access_token({"sub": "testuser", "role": "doctor"})
        
        # Attempt XSS in patient name
        response = client.post(
            "/api/v1/patients/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "first_name": "<script>alert('xss')</script>",
                "last_name": "Test",
                "date_of_birth": "1990-01-01",
                "email": "test@example.com",
                "phone_number": "+639171234567"
            }
        )
        
        # Should be rejected by validation
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]

