#!/usr/bin/env python3
"""
Database setup script for NeuraFormAI
Initializes PostgreSQL database with schema and initial data
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_database():
    """Create the database if it doesn't exist"""
    # Connect to default postgres database
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            database='postgres'
        )
        
        db_name = os.getenv('DB_NAME', 'neuraformai')
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            logger.info(f"Created database: {db_name}")
        else:
            logger.info(f"Database {db_name} already exists")
        
        await conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise

async def run_migrations():
    """Run database migrations"""
    try:
        # Connect to the application database
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'neuraformai')
        )
        
        # Read and execute schema
        schema_file = Path(__file__).parent / 'database_schema.sql'
        if schema_file.exists():
            with open(schema_file, 'r') as f:
                schema = f.read()
            
            await conn.execute(schema)
            logger.info("Database schema created successfully")
        else:
            logger.error("Schema file not found: database_schema.sql")
            return False
        
        # Insert initial personas data
        await insert_initial_personas(conn)
        
        await conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        raise

async def insert_initial_personas(conn):
    """Insert initial persona data"""
    personas = [
        {
            'name': 'fuka',
            'display_name': 'Fuka',
            'description': 'A cheerful and energetic AI companion who loves to chat and help with daily tasks.',
            'avatar_url': '/assets/neuraform_icon.png',
            'vrm_model_path': '/assets/vrms/fuka_model.vrm',
            'personality_config': {
                'traits': ['cheerful', 'energetic', 'helpful', 'friendly'],
                'interests': ['conversation', 'helping others', 'learning new things'],
                'speaking_style': 'casual and enthusiastic'
            },
            'voice_config': {
                'voice_id': 'fuka_voice',
                'speed': 1.0,
                'pitch': 1.0
            },
            'is_public': True
        },
        {
            'name': 'gwen',
            'display_name': 'Gwen',
            'description': 'A wise and thoughtful AI companion with a calm demeanor and deep insights.',
            'avatar_url': '/assets/neuraform_icon.png',
            'vrm_model_path': '/assets/vrms/gwen_model.vrm',
            'personality_config': {
                'traits': ['wise', 'thoughtful', 'calm', 'insightful'],
                'interests': ['philosophy', 'deep conversations', 'problem-solving'],
                'speaking_style': 'contemplative and measured'
            },
            'voice_config': {
                'voice_id': 'gwen_voice',
                'speed': 0.9,
                'pitch': 0.95
            },
            'is_public': True
        },
        {
            'name': 'kenji',
            'display_name': 'Kenji',
            'description': 'A disciplined and focused AI companion who excels at goal-setting and motivation.',
            'avatar_url': '/assets/neuraform_icon.png',
            'vrm_model_path': '/assets/vrms/kenji_model.vrm',
            'personality_config': {
                'traits': ['disciplined', 'focused', 'motivational', 'organized'],
                'interests': ['productivity', 'goal-setting', 'self-improvement'],
                'speaking_style': 'clear and encouraging'
            },
            'voice_config': {
                'voice_id': 'kenji_voice',
                'speed': 1.1,
                'pitch': 1.05
            },
            'is_public': True
        },
        {
            'name': 'koan',
            'display_name': 'Koan',
            'description': 'A creative and artistic AI companion who inspires imagination and artistic expression.',
            'avatar_url': '/assets/neuraform_icon.png',
            'vrm_model_path': '/assets/vrms/koan_model.vrm',
            'personality_config': {
                'traits': ['creative', 'artistic', 'imaginative', 'expressive'],
                'interests': ['art', 'creativity', 'storytelling', 'music'],
                'speaking_style': 'poetic and expressive'
            },
            'voice_config': {
                'voice_id': 'koan_voice',
                'speed': 0.95,
                'pitch': 1.0
            },
            'is_public': True
        },
        {
            'name': 'nika',
            'display_name': 'Nika',
            'description': 'A tech-savvy and analytical AI companion who loves exploring new technologies and solving complex problems.',
            'avatar_url': '/assets/neuraform_icon.png',
            'vrm_model_path': '/assets/vrms/nika_model.vrm',
            'personality_config': {
                'traits': ['tech-savvy', 'analytical', 'curious', 'logical'],
                'interests': ['technology', 'science', 'problem-solving', 'innovation'],
                'speaking_style': 'precise and informative'
            },
            'voice_config': {
                'voice_id': 'nika_voice',
                'speed': 1.05,
                'pitch': 1.0
            },
            'is_public': True
        }
    ]
    
    for persona in personas:
        # Check if persona already exists
        existing = await conn.fetchval(
            "SELECT id FROM public.personas WHERE name = $1", persona['name']
        )
        
        if not existing:
            await conn.execute("""
                INSERT INTO public.personas (
                    name, display_name, description, avatar_url, vrm_model_path,
                    personality_config, voice_config, is_public
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, 
                persona['name'], persona['display_name'], persona['description'],
                persona['avatar_url'], persona['vrm_model_path'],
                persona['personality_config'], persona['voice_config'], persona['is_public']
            )
            logger.info(f"Inserted persona: {persona['display_name']}")
        else:
            logger.info(f"Persona {persona['display_name']} already exists")

def create_env_template():
    """Create .env template file"""
    env_template = """# NeuraFormAI Environment Configuration

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=neuraformai
DB_USER=postgres
DB_PASSWORD=your_password_here

# Database Pool Configuration
DB_MIN_SIZE=5
DB_MAX_SIZE=20
DB_SSL=false

# Supabase Configuration (for OAuth and real-time features)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
FACEBOOK_APP_ID=your_facebook_app_id_here
FACEBOOK_APP_SECRET=your_facebook_app_secret_here
APPLE_TEAM_ID=your_apple_team_id_here
APPLE_KEY_ID=your_apple_key_id_here
APPLE_PRIVATE_KEY=your_apple_private_key_here

# Application Configuration
APP_SECRET_KEY=your_secret_key_here
APP_ENVIRONMENT=development
"""
    
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_template)
        logger.info("Created .env template file")
        logger.info("Please update .env with your actual configuration values")
    else:
        logger.info(".env file already exists")

async def main():
    """Main setup function"""
    logger.info("Starting NeuraFormAI database setup...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        # Create database
        await create_database()
        
        # Run migrations
        success = await run_migrations()
        
        if success:
            logger.info("Database setup completed successfully!")
            
            # Create .env template
            create_env_template()
            
            logger.info("\nNext steps:")
            logger.info("1. Update .env file with your actual configuration")
            logger.info("2. Install dependencies: pip install -r requirements_database.txt")
            logger.info("3. Set up OAuth applications in Google, Facebook, and Apple developer consoles")
            logger.info("4. Start your application!")
            
        else:
            logger.error("Database setup failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 