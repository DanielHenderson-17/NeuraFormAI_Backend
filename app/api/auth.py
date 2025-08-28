"""
Authentication API endpoints for NeuraFormAI
Handles OAuth login, user registration, and session management
"""

from datetime import date
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator, ValidationError
import logging

from app.services.auth_service import oauth_service, AuthProvider
from app.services.user_service import UserProfile
import aiohttp

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response Models
class OAuthLoginRequest(BaseModel):
    provider: str  # "google", "facebook", "apple"
    token: str
    device_info: Optional[Dict[str, Any]] = None

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_info: Optional[Dict[str, Any]] = None

class GoogleTokenExchangeRequest(BaseModel):
    authorization_code: str
    redirect_uri: str

class UserRegistrationRequest(BaseModel):
    provider: str
    provider_user_id: str
    first_name: str
    last_name: str
    email: EmailStr
    birthdate: date
    avatar_url: Optional[str] = None
    timezone: Optional[str] = "UTC"
    language_preference: Optional[str] = "en"
    
    @validator('provider')
    def validate_provider(cls, v):
        if v not in ['google', 'facebook', 'apple']:
            raise ValueError('Provider must be google, facebook, or apple')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('birthdate')
    def validate_birthdate(cls, v):
        # Check if user is at least 13 years old (COPPA compliance)
        from datetime import date
        min_age = date.today().replace(year=date.today().year - 13)
        if v > min_age:
            raise ValueError('User must be at least 13 years old')
        return v

class EmailRegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    birthdate: date
    timezone: Optional[str] = "UTC"
    language_preference: Optional[str] = "en"
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('birthdate')
    def validate_birthdate(cls, v):
        # Check if user is at least 13 years old (COPPA compliance)
        from datetime import date
        min_age = date.today().replace(year=date.today().year - 13)
        if v > min_age:
            raise ValueError('User must be at least 13 years old')
        return v

class LoginResponse(BaseModel):
    success: bool
    user: Optional[UserProfile] = None
    session_token: Optional[str] = None
    message: Optional[str] = None
    requires_registration: bool = False
    token_email: Optional[str] = None
    token_sub: Optional[str] = None
    token_first_name: Optional[str] = None
    token_last_name: Optional[str] = None
    token_picture: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    avatar_url: Optional[str] = None
    timezone: str
    language_preference: str
    auth_provider: Optional[str] = None
    terms_accepted_at: Optional[str] = None
    privacy_policy_accepted_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language_preference: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    ui_preferences: Optional[Dict[str, Any]] = None

