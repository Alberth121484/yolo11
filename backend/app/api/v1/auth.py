"""
Authentication endpoints
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from starlette.config import Config
from app.auth.oauth import oauth
from app.auth.jwt import create_access_token, get_current_user
from pydantic import BaseModel
from typing import Optional
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory user storage (replace with database in production)
users_db = {
    "admin": {
        "id": "admin",
        "email": "admin@admin.com",
        "name": "Administrador",
        "password": "admin123",  # In production, use hashed passwords
        "avatar_url": None,
        "provider": "local"
    }
}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    provider: str


class LoginCredentials(BaseModel):
    email: str
    password: str


@router.get("/login/{provider}")
async def login(provider: str, request: Request):
    """
    Initiate OAuth login
    Supported providers: google, github, facebook
    """
    if provider not in ['google', 'github', 'facebook']:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    # Set redirect URI
    redirect_uri = f"{request.base_url}api/v1/auth/callback/{provider}"
    
    try:
        return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)
    except Exception as e:
        logger.error(f"OAuth login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback/{provider}")
async def auth_callback(provider: str, request: Request):
    """OAuth callback endpoint"""
    try:
        # Get access token
        token = await oauth.create_client(provider).authorize_access_token(request)
        
        # Get user info based on provider
        if provider == 'google':
            user_info = token.get('userinfo')
            user_data = {
                'id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'avatar_url': user_info.get('picture'),
                'provider': 'google',
                'provider_id': user_info['sub']
            }
        
        elif provider == 'github':
            resp = await oauth.github.get('user', token=token)
            user_info = resp.json()
            user_data = {
                'id': str(user_info['id']),
                'email': user_info.get('email', ''),
                'name': user_info.get('name', user_info.get('login', '')),
                'avatar_url': user_info.get('avatar_url'),
                'provider': 'github',
                'provider_id': str(user_info['id'])
            }
        
        elif provider == 'facebook':
            resp = await oauth.facebook.get('me?fields=id,name,email,picture', token=token)
            user_info = resp.json()
            user_data = {
                'id': user_info['id'],
                'email': user_info.get('email', ''),
                'name': user_info.get('name', ''),
                'avatar_url': user_info.get('picture', {}).get('data', {}).get('url'),
                'provider': 'facebook',
                'provider_id': user_info['id']
            }
        
        # Store user (in production, save to database)
        user_id = user_data['id']
        users_db[user_id] = user_data
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user_id, "email": user_data['email']})
        
        # Redirect to frontend with token
        frontend_url = f"http://localhost:3000/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)
    
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        # Redirect to frontend with error
        return RedirectResponse(url=f"http://localhost:3000/auth/error?message={str(e)}")


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    user_id = current_user.get("sub")
    user = users_db.get(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove password from response
    user_response = {k: v for k, v in user.items() if k != 'password'}
    return UserInfo(**user_response)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    # In production, invalidate token in database
    return {"message": "Logged out successfully"}


@router.post("/login/credentials", response_model=TokenResponse)
async def login_credentials(credentials: LoginCredentials):
    """Login with email and password"""
    # Find user by email
    user = None
    user_id = None
    for uid, user_data in users_db.items():
        if user_data.get("email") == credentials.email:
            user = user_data
            user_id = uid
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Verify password (in production, use password hashing)
    if user.get("password") != credentials.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user_id, "email": user['email']})
    
    # Remove password from response
    user_response = {k: v for k, v in user.items() if k != 'password'}
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )
