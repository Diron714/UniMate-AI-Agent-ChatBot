"""
Memory Store Tool
Read/write user memory for context persistence
Uses MemoryService for structured memory management
"""
from typing import Dict, Any, Optional
from app.tools.base_tool import BaseTool
from app.services.memory_service import MemoryService
import logging

logger = logging.getLogger(__name__)

class MemoryStoreTool(BaseTool):
    """
    Tool for storing and retrieving user memory/context
    Uses the structured memory system with short-term and long-term memory
    """
    
    def __init__(self):
        super().__init__(
            name="memory_store",
            description="Stores and retrieves user preferences, context, and remembered information. Use this to remember user details like university, course, stage, preferences, or important facts about the user. Can read full memory or update specific fields."
        )
        self.memory_service = MemoryService()
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform: 'read' to get user memory, 'write' to update user profile (university, course, stage, preferences)",
                    "enum": ["read", "write"]
                },
                "user_id": {
                    "type": "string",
                    "description": "User ID"
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID (optional, uses latest if not provided)"
                },
                "university": {
                    "type": "string",
                    "description": "University name (for write operation)"
                },
                "course": {
                    "type": "string",
                    "description": "Course name (for write operation)"
                },
                "stage": {
                    "type": "string",
                    "description": "User stage: 'pre-application', 'selected', or 'enrolled' (for write operation)",
                    "enum": ["pre-application", "selected", "enrolled"]
                },
                "preferences": {
                    "type": "object",
                    "description": "User preferences object (for write operation)"
                }
            },
            "required": ["operation", "user_id"]
        }
    
    def execute(
        self,
        operation: str = "",
        user_id: str = "",
        session_id: Optional[str] = None,
        university: Optional[str] = None,
        course: Optional[str] = None,
        stage: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Read or write user memory
        
        Args:
            operation: 'read' or 'write'
            user_id: User ID
            session_id: Session ID (optional)
            university: University name (for write)
            course: Course name (for write)
            stage: User stage (for write)
            preferences: User preferences (for write)
        
        Returns:
            Dict with operation result
        """
        if not operation or not user_id:
            return {
                "success": False,
                "data": None,
                "message": "Operation and user_id are required"
            }
        
        try:
            operation_lower = operation.lower()
            
            if operation_lower == "read":
                # Read memory
                memory = self.memory_service.get_memory(user_id, session_id)
                
                if memory:
                    # Format for LLM
                    long_term = memory.get("longTerm", {})
                    short_term = memory.get("shortTerm", [])
                    
                    return {
                        "success": True,
                        "data": {
                            "university": long_term.get("university"),
                            "course": long_term.get("course"),
                            "stage": long_term.get("stage"),
                            "preferences": long_term.get("preferences", {}),
                            "recent_messages": len(short_term)
                        },
                        "message": f"Retrieved memory for user {user_id}"
                    }
                else:
                    return {
                        "success": True,
                        "data": {
                            "university": None,
                            "course": None,
                            "stage": None,
                            "preferences": {},
                            "recent_messages": 0
                        },
                        "message": "No memory found for this user"
                    }
            
            elif operation_lower == "write":
                # Write memory (update long-term)
                if not session_id:
                    return {
                        "success": False,
                        "data": None,
                        "message": "session_id is required for write operation"
                    }
                
                success = self.memory_service.update_long_term(
                    userId=user_id,
                    sessionId=session_id,
                    university=university,
                    course=course,
                    stage=stage,
                    preferences=preferences
                )
                
                if success:
                    return {
                        "success": True,
                        "data": {
                            "university": university,
                            "course": course,
                            "stage": stage,
                            "preferences": preferences
                        },
                        "message": "Memory updated successfully"
                    }
                else:
                    return {
                        "success": False,
                        "data": None,
                        "message": "Failed to update memory"
                    }
            
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"Unknown operation: {operation}. Use 'read' or 'write'"
                }
                
        except Exception as e:
            logger.error(f"Memory Store Tool error: {e}", exc_info=True)
            return {
                "success": False,
                "data": None,
                "message": f"Memory operation error: {str(e)}"
            }