# Dependency to get current user from session
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Get current user from session token"""
    session_token = credentials.credentials
    
    user = await oauth_service.validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    return user

@router.post("/login/oauth", response_model=LoginResponse)
async def oauth_login(request: OAuthLoginRequest):
    """OAuth login endpoint"""
    try:
        provider = AuthProvider(request.provider)
        
        # Authenticate with the specified provider
        if provider == AuthProvider.GOOGLE:
            success, user, message = await oauth_service.authenticate_google(request.token)
        elif provider == AuthProvider.FACEBOOK:
            success, user, message = await oauth_service.authenticate_facebook(request.token)
        elif provider == AuthProvider.APPLE:
            success, user, message = await oauth_service.authenticate_apple(request.token)
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")
        
        if success and user:
            # User exists, create session
            session_token = await oauth_service.create_session(
                user.id, 
                request.device_info
            )
            
            # Track login event
            await oauth_service.track_analytics_event(
                user.id, 
                "user_login", 
                {"provider": provider.value, "device_info": request.device_info}
            )
            
            return LoginResponse(
                success=True,
                user=user,
                session_token=session_token
            )
        
        elif message == "additional_info_required" or (isinstance(message, dict) and message.get("message") == "additional_info_required"):
            # User doesn't exist, needs to register
            if isinstance(message, dict):
                # Return the user data for registration
                return LoginResponse(
                    success=False,
                    message="User registration required",
                    requires_registration=True,
                    **{k: v for k, v in message.items() if k not in ["message", "requires_registration"]}
                )
            else:
                return LoginResponse(
                    success=False,
                    message="User registration required",
                    requires_registration=True
                )
        
        else:
            # Authentication failed
            return LoginResponse(
                success=False,
                message=message
            )
    
    except Exception as e:
        logger.error(f"OAuth login failed: {e}")
        # Return error detail to aid debugging (temporary; tighten in production)
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.post("/login", response_model=LoginResponse)
async def email_login(request: EmailLoginRequest):
    """Email/password login endpoint"""
    try:
        from app.services.user_service import user_service, AuthProvider
        
        # Verify password
        user = await user_service.verify_password(request.email, request.password)
        
        if not user:
            return LoginResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Create session
        session_token = await oauth_service.create_session(
            user.id, 
            request.device_info or {}
        )
        
        # Track login event
        await oauth_service.track_analytics_event(
            user.id, 
            "user_login", 
            {"provider": "email", "device_info": request.device_info}
        )
        
        return LoginResponse(
            success=True,
            user=user,
            session_token=session_token
        )
            
    except Exception as e:
        logger.error(f"Email login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/exchange-google-token")
async def exchange_google_token(request: GoogleTokenExchangeRequest):
    """Securely exchange Google authorization code for ID token using backend credentials"""
    try:
        import os
        from google.auth.transport import requests
        from google.oauth2 import id_token
        
        # Get Google client credentials from environment (secure)
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not google_client_id or not google_client_secret:
            logger.error("Google client credentials not configured")
            raise HTTPException(status_code=500, detail="OAuth configuration error")
        
        # Exchange authorization code for tokens
        async with aiohttp.ClientSession() as session:
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'code': request.authorization_code,
                'client_id': google_client_id,
                'client_secret': google_client_secret,
                'redirect_uri': request.redirect_uri,
                'grant_type': 'authorization_code',
            }
            
            async with session.post(token_url, data=token_data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Google token exchange failed: {response.status} - {error_text}")
                    raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
                
                token_response = await response.json()
                id_token = token_response.get('id_token')
                
                if not id_token:
                    logger.error("No ID token in Google response")
                    raise HTTPException(status_code=400, detail="No ID token received")
                
                # Verify the ID token
                try:
                    from google.auth.transport import requests
                    from google.oauth2 import id_token as google_id_token
                    
                    idinfo = google_id_token.verify_oauth2_token(
                        id_token,
                        requests.Request(),
                        google_client_id,
                        clock_skew_in_seconds=60,
                    )
                    logger.info(f"Google ID token verified for user: {idinfo.get('email')}")
                except Exception as e:
                    logger.error(f"Google ID token verification failed: {e}")
                    raise HTTPException(status_code=400, detail="Invalid ID token")
                
                return {"id_token": id_token}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google token exchange failed: {e}")
        raise HTTPException(status_code=500, detail="Token exchange failed")

@router.post("/register/oauth", response_model=LoginResponse)
async def oauth_register_user(request: UserRegistrationRequest):
    """Register a new user from OAuth"""
    try:
        provider = AuthProvider(request.provider)
        
        # Create user
        user = await oauth_service.create_user_from_oauth(
            provider=provider,
            provider_user_id=request.provider_user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            birthdate=request.birthdate,
            avatar_url=request.avatar_url,
            timezone=request.timezone,
            language_preference=request.language_preference
        )
        
        # Create session
        session_token = await oauth_service.create_session(user.id)
        
        # Track registration event
        await oauth_service.track_analytics_event(
            user.id, 
            "user_registration", 
            {"provider": provider.value}
        )
        
        return LoginResponse(
            success=True,
            user=user,
            session_token=session_token
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        # Return the error message to help diagnose setup issues (temporary; tighten in prod)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/register", response_model=LoginResponse)
async def email_register_user(request: EmailRegistrationRequest):
    """Register a new user with email/password"""
    logger.info("=== REGISTRATION ENDPOINT CALLED ===")
    logger.info(f"Request data: {request}")
    try:
        from app.services.user_service import user_service, AuthProvider
        
        # Debug logging
        logger.info(f"Registration request received: email={request.email}, first_name={request.first_name}, last_name={request.last_name}, birthdate={request.birthdate}")
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create user with email authentication
        user = await user_service.create_user(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            birthdate=request.birthdate,
            auth_provider=AuthProvider.EMAIL,
            auth_provider_id=None,
            timezone=request.timezone,
            language_preference=request.language_preference,
            password=request.password
        )
        
        # Create session
        session_token = await oauth_service.create_session(user.id)
        
        # Track registration event
        await oauth_service.track_analytics_event(
            user.id, 
            "user_registration", 
            {"provider": "email"}
        )
        
        return LoginResponse(
            success=True,
            user=user,
            session_token=session_token
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error in registration: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Email registration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user profile"""
    try:
        return UserProfileResponse(
            id=str(current_user.id) if current_user.id is not None else "",
            first_name=current_user.first_name or "",
            last_name=current_user.last_name or "",
            email=current_user.email or "",
            avatar_url=current_user.avatar_url,
            timezone=current_user.timezone or "UTC",
            language_preference=current_user.language_preference or "en",
            auth_provider=current_user.auth_provider.value if current_user.auth_provider else None,
            terms_accepted_at=current_user.terms_accepted_at.isoformat() if current_user.terms_accepted_at else None,
            privacy_policy_accepted_at=current_user.privacy_policy_accepted_at.isoformat() if current_user.privacy_policy_accepted_at else None,
            created_at=current_user.created_at.isoformat() if current_user.created_at else None,
            updated_at=current_user.updated_at.isoformat() if current_user.updated_at else None
        )
    except Exception as e:
        logger.error(f"Failed to serialize profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile serialization failed: {str(e)}")

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update user profile"""
    try:
        # Filter out None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        updated_user = await oauth_service.user_service.update_user_profile(
            current_user.id,
            **updates
        )
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Track profile update event
        await oauth_service.track_analytics_event(
            current_user.id, 
            "profile_updated", 
            {"updated_fields": list(updates.keys())}
        )
        
        return UserProfileResponse(
            id=updated_user.id,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            email=updated_user.email,
            avatar_url=updated_user.avatar_url,
            timezone=updated_user.timezone,
            language_preference=updated_user.language_preference,
            auth_provider=updated_user.auth_provider.value if updated_user.auth_provider else None,
            terms_accepted_at=updated_user.terms_accepted_at.isoformat() if updated_user.terms_accepted_at else None,
            privacy_policy_accepted_at=updated_user.privacy_policy_accepted_at.isoformat() if updated_user.privacy_policy_accepted_at else None,
            created_at=updated_user.created_at.isoformat() if updated_user.created_at else None,
            updated_at=updated_user.updated_at.isoformat() if updated_user.updated_at else None
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")

@router.post("/accept-terms")
async def accept_terms_and_privacy(current_user: UserProfile = Depends(get_current_user)):
    """Accept terms of service and privacy policy"""
    try:
        success = await oauth_service.user_service.accept_terms_and_privacy(current_user.id)
        
        if success:
            # Track terms acceptance event
            await oauth_service.track_analytics_event(
                current_user.id, 
                "terms_accepted"
            )
            
            return {"success": True, "message": "Terms and privacy policy accepted"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    except Exception as e:
        logger.error(f"Terms acceptance failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to accept terms")

@router.post("/logout")
async def logout(current_user: UserProfile = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user and invalidate session"""
    try:
        session_token = credentials.credentials
        success = await oauth_service.invalidate_session(session_token)
        
        if success:
            # Track logout event
            await oauth_service.track_analytics_event(
                current_user.id, 
                "user_logout"
            )
            
            return {"success": True, "message": "Logged out successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.delete("/account")
async def delete_account(current_user: UserProfile = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Deactivate user account"""
    try:
        # Invalidate all sessions first
        session_token = credentials.credentials
        await oauth_service.invalidate_session(session_token)
        
        # Deactivate user account
        success = await oauth_service.user_service.deactivate_user(current_user.id)
        
        if success:
            # Track account deletion event
            await oauth_service.track_analytics_event(
                current_user.id, 
                "account_deleted"
            )
            
            return {"success": True, "message": "Account deactivated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    except Exception as e:
        logger.error(f"Account deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate account")

@router.get("/sessions")
async def get_active_sessions(current_user: UserProfile = Depends(get_current_user)):
    """Get user's active sessions"""
    try:
        query = """
            SELECT id, device_info, created_at, last_activity_at, expires_at
            FROM public.user_sessions
            WHERE user_id = $1 AND is_active = true AND expires_at > NOW()
            ORDER BY last_activity_at DESC
        """
        
        sessions = await oauth_service.db.fetch(query, current_user.id)
        return {"sessions": [dict(session) for session in sessions]}
    
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sessions")

@router.delete("/sessions/{session_id}")
async def invalidate_session_by_id(session_id: str, current_user: UserProfile = Depends(get_current_user)):
    """Invalidate a specific session"""
    try:
        query = """
            UPDATE public.user_sessions 
            SET is_active = false 
            WHERE id = $1 AND user_id = $2
            RETURNING id
        """
        
        result = await oauth_service.db.fetchrow(query, session_id, current_user.id)
        
        if result:
            return {"success": True, "message": "Session invalidated"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    except Exception as e:
        logger.error(f"Failed to invalidate session: {e}")
        raise HTTPException(status_code=500, detail="Failed to invalidate session") 