"""
User service for NeuraFormAI
Handles user authentication, profile management, and OAuth integration
"""

import uuid
from datetime import datetime, date
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
from enum import Enum
import bcrypt

from app.config.database import db

logger = logging.getLogger(__name__)

class AuthProvider(Enum):
    """Supported OAuth providers"""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"
    EMAIL = "email"

@dataclass
class UserProfile:
    """User profile data structure"""
    id: str
    first_name: str
    last_name: str
    email: str
    birthdate: date
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    language_preference: str = "en"
    auth_provider: Optional[AuthProvider] = None
    auth_provider_id: Optional[str] = None
    terms_accepted_at: Optional[datetime] = None
    privacy_policy_accepted_at: Optional[datetime] = None
    is_active: bool = True
    notification_preferences: Dict[str, Any] = None
    ui_preferences: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.notification_preferences is None:
            self.notification_preferences = {}
        if self.ui_preferences is None:
            self.ui_preferences = {}

class UserService:
    """Service for user management and authentication"""
    
    def __init__(self):
        self.db = db
    
    async def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        birthdate: date,
        auth_provider: AuthProvider,
        auth_provider_id: Optional[str] = None,
        avatar_url: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ) -> UserProfile:
        """Create a new user profile"""
        
        # Validate required fields
        if not all([first_name, last_name, email, birthdate]):
            raise ValueError("first_name, last_name, email, and birthdate are required")
        
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Generate user ID (UUID)
        user_id = str(uuid.uuid4())
        
        # Hash password if provided
        password_hash = None
        if password and auth_provider == AuthProvider.EMAIL:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Prepare user data explicitly in the same order as the INSERT columns
        timezone = kwargs.get('timezone', 'UTC')
        language_preference = kwargs.get('language_preference', 'en')
        notification_preferences = kwargs.get('notification_preferences', {})
        ui_preferences = kwargs.get('ui_preferences', {})

        values = [
            user_id,                      # $1  id
            first_name,                   # $2  first_name
            last_name,                    # $3  last_name
            email.lower(),                # $4  email
            password_hash,                # $5  password_hash
            birthdate,                    # $6  birthdate
            auth_provider.value,          # $7  auth_provider
            auth_provider_id,             # $8  auth_provider_id
            avatar_url,                   # $9  avatar_url
            timezone,                     # $10 timezone
            language_preference,          # $11 language_preference
            notification_preferences,     # $12 notification_preferences (JSONB)
            ui_preferences,               # $13 ui_preferences (JSONB)
            True,                         # $14 is_active
            datetime.utcnow(),            # $15 created_at
            datetime.utcnow(),            # $16 updated_at
        ]
        
        # Insert into database
        query = """
            INSERT INTO public.users (
                id, first_name, last_name, email, password_hash, birthdate, auth_provider, 
                auth_provider_id, avatar_url, timezone, language_preference,
                notification_preferences, ui_preferences, is_active, created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12::jsonb, $13::jsonb, $14, $15, $16)
            RETURNING *
        """
        
        try:
            # Ensure JSON types are encoded properly for the database driver
            values[11] = json.dumps(values[11])  # notification_preferences
            values[12] = json.dumps(values[12])  # ui_preferences

            result = await self.db.fetchrow(query, *values)
            logger.info(f"Created user: {email}")
            return self._row_to_user_profile(result)
        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Get user by ID"""
        query = "SELECT * FROM public.users WHERE id = $1 AND is_active = true"
        result = await self.db.fetchrow(query, user_id)
        return self._row_to_user_profile(result) if result else None
    
    async def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email"""
        query = "SELECT * FROM public.users WHERE email = $1 AND is_active = true"
        result = await self.db.fetchrow(query, email.lower())
        return self._row_to_user_profile(result) if result else None
    
    async def get_user_by_auth_provider(self, provider: AuthProvider, provider_id: str) -> Optional[UserProfile]:
        """Get user by OAuth provider ID"""
        query = """
            SELECT * FROM public.users 
            WHERE auth_provider = $1 AND auth_provider_id = $2 AND is_active = true
        """
        result = await self.db.fetchrow(query, provider.value, provider_id)
        return self._row_to_user_profile(result) if result else None
    
    async def verify_password(self, email: str, password: str) -> Optional[UserProfile]:
        """Verify email/password authentication"""
        query = """
            SELECT * FROM public.users 
            WHERE email = $1 AND auth_provider = 'email' AND is_active = true
        """
        result = await self.db.fetchrow(query, email.lower())
        if not result:
            return None
        
        stored_password_hash = result.get('password_hash')
        if not stored_password_hash:
            return None
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            return self._row_to_user_profile(result)
        
        return None
    
    async def update_user_profile(
        self,
        user_id: str,
        **updates
    ) -> Optional[UserProfile]:
        """Update user profile"""
        
        # Build dynamic update query
        allowed_fields = {
            'first_name', 'last_name', 'avatar_url', 'timezone', 
            'language_preference', 'notification_preferences', 'ui_preferences'
        }
        
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}
        if not update_fields:
            raise ValueError("No valid fields to update")
        
        # Build query dynamically
        set_clause = ", ".join([f"{field} = ${i+2}" for i, field in enumerate(update_fields.keys())])
        query = f"""
            UPDATE public.users 
            SET {set_clause}, updated_at = ${len(update_fields) + 2}
            WHERE id = $1 AND is_active = true
            RETURNING *
        """
        
        values = [user_id] + list(update_fields.values()) + [datetime.utcnow()]
        
        try:
            result = await self.db.fetchrow(query, *values)
            if result:
                logger.info(f"Updated user profile: {user_id}")
                return self._row_to_user_profile(result)
            return None
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
    
    async def accept_terms_and_privacy(self, user_id: str) -> bool:
        """Mark user as having accepted terms and privacy policy"""
        query = """
            UPDATE public.users 
            SET terms_accepted_at = $2, privacy_policy_accepted_at = $2, updated_at = $2
            WHERE id = $1 AND is_active = true
            RETURNING id
        """
        
        try:
            result = await self.db.fetchrow(query, user_id, datetime.utcnow())
            if result:
                logger.info(f"User {user_id} accepted terms and privacy policy")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update terms acceptance for user {user_id}: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account"""
        query = """
            UPDATE public.users 
            SET is_active = false, updated_at = $2
            WHERE id = $1
            RETURNING id
        """
        
        try:
            result = await self.db.fetchrow(query, user_id, datetime.utcnow())
            if result:
                logger.info(f"Deactivated user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to deactivate user {user_id}: {e}")
            raise
    
    async def get_user_conversations(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user's conversations with summary"""
        query = """
            SELECT 
                c.id,
                c.title,
                c.summary,
                c.created_at,
                c.updated_at,
                p.name as persona_name,
                p.display_name as persona_display_name,
                p.avatar_url as persona_avatar,
                (SELECT COUNT(*) FROM public.messages WHERE conversation_id = c.id) as message_count
            FROM public.conversations c
            JOIN public.personas p ON c.persona_id = p.id
            WHERE c.user_id = $1 AND c.is_active = true
            ORDER BY c.updated_at DESC
            LIMIT $2 OFFSET $3
        """
        
        try:
            results = await self.db.fetch(query, user_id, limit, offset)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get conversations for user {user_id}: {e}")
            raise
    
    async def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get user analytics for the specified period"""
        query = """
            SELECT 
                event_type,
                COUNT(*) as event_count,
                DATE(created_at) as event_date
            FROM public.user_analytics
            WHERE user_id = $1 
            AND created_at >= NOW() - INTERVAL '$2 days'
            GROUP BY event_type, DATE(created_at)
            ORDER BY event_date DESC, event_count DESC
        """
        
        try:
            results = await self.db.fetch(query, user_id, days)
            
            analytics = {
                'total_events': sum(row['event_count'] for row in results),
                'events_by_type': {},
                'events_by_date': {}
            }
            
            for row in results:
                event_type = row['event_type']
                event_count = row['event_count']
                event_date = row['event_date'].isoformat()
                
                # Group by event type
                if event_type not in analytics['events_by_type']:
                    analytics['events_by_type'][event_type] = 0
                analytics['events_by_type'][event_type] += event_count
                
                # Group by date
                if event_date not in analytics['events_by_date']:
                    analytics['events_by_date'][event_date] = {}
                analytics['events_by_date'][event_date][event_type] = event_count
            
            return analytics
        except Exception as e:
            logger.error(f"Failed to get analytics for user {user_id}: {e}")
            raise
    
    def _row_to_user_profile(self, row) -> UserProfile:
        """Convert database row to UserProfile object"""
        if not row:
            return None
        
        return UserProfile(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            birthdate=row['birthdate'],
            avatar_url=row['avatar_url'],
            timezone=row['timezone'],
            language_preference=row['language_preference'],
            auth_provider=AuthProvider(row['auth_provider']) if row['auth_provider'] else None,
            auth_provider_id=row['auth_provider_id'],
            terms_accepted_at=row['terms_accepted_at'],
            privacy_policy_accepted_at=row['privacy_policy_accepted_at'],
            is_active=row['is_active'],
            notification_preferences=row['notification_preferences'] or {},
            ui_preferences=row['ui_preferences'] or {},
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )

# Global user service instance
user_service = UserService() 