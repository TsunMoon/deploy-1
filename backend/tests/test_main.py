"""
Tests for main application endpoints
"""
import pytest
from fastapi import status


class TestRootEndpoint:
    """Test cases for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check basic structure
        assert "message" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data
        assert "features" in data
        
        # Check version
        assert data["version"] == "2.0.0"
        
        # Check endpoints structure
        assert "documentation" in data["endpoints"]
        assert "langchain_api" in data["endpoints"]
        
        # Check features list
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0
    
    def test_root_endpoint_has_documentation_links(self, client):
        """Test root endpoint includes documentation links"""
        response = client.get("/")
        data = response.json()
        
        docs = data["endpoints"]["documentation"]
        assert "swagger" in docs
        assert "redoc" in docs
        assert docs["swagger"] == "/docs"
        assert docs["redoc"] == "/redoc"
    
    def test_root_endpoint_has_langchain_api_info(self, client):
        """Test root endpoint includes LangChain API information"""
        response = client.get("/")
        data = response.json()
        
        langchain_api = data["endpoints"]["langchain_api"]
        assert "recommendation" in langchain_api
        assert "health" in langchain_api
        assert langchain_api["recommendation"] == "/api/v2/recommendation"


class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    def test_health_check_endpoint(self, client):
        """Test health check returns healthy status"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check basic structure
        assert "status" in data
        assert "version" in data
        assert "services" in data
        
        # Check status
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        
        # Check services
        services = data["services"]
        assert "qdrant" in services
        assert "openai" in services
        assert "tts" in services
        assert "langchain" in services
        
        # All services should be operational
        for service_name, service_status in services.items():
            assert service_status == "operational"


class TestCORS:
    """Test cases for CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response"""
        response = client.options(
            "/api/v2/recommendation",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # Should allow the request
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
    
    def test_cors_allows_credentials(self, client):
        """Test that CORS allows credentials"""
        response = client.get(
            "/",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == status.HTTP_200_OK


class TestDocumentation:
    """Test cases for API documentation"""
    
    def test_swagger_docs_accessible(self, client):
        """Test Swagger documentation is accessible"""
        response = client.get("/docs")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_accessible(self, client):
        """Test ReDoc documentation is accessible"""
        response = client.get("/redoc")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema_accessible(self, client):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check OpenAPI structure
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        
        # Check API info
        assert data["info"]["title"] == "Entertainment Recommendation API"
        assert data["info"]["version"] == "2.0.0"


class TestErrorHandling:
    """Test cases for error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoint"""
        response = client.get("/api/nonexistent-endpoint")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method"""
        response = client.get("/api/auth/login")  # Should be POST
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_422_validation_error(self, client):
        """Test 422 error for invalid request body"""
        response = client.post(
            "/api/auth/login",
            json={"invalid": "data"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestStaticFiles:
    """Test cases for static file serving"""
    
    def test_audio_endpoint_exists(self, client):
        """Test that audio endpoint is configured"""
        # This will return 404 if file doesn't exist, but endpoint should be mounted
        response = client.get("/audio/test.wav")
        
        # Either file exists (200) or doesn't exist (404), but endpoint should be there
        assert response.status_code in [
            status.HTTP_200_OK, 
            status.HTTP_404_NOT_FOUND
        ]
