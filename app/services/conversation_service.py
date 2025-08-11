import asyncpg
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConversationService:
    """Service for managing conversations and messages in the database"""
    
    def __init__(self):
        # Try DATABASE_URL first, then build from individual components
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME")
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            
            if not all([db_host, db_name, db_user, db_password]):
                raise ValueError("Database configuration incomplete. Need DB_HOST, DB_NAME, DB_USER, DB_PASSWORD")
            
            self.db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        print(f"🔗 [ConversationService] Database URL configured: postgresql://{os.getenv('DB_USER')}:***@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    
    async def _get_connection(self):
        """Get database connection"""
        return await asyncpg.connect(self.db_url)
    
    async def get_or_create_conversation(self, user_id: str, persona_name: str) -> str:
        """Get existing conversation or create new one for user-persona pair"""
        conn = await self._get_connection()
        try:
            # First try to find existing active conversation
            query = """
                SELECT c.id 
                FROM conversations c
                JOIN personas p ON c.persona_id = p.id
                WHERE c.user_id = $1 AND LOWER(p.name) = LOWER($2) AND c.is_active = true
                LIMIT 1
            """
            result = await conn.fetchrow(query, UUID(user_id), persona_name)
            
            if result:
                return str(result['id'])
            
            # No existing conversation, create new one
            # First get persona_id
            persona_query = "SELECT id FROM personas WHERE LOWER(name) = LOWER($1) LIMIT 1"
            persona_result = await conn.fetchrow(persona_query, persona_name)
            
            if not persona_result:
                # Create persona record if it doesn't exist
                persona_id = uuid4()
                insert_persona_query = """
                    INSERT INTO personas (id, name, display_name, description, personality_config)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                """
                persona_result = await conn.fetchrow(
                    insert_persona_query, 
                    persona_id, 
                    persona_name, 
                    persona_name.title(), 
                    f"AI persona named {persona_name}",
                    json.dumps({})  # Convert dict to JSON string
                )
            
            # Create new conversation
            conversation_id = uuid4()
            insert_query = """
                INSERT INTO conversations (id, user_id, persona_id, title, is_active)
                VALUES ($1, $2, $3, $4, true)
                RETURNING id
            """
            title = f"Chat with {persona_name.title()}"
            result = await conn.fetchrow(
                insert_query, 
                conversation_id, 
                UUID(user_id), 
                persona_result['id'], 
                title
            )
            
            return str(result['id'])
            
        finally:
            await conn.close()

    async def get_conversation_for_persona(self, user_id: str, persona_name: str) -> Optional[str]:
        """Get existing conversation ID for user-persona pair (without creating)"""
        conn = await self._get_connection()
        try:
            query = """
                SELECT c.id 
                FROM conversations c
                JOIN personas p ON c.persona_id = p.id
                WHERE c.user_id = $1 AND LOWER(p.name) = LOWER($2) AND c.is_active = true
                LIMIT 1
            """
            result = await conn.fetchrow(query, UUID(user_id), persona_name)
            
            return str(result['id']) if result else None
            
        finally:
            await conn.close()
    
    async def save_message(self, conversation_id: str, sender_type: str, content: str, 
                          user_id: str = None, persona_id: str = None, tokens_used: int = None,
                          processing_time_ms: int = None) -> str:
        """Save a message to the database"""
        conn = await self._get_connection()
        try:
            message_id = uuid4()
            query = """
                INSERT INTO messages (
                    id, conversation_id, sender_type, content, 
                    user_id, ai_persona_id, tokens_used, processing_time_ms
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """
            
            result = await conn.fetchrow(
                query,
                message_id,
                UUID(conversation_id),
                sender_type,
                content,
                UUID(user_id) if user_id else None,
                UUID(persona_id) if persona_id else None,
                tokens_used,
                processing_time_ms
            )
            
            # Update conversation's updated_at timestamp
            update_query = """
                UPDATE conversations 
                SET updated_at = NOW() 
                WHERE id = $1
            """
            await conn.execute(update_query, UUID(conversation_id))
            
            return str(result['id'])
            
        finally:
            await conn.close()
    
    async def get_conversation_messages(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a conversation"""
        conn = await self._get_connection()
        try:
            query = """
                SELECT 
                    id,
                    sender_type,
                    content,
                    created_at,
                    tokens_used,
                    processing_time_ms,
                    metadata
                FROM messages 
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                LIMIT $2
            """
            
            results = await conn.fetch(query, UUID(conversation_id), limit)
            
            return [
                {
                    'id': str(row['id']),
                    'sender_type': row['sender_type'],
                    'content': row['content'],
                    'created_at': row['created_at'].isoformat(),
                    'tokens_used': row['tokens_used'],
                    'processing_time_ms': row['processing_time_ms'],
                    'metadata': row['metadata'] or {}
                }
                for row in results
            ]
            
        finally:
            await conn.close()

    async def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user with their titles and metadata"""
        conn = await self._get_connection()
        
        try:
            query = """
                SELECT 
                    c.id,
                    c.title,
                    c.created_at,
                    c.updated_at,
                    c.is_active,
                    p.name as persona_name,
                    COUNT(m.id) as message_count,
                    MAX(m.created_at) as last_message_at
                FROM conversations c
                LEFT JOIN personas p ON c.persona_id = p.id
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.user_id = $1
                GROUP BY c.id, c.title, c.created_at, c.updated_at, c.is_active, p.name
                ORDER BY c.updated_at DESC
            """
            
            results = await conn.fetch(query, UUID(user_id))
            
            return [
                {
                    'id': str(row['id']),
                    'title': row['title'],
                    'persona_name': row['persona_name'],
                    'created_at': row['created_at'].isoformat(),
                    'updated_at': row['updated_at'].isoformat(),
                    'is_active': row['is_active'],
                    'message_count': row['message_count'],
                    'last_message_at': row['last_message_at'].isoformat() if row['last_message_at'] else None
                }
                for row in results
            ]
            
        finally:
            await conn.close()

    async def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        conn = await self._get_connection()
        
        try:
            query = """
                UPDATE conversations 
                SET title = $1, updated_at = $2
                WHERE id = $3
            """
            
            result = await conn.execute(query, title, datetime.utcnow(), UUID(conversation_id))
            
            # Check if any rows were affected
            return result == "UPDATE 1"
            
        finally:
            await conn.close()

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        conn = await self._get_connection()
        
        try:
            # Start a transaction
            async with conn.transaction():
                # Delete all messages in the conversation first
                delete_messages_query = "DELETE FROM messages WHERE conversation_id = $1"
                await conn.execute(delete_messages_query, UUID(conversation_id))
                
                # Delete the conversation
                delete_conversation_query = "DELETE FROM conversations WHERE id = $1"
                result = await conn.execute(delete_conversation_query, UUID(conversation_id))
                
                # Check if any rows were affected
                return result == "DELETE 1"
                
        finally:
            await conn.close()