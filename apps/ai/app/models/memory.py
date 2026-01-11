"""
Memory Model
Stores user memory and context for personalized responses
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.config.db import MongoDBConnection

logger = logging.getLogger(__name__)


class MemoryModel:
    """
    Model for managing user memory in MongoDB
    """
    
    def __init__(self, collection_name: str = "memories"):
        """
        Initialize memory model
        
        Args:
            collection_name: Name of MongoDB collection
        """
        self.collection_name = collection_name
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB and get collection"""
        try:
            self.db = MongoDBConnection.get_db()
            if self.db is None:
                logger.warning("MongoDB not connected. Memory model operations will fail.")
                return
            
            self.collection = self.db[self.collection_name]
            self._ensure_indexes()
            logger.info(f"Memory model connected to collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}", exc_info=True)
            self.db = None
            self.collection = None
    
    def _ensure_indexes(self):
        """Create indexes for efficient queries"""
        if self.collection is None:
            return
        
        try:
            # Index on userId and sessionId for fast lookups
            self.collection.create_index([("userId", 1), ("sessionId", 1)])
            # Index on userId for user-specific queries
            self.collection.create_index([("userId", 1)])
            # Index on updatedAt for cleanup queries
            self.collection.create_index([("updatedAt", -1)])
            logger.info("Memory model indexes created")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def get_memory(
        self,
        userId: str,
        sessionId: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get user memory
        
        Args:
            userId: User ID
            sessionId: Session ID (optional, uses latest if not provided)
        
        Returns:
            Memory document or None
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return None
        
        try:
            query = {"userId": userId}
            if sessionId:
                query["sessionId"] = sessionId
            
            memory = self.collection.find_one(query, sort=[("updatedAt", -1)])
            
            if memory:
                # Remove MongoDB _id for cleaner response
                memory.pop("_id", None)
                return memory
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting memory: {e}", exc_info=True)
            return None
    
    def create_or_update_memory(
        self,
        userId: str,
        sessionId: str,
        shortTerm: Optional[List[Dict[str, Any]]] = None,
        longTerm: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create or update user memory
        
        Args:
            userId: User ID
            sessionId: Session ID
            shortTerm: Array of recent messages (last 10)
            longTerm: Long-term memory (university, course, stage, preferences)
        
        Returns:
            True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return False
        
        try:
            # Get existing memory
            existing = self.collection.find_one({
                "userId": userId,
                "sessionId": sessionId
            })
            
            # Prepare update document
            update_doc = {
                "updatedAt": datetime.utcnow()
            }
            
            if shortTerm is not None:
                # Limit to last 10 messages
                update_doc["shortTerm"] = shortTerm[-10:] if len(shortTerm) > 10 else shortTerm
            
            if longTerm is not None:
                update_doc["longTerm"] = longTerm
            
            if existing:
                # Update existing memory
                self.collection.update_one(
                    {"userId": userId, "sessionId": sessionId},
                    {"$set": update_doc}
                )
                logger.debug(f"Updated memory for user {userId}, session {sessionId}")
            else:
                # Create new memory
                memory_doc = {
                    "userId": userId,
                    "sessionId": sessionId,
                    "shortTerm": shortTerm[-10:] if shortTerm and len(shortTerm) > 10 else (shortTerm or []),
                    "longTerm": longTerm or {
                        "university": None,
                        "course": None,
                        "stage": None,
                        "preferences": {}
                    },
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }
                self.collection.insert_one(memory_doc)
                logger.debug(f"Created memory for user {userId}, session {sessionId}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating/updating memory: {e}", exc_info=True)
            return False
    
    def add_to_short_term(
        self,
        userId: str,
        sessionId: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Add message to short-term memory (conversation history)
        
        Args:
            userId: User ID
            sessionId: Session ID
            message: Message dict with role, content, timestamp
        
        Returns:
            True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return False
        
        try:
            # Get existing memory
            memory = self.get_memory(userId, sessionId)
            
            if memory:
                # Add to existing short-term memory
                short_term = memory.get("shortTerm", [])
                short_term.append(message)
                # Keep only last 10
                short_term = short_term[-10:]
                
                return self.create_or_update_memory(
                    userId=userId,
                    sessionId=sessionId,
                    shortTerm=short_term,
                    longTerm=memory.get("longTerm")
                )
            else:
                # Create new memory with this message
                return self.create_or_update_memory(
                    userId=userId,
                    sessionId=sessionId,
                    shortTerm=[message],
                    longTerm={
                        "university": None,
                        "course": None,
                        "stage": None,
                        "preferences": {}
                    }
                )
            
        except Exception as e:
            logger.error(f"Error adding to short-term memory: {e}", exc_info=True)
            return False
    
    def update_long_term(
        self,
        userId: str,
        sessionId: str,
        long_term_updates: Dict[str, Any]
    ) -> bool:
        """
        Update long-term memory (user profile)
        
        Args:
            userId: User ID
            sessionId: Session ID
            long_term_updates: Dict with keys to update (university, course, stage, preferences)
        
        Returns:
            True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return False
        
        try:
            # Get existing memory
            memory = self.get_memory(userId, sessionId)
            
            if memory:
                # Merge with existing long-term memory
                existing_long_term = memory.get("longTerm", {})
                updated_long_term = {**existing_long_term, **long_term_updates}
                
                return self.create_or_update_memory(
                    userId=userId,
                    sessionId=sessionId,
                    shortTerm=memory.get("shortTerm"),
                    longTerm=updated_long_term
                )
            else:
                # Create new memory
                return self.create_or_update_memory(
                    userId=userId,
                    sessionId=sessionId,
                    shortTerm=[],
                    longTerm={
                        "university": None,
                        "course": None,
                        "stage": None,
                        "preferences": {}
                    } | long_term_updates
                )
            
        except Exception as e:
            logger.error(f"Error updating long-term memory: {e}", exc_info=True)
            return False
    
    def clear_session(
        self,
        userId: str,
        sessionId: str
    ) -> bool:
        """
        Clear short-term memory for a session (reset conversation)
        
        Args:
            userId: User ID
            sessionId: Session ID
        
        Returns:
            True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return False
        
        try:
            memory = self.get_memory(userId, sessionId)
            if memory:
                return self.create_or_update_memory(
                    userId=userId,
                    sessionId=sessionId,
                    shortTerm=[],
                    longTerm=memory.get("longTerm")
                )
            return True
            
        except Exception as e:
            logger.error(f"Error clearing session: {e}", exc_info=True)
            return False

