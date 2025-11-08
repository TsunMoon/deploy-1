"""
Tests for authentication endpoints
"""
from fastapi import status

class TestAuthLogin:
    """Test cases for /api/auth/login endpoint"""
    
    def test_login_successful(self, client, sample_login_credentials):
        """Test successful login with valid credentials"""
        response = client.post(
            "/api/auth/login",
            json=sample_login_credentials["valid"]
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert "email" in data
        assert "name" in data
        assert "role" in data
        assert "accessToken" in data
        assert "refreshToken" in data
        
        # Check specific values
        assert data["email"] == sample_login_credentials["valid"]["email"]
        assert data["role"] in ["admin", "user"]
        assert len(data["accessToken"]) > 0
    
    def test_login_invalid_credentials(self, client, sample_login_credentials):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login",
            json=sample_login_credentials["invalid"]
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert "Invalid email or password" in data["detail"]
    
    def test_login_missing_email(self, client):
        """Test login with missing email field"""
        response = client.post(
            "/api/auth/login",
            json={"password": "somepassword"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self, client):
        """Test login with missing password field"""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "not-an-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_empty_password(self, client):
        """Test login with empty password"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": ""
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_test_user(self, client):
        """Test login with test user credentials"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"


class TestAuthLogout:
    """Test cases for /api/auth/logout endpoint"""
    
    def test_logout_successful(self, client):
        """Test successful logout"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert data["message"] == "Logout successful"
    
    def test_logout_without_authentication(self, client):
        """Test logout without authentication (should still work in mock)"""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK


class TestAuthIntegration:
    """Integration tests for authentication flow"""
    
    def test_login_logout_flow(self, client, sample_login_credentials):
        """Test complete login and logout flow"""
        # Login
        login_response = client.post(
            "/api/auth/login",
            json=sample_login_credentials["valid"]
        )
        assert login_response.status_code == status.HTTP_200_OK
        
        # Get token
        token = login_response.json()["accessToken"]
        assert len(token) > 0
        
        # Logout
        logout_response = client.post("/api/auth/logout")
        assert logout_response.status_code == status.HTTP_200_OK
    
    def test_multiple_login_attempts(self, client, sample_login_credentials):
        """Test multiple login attempts with same credentials"""
        for _ in range(3):
            response = client.post(
                "/api/auth/login",
                json=sample_login_credentials["valid"]
            )
            assert response.status_code == status.HTTP_200_OK
            
            # Each login should generate a new token
            data = response.json()
            assert "accessToken" in data
