"""
Database configuration for NeuraFormAI
Supports both local PostgreSQL and Supabase cloud database
"""

import os
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool, Connection
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration from environment variables"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'neuraformai'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'min_size': int(os.getenv('DB_MIN_SIZE', '5')),
            'max_size': int(os.getenv('DB_MAX_SIZE', '20')),
            'ssl': os.getenv('DB_SSL', 'false').lower() == 'true',
            'ssl_cert': os.getenv('DB_SSL_CERT'),
            'ssl_key': os.getenv('DB_SSL_KEY'),
            'ssl_ca': os.getenv('DB_SSL_CA'),
        }
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            ssl_config = None
            if self._config['ssl']:
                ssl_config = {
                    'ssl': True,
                    'ssl_cert': self._config['ssl_cert'],
                    'ssl_key': self._config['ssl_key'],
                    'ssl_ca': self._config['ssl_ca'],
                }
                # Remove None values
                ssl_config = {k: v for k, v in ssl_config.items() if v is not None}
            
            self.pool = await asyncpg.create_pool(
                host=self._config['host'],
                port=self._config['port'],
                database=self._config['database'],
                user=self._config['user'],
                password=self._config['password'],
                min_size=self._config['min_size'],
                max_size=self._config['max_size'],
                **ssl_config if ssl_config else {}
            )
            
            logger.info(f"Database pool initialized with {self._config['min_size']}-{self._config['max_size']} connections")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args, **kwargs):
        """Execute a query without returning results"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args, **kwargs)
    
    async def fetch(self, query: str, *args, **kwargs):
        """Fetch all rows from a query"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args, **kwargs)
    
    async def fetchrow(self, query: str, *args, **kwargs):
        """Fetch a single row from a query"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args, **kwargs)
    
    async def fetchval(self, query: str, *args, **kwargs):
        """Fetch a single value from a query"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args, **kwargs)

# Global database instance
db = DatabaseConfig()

# Supabase specific configuration
class SupabaseConfig:
    """Supabase configuration for authentication and real-time features"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not all([self.url, self.anon_key]):
            logger.warning("Supabase configuration incomplete. OAuth features may not work.")
    
    def get_auth_url(self) -> str:
        """Get Supabase auth URL"""
        return f"{self.url}/auth/v1"
    
    def get_rest_url(self) -> str:
        """Get Supabase REST API URL"""
        return f"{self.url}/rest/v1"
    
    def get_realtime_url(self) -> str:
        """Get Supabase real-time URL"""
        return f"{self.url}/realtime/v1"

# Global Supabase instance
supabase = SupabaseConfig()

# Database initialization function
async def init_database():
    """Initialize database connection"""
    await db.initialize()
    
    # Test connection
    try:
        result = await db.fetchval("SELECT 1")
        logger.info("Database connection test successful")
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        raise

# Database cleanup function
async def cleanup_database():
    """Cleanup database connections"""
    await db.close()

# Environment variable template
ENV_TEMPLATE = """
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=neuraformai
DB_USER=postgres
DB_PASSWORD=your_password_here

# Supabase Configuration (for OAuth and real-time features)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Database Pool Configuration
DB_MIN_SIZE=5
DB_MAX_SIZE=20
DB_SSL=false
""" 