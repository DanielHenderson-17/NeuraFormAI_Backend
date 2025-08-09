"""
Authentication service for NeuraFormAI
Handles OAuth authentication with Google, Facebook, and Apple
"""

import os
import json
import asyncio
from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple, List
import logging
import aiohttp
from google.auth.transport import requests
from google.oauth2 import id_token
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from app.services.user_service import UserService, AuthProvider, UserProfile
from app.config.database import db

logger = logging.getLogger(__name__)

class OAuthService:
    """OAuth authentication service"""
    
    def __init__(self):
        self.user_service = UserService()
        self.db = db
        
        # OAuth configuration
        # Support multiple Google client IDs (desktop + web). Use comma-separated list in GOOGLE_CLIENT_IDS,
        # or fallback to single GOOGLE_CLIENT_ID.
        google_ids_env = os.getenv('GOOGLE_CLIENT_IDS') or os.getenv('GOOGLE_CLIENT_ID') or ''
        self.google_client_ids: List[str] = [cid.strip() for cid in google_ids_env.split(',') if cid.strip()]
        self.facebook_app_id = os.getenv('FACEBOOK_APP_ID')
        self.facebook_app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.apple_team_id = os.getenv('APPLE_TEAM_ID')
        self.apple_key_id = os.getenv('APPLE_KEY_ID')
        self.apple_private_key = os.getenv('APPLE_PRIVATE_KEY')
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate OAuth configuration"""
        missing_configs = []
        
        if not self.google_client_ids:
            missing_configs.append("GOOGLE_CLIENT_ID or GOOGLE_CLIENT_IDS")
        if not self.facebook_app_id or not self.facebook_app_secret:
            missing_configs.append("FACEBOOK_APP_ID and FACEBOOK_APP_SECRET")
        if not all([self.apple_team_id, self.apple_key_id, self.apple_private_key]):
            missing_configs.append("APPLE_TEAM_ID, APPLE_KEY_ID, and APPLE_PRIVATE_KEY")
        
        if missing_configs:
            logger.warning(f"Missing OAuth configuration: {', '.join(missing_configs)}")
    
    async def authenticate_google(self, id_token_str: str) -> Tuple[bool, Optional[UserProfile], Optional[str]]:
        """Authenticate with Google OAuth"""
        try:
            # Verify the ID token
            # Verify signature and expiry first; check audience manually to support multiple client IDs
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                clock_skew_in_seconds=60,
            )
            aud = idinfo.get('aud')
            if not aud or aud not in self.google_client_ids:
                logger.error(f"Google token audience mismatch. aud={aud}, allowed={self.google_client_ids}")
                return False, None, "Invalid Google token"
            
            # Extract user information
            google_user_id = idinfo['sub']
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            avatar_url = idinfo.get('picture')
            
            # Check if user exists
            user = await self.user_service.get_user_by_auth_provider(AuthProvider.GOOGLE, google_user_id)
            
            if user:
                # User exists, return success
                return True, user, None
            
            # Check if email already exists with different provider
            existing_user = await self.user_service.get_user_by_email(email)
            if existing_user:
                return False, None, f"Email {email} is already registered with {existing_user.auth_provider.value}"
            
            # User doesn't exist, need to collect additional info
            return False, None, "additional_info_required"
            
        except Exception as e:
            logger.error(f"Google authentication failed: {e}")
            # Surface reason to client to aid debugging (token remains server-verified)
            return False, None, f"Google auth error: {str(e)}"
    
    async def authenticate_facebook(self, access_token: str) -> Tuple[bool, Optional[UserProfile], Optional[str]]:
        """Authenticate with Facebook OAuth"""
        try:
            # Verify the access token and get user info
            async with aiohttp.ClientSession() as session:
                # First, verify the token
                verify_url = f"https://graph.facebook.com/debug_token"
                params = {
                    'input_token': access_token,
                    'access_token': f"{self.facebook_app_id}|{self.facebook_app_secret}"
                }
                
                async with session.get(verify_url, params=params) as response:
                    if response.status != 200:
                        return False, None, "Invalid Facebook token"
                    
                    verify_data = await response.json()
                    if not verify_data.get('data', {}).get('is_valid'):
                        return False, None, "Invalid Facebook token"
                
                # Get user information
                user_url = "https://graph.facebook.com/me"
                params = {
                    'access_token': access_token,
                    'fields': 'id,name,email,first_name,last_name,picture'
                }
                
                async with session.get(user_url, params=params) as response:
                    if response.status != 200:
                        return False, None, "Failed to get Facebook user info"
                    
                    user_data = await response.json()
            
            facebook_user_id = user_data['id']
            email = user_data.get('email', '')
            first_name = user_data.get('first_name', '')
            last_name = user_data.get('last_name', '')
            avatar_url = user_data.get('picture', {}).get('data', {}).get('url')
            
            # Check if user exists
            user = await self.user_service.get_user_by_auth_provider(AuthProvider.FACEBOOK, facebook_user_id)
            
            if user:
                return True, user, None
            
            # Check if email already exists with different provider
            if email:
                existing_user = await self.user_service.get_user_by_email(email)
                if existing_user:
                    return False, None, f"Email {email} is already registered with {existing_user.auth_provider.value}"
            
            # User doesn't exist, need to collect additional info
            return False, None, "additional_info_required"
            
        except Exception as e:
            logger.error(f"Facebook authentication failed: {e}")
            return False, None, "Facebook authentication failed"
    
    async def authenticate_apple(self, id_token_str: str) -> Tuple[bool, Optional[UserProfile], Optional[str]]:
        """Authenticate with Apple OAuth"""
        try:
            # Decode the JWT header to get the key ID
            header = jwt.get_unverified_header(id_token_str)
            key_id = header.get('kid')
            
            if not key_id:
                return False, None, "Invalid Apple token format"
            
            # Get Apple's public keys
            async with aiohttp.ClientSession() as session:
                async with session.get('https://appleid.apple.com/auth/keys') as response:
                    if response.status != 200:
                        return False, None, "Failed to get Apple public keys"
                    
                    keys_data = await response.json()
            
            # Find the matching public key
            public_key = None
            for key in keys_data['keys']:
                if key['kid'] == key_id:
                    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not public_key:
                return False, None, "Apple public key not found"
            
            # Verify the token
            payload = jwt.decode(
                id_token_str,
                public_key,
                algorithms=['RS256'],
                audience=self.apple_team_id,
                issuer='https://appleid.apple.com'
            )
            
            apple_user_id = payload['sub']
            email = payload.get('email', '')
            
            # Check if user exists
            user = await self.user_service.get_user_by_auth_provider(AuthProvider.APPLE, apple_user_id)
            
            if user:
                return True, user, None
            
            # Check if email already exists with different provider
            if email:
                existing_user = await self.user_service.get_user_by_email(email)
                if existing_user:
                    return False, None, f"Email {email} is already registered with {existing_user.auth_provider.value}"
            
            # User doesn't exist, need to collect additional info
            return False, None, "additional_info_required"
            
        except Exception as e:
            logger.error(f"Apple authentication failed: {e}")
            return False, None, "Apple authentication failed"
    
    async def create_user_from_oauth(
        self,
        provider: AuthProvider,
        provider_user_id: str,
        first_name: str,
        last_name: str,
        email: str,
        birthdate: date,
        avatar_url: Optional[str] = None,
        **kwargs
    ) -> UserProfile:
        """Create a new user from OAuth authentication"""
        
        try:
            user = await self.user_service.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                birthdate=birthdate,
                auth_provider=provider,
                auth_provider_id=provider_user_id,
                avatar_url=avatar_url,
                **kwargs
            )
            
            logger.info(f"Created user from {provider.value} OAuth: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user from {provider.value} OAuth: {e}")
            raise
    
    async def create_session(self, user_id: str, device_info: Optional[Dict[str, Any]] = None) -> str:
        """Create a new user session"""
        import uuid
        
        session_token = str(uuid.uuid4())
        expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Proactive housekeeping: prune old/expired sessions occasionally
        try:
            await self.prune_old_sessions()
        except Exception as _:
            pass

        query = """
            INSERT INTO public.user_sessions (
                user_id, session_token, device_info, is_active, expires_at
            ) VALUES ($1, $2, $3::jsonb, $4, $5)
            RETURNING id
        """
        
        try:
            import json as _json
            device_info_json = _json.dumps(device_info or {})
            await self.db.execute(query, user_id, session_token, device_info_json, True, expires_at)
            logger.info(f"Created session for user: {user_id}")
            return session_token
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {e}")
            raise
    
    async def validate_session(self, session_token: str) -> Optional[UserProfile]:
        """Validate a session token and return the associated user"""
        query = """
            SELECT u.* FROM public.users u
            JOIN public.user_sessions s ON u.id = s.user_id
            WHERE s.session_token = $1 
            AND s.is_active = true 
            AND s.expires_at > NOW()
            AND u.is_active = true
        """
        
        try:
            result = await self.db.fetchrow(query, session_token)
            if result:
                # Update last activity
                await self.db.execute(
                    "UPDATE public.user_sessions SET last_activity_at = $2 WHERE session_token = $1",
                    session_token, datetime.utcnow()
                )
                return self.user_service._row_to_user_profile(result)
            return None
        except Exception as e:
            logger.error(f"Failed to validate session {session_token}: {e}")
            return None
    
    async def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session token"""
        query = """
            UPDATE public.user_sessions 
            SET is_active = false 
            WHERE session_token = $1
            RETURNING id
        """
        
        try:
            result = await self.db.fetchrow(query, session_token)
            if result:
                logger.info(f"Invalidated session: {session_token}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to invalidate session {session_token}: {e}")
            return False
    
    async def track_analytics_event(
        self, 
        user_id: str, 
        event_type: str, 
        event_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ):
        """Track user analytics event"""
        query = """
            INSERT INTO public.user_analytics (
                user_id, event_type, event_data, session_id
            ) VALUES ($1, $2, $3::jsonb, $4)
        """
        
        try:
            import json as _json
            await self.db.execute(
                query,
                user_id,
                event_type,
                _json.dumps(event_data or {}),
                session_id,
            )
        except Exception as e:
            logger.error(f"Failed to track analytics event for user {user_id}: {e}")

    async def prune_old_sessions(self, retention_days: int = 30) -> None:
        """Delete expired or inactive sessions older than retention window.

        This keeps the user_sessions table from growing indefinitely while
        preserving recent auditability.
        """
        # Safe integer formatting (internal constant)
        days = max(1, int(retention_days))
        cutoff_expr = f"NOW() - INTERVAL '{days} days'"
        query = f"""
            DELETE FROM public.user_sessions
            WHERE expires_at < {cutoff_expr}
               OR (is_active = false AND created_at < {cutoff_expr})
        """
        try:
            await self.db.execute(query)
        except Exception as e:
            logger.error(f"Pruning sessions failed: {e}")

# Global OAuth service instance
oauth_service = OAuthService() 