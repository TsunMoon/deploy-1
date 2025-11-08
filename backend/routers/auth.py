from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Mock database
MOCK_DATABASE = {
    "congdanh.official@gmail.com": {
        "id": "user-123456",
        "email": "congdanh.official@gmail.com",
        "password": "congdanh@123",
        "name": "Cong Danh",
        "role": "admin",
        "profile": {
            "preferences": "Love action-packed movies with intense fight scenes, anime with deep storylines, mind-bending thrillers, and sci-fi that explores complex concepts",
            "favorite_genres": ["action", "anime", "thriller", "sci-fi", "martial arts"],
            "disliked_genres": ["slow-paced drama", "musical"],
            "favorite_actors": ["Tom Cruise", "Keanu Reeves", "Leonardo DiCaprio"],
            "watch_style": "Enjoys intense action sequences, complex storylines, and plot twists",
            "mood_preference": "Prefers fast-paced, adrenaline-pumping content",
            "recently_watched": ["John Wick", "Inception", "The Matrix"],
            "watching_with": "solo",  # solo, family, friends
            "time_available": "2-3 hours",  # for movie length suggestions
            "language_preference": "English, Japanese (anime)"
        }
    },
    "test@example.com": {
        "id": "user-789012",
        "email": "test@example.com",
        "password": "password123",
        "name": "Test User",
        "role": "user",
        "profile": {
            "preferences": "Enjoy light-hearted comedies, romantic movies with happy endings, and emotional dramas",
            "favorite_genres": ["comedy", "romance", "drama", "feel-good"],
            "disliked_genres": ["horror", "extreme violence"],
            "favorite_actors": ["Emma Stone", "Ryan Gosling", "Meryl Streep"],
            "watch_style": "Prefers light-hearted content, emotional stories, and feel-good endings",
            "mood_preference": "Looking for uplifting, heartwarming content",
            "recently_watched": ["La La Land", "The Proposal", "The Notebook"],
            "watching_with": "partner",
            "time_available": "1.5-2 hours",
            "language_preference": "English"
        }
    }
}


class LoginRequest(BaseModel):
    """Request model for login endpoint"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "congdanh.official@gmail.com",
                "password": "congdanh@123"
            }
        }


class LoginResponse(BaseModel):
    """Response model for login endpoint"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User name")
    role: str = Field(..., description="User role")
    accessToken: str = Field(..., description="Access token")
    refreshToken: Optional[str] = Field(None, description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user-123456",
                "email": "congdanh.official@gmail.com",
                "name": "Cong Danh",
                "role": "admin",
                "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class LogoutResponse(BaseModel):
    """Response model for logout endpoint"""
    message: str = Field(..., description="Logout message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Logout successful"
            }
        }


def generate_mock_token(user_id: str, email: str) -> str:
    """Generate a simple mock token (in production, use JWT)"""
    import base64
    import json
    from datetime import datetime
    
    payload = {
        "id": user_id,
        "email": email,
        "iat": datetime.now().timestamp()
    }
    token_data = base64.b64encode(json.dumps(payload).encode()).decode()
    return f"mock_token_{token_data}"


def get_user_profile(user_id: str) -> Optional[Dict]:
    """Get user profile from MOCK_DATABASE by user ID"""
    for email, user_data in MOCK_DATABASE.items():
        if user_data.get("id") == user_id:
            return user_data.get("profile")
    return None


def get_user_profile_by_email(email: str) -> Optional[Dict]:
    """Get user profile from MOCK_DATABASE by email"""
    user = MOCK_DATABASE.get(email.lower())
    if user:
        return user.get("profile")
    return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get full user data from MOCK_DATABASE by user ID"""
    for email, user_data in MOCK_DATABASE.items():
        if user_data.get("id") == user_id:
            return user_data
    return None


@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """
    Get user profile information
    
    Returns user profile data including preferences, favorite genres, etc.
    Used by frontend to display user preferences and by AI for personalization.
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "profile": user.get("profile", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile"""
    preferences: Optional[str] = Field(None, description="User preferences")
    favorite_genres: Optional[List[str]] = Field(None, description="Favorite genres")
    disliked_genres: Optional[List[str]] = Field(None, description="Disliked genres")
    favorite_actors: Optional[List[str]] = Field(None, description="Favorite actors")
    watch_style: Optional[str] = Field(None, description="Watch style")
    mood_preference: Optional[str] = Field(None, description="Mood preference")
    recently_watched: Optional[List[str]] = Field(None, description="Recently watched")
    watching_with: Optional[str] = Field(None, description="Watching with")
    time_available: Optional[str] = Field(None, description="Time available")
    language_preference: Optional[str] = Field(None, description="Language preference")


@router.put("/profile/{user_id}")
async def update_profile(user_id: str, request: UpdateProfileRequest):
    """
    Update user profile information
    
    Allows users to customize their preferences for personalized recommendations.
    """
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update profile with new values (only update provided fields)
        profile = user.get("profile", {})
        
        update_data = request.model_dump(exclude_none=True)
        profile.update(update_data)
        
        # Update in MOCK_DATABASE
        for email, user_data in MOCK_DATABASE.items():
            if user_data.get("id") == user_id:
                user_data["profile"] = profile
                break
        
        logger.info(f"Profile updated for user {user_id}")
        
        return {
            "message": "Profile updated successfully",
            "profile": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint with mock authentication
    
    Mock credentials:
    - Email: congdanh.official@gmail.com, Password: congdanh@123
    - Email: test@example.com, Password: password123
    """
    try:
        logger.info(f"Login attempt for email: {request.email}")
        
        # Check if user exists in mock database
        user = MOCK_DATABASE.get(request.email.lower())
        
        if not user or user["password"] != request.password:
            logger.warning(f"Invalid credentials for email: {request.email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        # Generate mock tokens
        access_token = generate_mock_token(user["id"], user["email"])
        refresh_token = generate_mock_token(user["id"], user["email"])
        
        logger.info(f"Login successful for user: {user['email']}")
        
        return LoginResponse(
            id=user["id"],
            email=user["email"],
            name=user.get("name"),
            role=user["role"],
            accessToken=access_token,
            refreshToken=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout():
    """
    Logout endpoint
    In a real application, this would invalidate tokens on the server
    """
    try:
        logger.info("Logout request received")
        return LogoutResponse(message="Logout successful")
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )

