"""
Memory Service
Service layer for managing user memory and context
"""
from typing import Optional, Dict, Any, List
import logging

from app.models.memory import MemoryModel

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Service for managing user memory
    """
    
    def __init__(self):
        """Initialize memory service"""
        self.memory_model = MemoryModel()
    
    def get_memory(
        self,
        userId: str,
        sessionId: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load user memory from MongoDB
        
        Args:
            userId: User ID
            sessionId: Session ID (optional)
        
        Returns:
            Memory dict or None
        """
        try:
            return self.memory_model.get_memory(userId, sessionId)
        except Exception as e:
            logger.error(f"Error getting memory: {e}", exc_info=True)
            return None
    
    def update_memory(
        self,
        userId: str,
        sessionId: str,
        shortTerm: Optional[List[Dict[str, Any]]] = None,
        longTerm: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save memory to MongoDB
        
        Args:
            userId: User ID
            sessionId: Session ID
            shortTerm: Short-term memory (conversation history)
            longTerm: Long-term memory (user profile)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.memory_model.create_or_update_memory(
                userId=userId,
                sessionId=sessionId,
                shortTerm=shortTerm,
                longTerm=longTerm
            )
        except Exception as e:
            logger.error(f"Error updating memory: {e}", exc_info=True)
            return False
    
    def add_to_short_term(
        self,
        userId: str,
        sessionId: str,
        role: str,
        content: str
    ) -> bool:
        """
        Add message to conversation history (short-term memory)
        
        Args:
            userId: User ID
            sessionId: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from datetime import datetime
            
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return self.memory_model.add_to_short_term(
                userId=userId,
                sessionId=sessionId,
                message=message
            )
        except Exception as e:
            logger.error(f"Error adding to short-term memory: {e}", exc_info=True)
            return False
    
    def update_long_term(
        self,
        userId: str,
        sessionId: str,
        university: Optional[str] = None,
        course: Optional[str] = None,
        stage: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update user profile (long-term memory)
        
        Args:
            userId: User ID
            sessionId: Session ID
            university: University name
            course: Course name
            stage: User stage (pre-application, selected, enrolled)
            preferences: User preferences dict
        
        Returns:
            True if successful, False otherwise
        """
        try:
            updates = {}
            
            if university is not None:
                updates["university"] = university
            if course is not None:
                updates["course"] = course
            if stage is not None:
                updates["stage"] = stage
            if preferences is not None:
                updates["preferences"] = preferences
            
            if updates:
                return self.memory_model.update_long_term(
                    userId=userId,
                    sessionId=sessionId,
                    long_term_updates=updates
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating long-term memory: {e}", exc_info=True)
            return False
    
    def clear_session(
        self,
        userId: str,
        sessionId: str
    ) -> bool:
        """
        Reset short-term memory for a session
        
        Args:
            userId: User ID
            sessionId: Session ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.memory_model.clear_session(userId, sessionId)
        except Exception as e:
            logger.error(f"Error clearing session: {e}", exc_info=True)
            return False
    
    def get_context(
        self,
        userId: str,
        sessionId: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get formatted context for LLM
        
        Args:
            userId: User ID
            sessionId: Session ID
        
        Returns:
            Context dict with user information
        """
        memory = self.get_memory(userId, sessionId)
        
        if not memory:
            return {
                "university": None,
                "course": None,
                "stage": None,
                "preferences": {},
                "conversation_history": []
            }
        
        long_term = memory.get("longTerm", {})
        short_term = memory.get("shortTerm", [])
        
        return {
            "university": long_term.get("university"),
            "course": long_term.get("course"),
            "stage": long_term.get("stage"),
            "preferences": long_term.get("preferences", {}),
            "conversation_history": short_term
        }

