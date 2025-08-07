# NeuraFormAI Database Setup Guide

## Overview

This guide will help you set up a robust PostgreSQL database system for NeuraFormAI with user authentication, OAuth integration, and comprehensive conversation storage. The system is designed to handle millions of users and conversations while maintaining excellent performance and security.

## Architecture

### Database Choice: PostgreSQL

**Why PostgreSQL over MongoDB?**

1. **ACID Compliance**: Critical for user data integrity and legal compliance
2. **Complex Relationships**: Excellent for user → conversations → messages → personas relationships
3. **JSON Support**: PostgreSQL's JSONB is perfect for flexible conversation data
4. **Scalability**: Can handle millions of records efficiently
5. **Supabase Integration**: Built-in auth with OAuth providers

### Key Features

- **User Authentication**: Google, Facebook, and Apple OAuth
- **Session Management**: Secure session tokens with expiration
- **Conversation Storage**: Complete chat history with metadata
- **Persona Management**: AI character configurations and preferences
- **Analytics**: User behavior tracking and insights
- **Voice Data**: TTS cache and voice recording storage
- **Row Level Security**: Data isolation and privacy protection

## Database Schema

### Core Tables

1. **users** - User profiles and authentication data
2. **personas** - AI character configurations
3. **conversations** - Chat sessions between users and personas
4. **messages** - Individual messages with metadata
5. **user_sessions** - Active user sessions
6. **user_persona_preferences** - User preferences for personas
7. **voice_data** - TTS cache and voice recordings
8. **user_analytics** - User behavior tracking

### Security Features

- **Row Level Security (RLS)**: Users can only access their own data
- **Session Management**: Secure token-based authentication
- **Data Encryption**: Sensitive data encryption at rest
- **Audit Logging**: Complete audit trail for compliance

## Setup Instructions

### 1. Prerequisites

- PostgreSQL 13+ installed and running
- Python 3.8+ with pip
- Git (for cloning the repository)

### 2. Install Dependencies

```bash
# Install database dependencies
pip install -r requirements_database.txt

# Or install individually
pip install asyncpg psycopg2-binary google-auth PyJWT cryptography aiohttp pydantic python-dotenv
```

### 3. Database Setup

```bash
# Run the setup script
python setup_database.py
```

This script will:

- Create the database if it doesn't exist
- Run the schema migrations
- Insert initial persona data
- Create a `.env` template file

### 4. Environment Configuration

Update the `.env` file with your actual configuration:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=neuraformai
DB_USER=postgres
DB_PASSWORD=your_actual_password

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
APPLE_TEAM_ID=your_apple_team_id
APPLE_KEY_ID=your_apple_key_id
APPLE_PRIVATE_KEY=your_apple_private_key

# Supabase (Optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 5. OAuth Setup

#### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs
6. Copy Client ID to `.env`

#### Facebook OAuth

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add Facebook Login product
4. Configure OAuth settings
5. Copy App ID and App Secret to `.env`

#### Apple OAuth

1. Go to [Apple Developer](https://developer.apple.com/)
2. Create App ID with Sign In with Apple capability
3. Create Service ID
4. Generate private key
5. Copy Team ID, Key ID, and Private Key to `.env`

## Integration with Existing Application

### 1. Update Main Application

Add the auth router to your FastAPI app:

```python
from app.api.auth import router as auth_router

app.include_router(auth_router)
```

### 2. Initialize Database

In your main application startup:

```python
from app.config.database import init_database, cleanup_database

@app.on_event("startup")
async def startup_event():
    await init_database()

@app.on_event("shutdown")
async def shutdown_event():
    await cleanup_database()
```

### 3. Update Chat Service

Modify your existing chat service to use the database:

```python
from app.services.user_service import user_service
from app.services.auth_service import oauth_service

# In your chat endpoints, get user from session
async def chat_endpoint(request: Request):
    # Get user from session token
    session_token = request.headers.get("Authorization")
    user = await oauth_service.validate_session(session_token)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Use user.id for conversation tracking
    # ... rest of your chat logic
```

## API Endpoints

### Authentication

- `POST /auth/login` - OAuth login
- `POST /auth/register` - User registration
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile
- `POST /auth/logout` - Logout user
- `DELETE /auth/account` - Delete account

### Usage Examples

#### OAuth Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "token": "google_id_token_here",
    "device_info": {"platform": "web", "browser": "chrome"}
  }'
```

#### Get User Profile

```bash
curl -X GET "http://localhost:8000/auth/profile" \
  -H "Authorization: Bearer your_session_token_here"
```

## Data Models

### User Profile

```python
@dataclass
class UserProfile:
    id: str
    first_name: str
    last_name: str
    email: str
    birthdate: date
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    language_preference: str = "en"
    auth_provider: Optional[AuthProvider] = None
    # ... additional fields
```

### Conversation

```python
class Conversation:
    id: UUID
    user_id: UUID
    persona_id: UUID
    title: str
    summary: str
    metadata: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

## Performance Considerations

### Indexing Strategy

- Primary keys on all tables
- Foreign key indexes for relationships
- Composite indexes for common queries
- Partial indexes for active records

### Connection Pooling

- Configured with 5-20 connections
- Automatic connection management
- Health checks and reconnection

### Query Optimization

- Use prepared statements
- Implement pagination for large datasets
- Cache frequently accessed data
- Use JSONB for flexible data storage

## Security Best Practices

### Data Protection

- All user data encrypted at rest
- Session tokens with expiration
- Row Level Security enabled
- Input validation and sanitization

### Authentication

- OAuth token verification
- Session management
- Rate limiting on auth endpoints
- Audit logging for security events

### Privacy Compliance

- COPPA compliance (13+ age requirement)
- GDPR-ready data handling
- User consent tracking
- Data deletion capabilities

## Monitoring and Analytics

### Built-in Analytics

- User login/logout events
- Conversation metrics
- Feature usage tracking
- Performance monitoring

### Custom Events

```python
# Track custom events
await oauth_service.track_analytics_event(
    user_id="user_123",
    event_type="persona_selected",
    event_data={"persona_id": "persona_456", "selection_method": "click"}
)
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**

   - Check PostgreSQL is running
   - Verify connection credentials
   - Check firewall settings

2. **OAuth Authentication Fails**

   - Verify OAuth app configuration
   - Check redirect URIs
   - Validate client IDs and secrets

3. **Session Validation Errors**
   - Check session token format
   - Verify token expiration
   - Ensure database connectivity

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. **Set up OAuth applications** in respective developer consoles
2. **Configure environment variables** with actual values
3. **Test authentication flow** with each provider
4. **Integrate with existing chat system**
5. **Add user management features**
6. **Implement analytics dashboard**

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review database logs
3. Verify configuration values
4. Test with minimal setup first

The database system is designed to be robust, scalable, and secure. It provides a solid foundation for your AI chat companion application with proper user management and data persistence.
