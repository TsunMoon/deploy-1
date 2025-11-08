# Backend Testing Documentation

## Overview
Testing system for Entertainment Recommendation API Backend using pytest and FastAPI TestClient.

## Testing Structure

```
tests/
├── __init__.py                      # Package initialization
├── conftest.py                      # Pytest fixtures and configuration
├── test_main.py                     # Tests cho main app endpoints
├── test_auth.py                     # Tests cho authentication
├── test_langchain_endpoints.py      # Tests cho LangChain API endpoints
├── test_services.py                 # Tests for services
└── README.md                        # This documentation
```

## Installing Dependencies

Install required packages for testing:

```bash
pip install pytest pytest-asyncio httpx pytest-cov pytest-mock
```

Or add to `requirements.txt`:
```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
pytest-cov==4.1.0
pytest-mock==3.12.0
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with detailed output
```bash
pytest -v
```

### Run tests for a specific file
```bash
pytest tests/test_auth.py
pytest tests/test_langchain_endpoints.py
```

### Run tests for a specific class
```bash
pytest tests/test_auth.py::TestAuthLogin
```

### Run a specific test
```bash
pytest tests/test_auth.py::TestAuthLogin::test_login_successful
```

### Run tests with coverage report
```bash
pytest --cov=. --cov-report=html --cov-report=term-missing
```

### Run tests with markers
```bash
pytest -m unit           # Only unit tests
pytest -m integration    # Only integration tests
pytest -m api           # Only API tests
```

## Test Categories

### 1. Authentication Tests (`test_auth.py`)
- ✅ Login with valid credentials
- ✅ Login with invalid credentials
- ✅ Validation errors (missing fields, invalid format)
- ✅ Logout functionality
- ✅ Complete login/logout flow

**Run:**
```bash
pytest tests/test_auth.py -v
```

### 2. Main Application Tests (`test_main.py`)
- ✅ Root endpoint and API information
- ✅ Health check endpoint
- ✅ CORS configuration
- ✅ API documentation (Swagger, ReDoc)
- ✅ Error handling (404, 405, 422)
- ✅ Static file serving

**Run:**
```bash
pytest tests/test_main.py -v
```

### 3. LangChain API Tests (`test_langchain_endpoints.py`)
- ✅ Basic recommendation requests
- ✅ Recommendation with audio generation
- ✅ Recommendation with chat history
- ✅ Function calling
- ✅ Film details endpoint
- ✅ Filter by genre endpoint
- ✅ Similar titles endpoint
- ✅ Trending endpoint
- ✅ Memory management (session history, clear memory)
- ✅ Response types information

**Run:**
```bash
pytest tests/test_langchain_endpoints.py -v
```

### 4. Services Tests (`test_services.py`)
- ✅ MemoryService (add, get, clear sessions)
- ✅ LangChainService initialization
- ✅ QdrantService initialization
- ✅ TTSService initialization and audio generation
- ✅ Response templates

**Run:**
```bash
pytest tests/test_services.py -v
```

## Available Fixtures

### Client Fixtures
- `client`: FastAPI TestClient instance

### Service Mocks
- `mock_qdrant_service`: Mocked QdrantService
- `mock_langchain_service`: Mocked LangChainService
- `mock_tts_service`: Mocked TTSService
- `mock_memory_service`: Mocked MemoryService

### Data Fixtures
- `sample_chat_history`: Sample conversation history
- `sample_langchain_request`: Sample API request payload
- `sample_login_credentials`: Sample login credentials

## Coverage Report

After running tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

Open coverage report:
```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

## Best Practices

### 1. Test Organization
- Each test file corresponds to a module/router
- Group related tests in classes
- Name tests descriptively: `test_<action>_<expected_result>`

### 2. Using Fixtures
- Leverage fixtures to avoid code duplication
- Create new fixtures in `conftest.py` if needed
- Use appropriately scoped fixtures (function, class, module, session)

### 3. Mocking
- Mock external dependencies (database, APIs, file system)
- Don't mock the code being tested
- Use `patch` decorator for mocking

### 4. Assertions
- Check status codes
- Check response structure
- Check data types and values
- Test both happy path and error cases

### 5. Test Data
- Use meaningful data, not random
- Create fixtures for complex test data
- Cleanup after each test if needed

## Continuous Integration

### GitHub Actions Example
```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Troubleshooting

### Import Errors
If you encounter import errors, ensure:
- PYTHONPATH is set correctly
- `conftest.py` adds parent directory to sys.path
- Run tests from backend directory

### Async Tests
If testing async functions, use:
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Mock Issues
If mocks don't work, check:
- Patch path is correct (import path, not file path)
- Mock is applied before code runs
- Fixtures are injected in correct order

## Next Steps

1. **Add Integration Tests**: Test with real database and services
2. **Performance Tests**: Test response times and throughput
3. **Security Tests**: Test authentication and authorization
4. **Load Tests**: Use locust or pytest-benchmark

## Contact

If you have issues or questions about testing, please create an issue or contact the team.
