"""
Detect University Tool
Detects university from user message using keyword matching and context
"""
from typing import Dict, Any
from app.tools.base_tool import BaseTool
import re

class DetectUniversityTool(BaseTool):
    """
    Tool to detect university from user message
    """
    
    # Common Sri Lankan universities and their variations
    UNIVERSITY_KEYWORDS = {
        "university of colombo": ["colombo", "uc", "university of colombo"],
        "university of peradeniya": ["peradeniya", "pera", "up"],
        "university of kelaniya": ["kelaniya", "kelani", "uk"],
        "university of moratuwa": ["moratuwa", "mora", "um"],
        "university of jaffna": ["jaffna", "uj"],
        "university of ruhuna": ["ruhuna", "ruh", "ur"],
        "eastern university": ["eastern", "eastern uni", "eu"],
        "sabaragamuwa university": ["sabaragamuwa", "sabara", "su"],
        "wayamba university": ["wayamba", "wayamba uni", "wu"],
        "rajarata university": ["rajarata", "rajarata uni", "ru"],
        "south eastern university": ["south eastern", "seu"],
        "open university": ["open uni", "ou", "open university of sri lanka"],
    }
    
    def __init__(self):
        super().__init__(
            name="detect_university",
            description="Detects which university the user is referring to in their message. Use this when the user mentions a university name or asks about a specific university."
        )
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The user's message to analyze for university mentions"
                }
            },
            "required": ["message"]
        }
    
    def execute(self, message: str = "") -> Dict[str, Any]:
        """
        Detect university from message
        
        Args:
            message: User message to analyze
        
        Returns:
            Dict with detected university and confidence
        """
        if not message:
            return {
                "success": False,
                "university": None,
                "confidence": 0.0,
                "message": "No message provided"
            }
        
        message_lower = message.lower()
        best_match = None
        best_score = 0.0
        
        # Check for exact matches and keyword matches
        for university, keywords in self.UNIVERSITY_KEYWORDS.items():
            score = 0.0
            
            # Exact match gets highest score
            if university in message_lower:
                score = 1.0
            else:
                # Check for keyword matches
                for keyword in keywords:
                    if keyword in message_lower:
                        score = max(score, 0.7)
                        # If keyword is at word boundary, increase score
                        if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                            score = max(score, 0.9)
            
            if score > best_score:
                best_score = score
                best_match = university
        
        # Format university name properly
        if best_match:
            # Convert to title case
            university_name = best_match.title()
            return {
                "success": True,
                "university": university_name,
                "confidence": best_score,
                "message": f"Detected university: {university_name} (confidence: {best_score:.2f})"
            }
        else:
            return {
                "success": False,
                "university": None,
                "confidence": 0.0,
                "message": "No university detected in message"
            }

