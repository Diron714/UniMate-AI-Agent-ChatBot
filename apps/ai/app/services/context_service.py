"""
Context Detection Service
Detects and extracts user context from messages
"""
import re
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ContextService:
    """
    Service for detecting and updating user context
    """
    
    # University name patterns
    UNIVERSITY_PATTERNS = [
        r"university of jaffna|jaffna university|jaffna",
        r"university of colombo|colombo university|colombo",
        r"university of peradeniya|peradeniya university|peradeniya",
        r"university of moratuwa|moratuwa university|moratuwa",
        r"university of kelaniya|kelaniya university|kelaniya",
        r"university of sri jayewardenepura|sri jayewardenepura university|jayewardenepura",
        r"university of ruhuna|ruhuna university|ruhuna",
        r"eastern university|eastern",
        r"rajarata university|rajarata",
        r"sabaragamuwa university|sabaragamuwa",
        r"south eastern university|south eastern",
        r"wayamba university|wayamba",
        r"uva wellassa university|uva wellassa",
        r"vavuniya university|vavuniya"
    ]
    
    # Stage detection patterns
    STAGE_PATTERNS = {
        "pre-application": [
            r"before.*application|pre.*application|not.*applied|haven.*applied|planning.*apply|going.*apply|will.*apply",
            r"a/l.*result|a level|advanced level|results.*out|got.*results"
        ],
        "selected": [
            r"selected|got.*selected|accepted|admitted|got.*admission|received.*offer",
            r"chosen|got.*place|got.*into|admission.*letter"
        ],
        "enrolled": [
            r"enrolled|studying|current.*student|at.*university|in.*university|my.*university",
            r"first.*year|second.*year|third.*year|fourth.*year|final.*year"
        ]
    }
    
    # Course detection patterns (common courses)
    COURSE_PATTERNS = [
        r"engineering|computer.*science|medicine|law|business|management",
        r"arts|science|commerce|agriculture|veterinary",
        r"bachelor|degree|program|course"
    ]
    
    def detect_university(self, message: str) -> Optional[str]:
        """
        Extract university name from user message
        
        Args:
            message: User message text
        
        Returns:
            University name or None
        """
        message_lower = message.lower()
        
        # Map patterns to university names
        university_map = {
            r"university of jaffna|jaffna university|jaffna": "University of Jaffna",
            r"university of colombo|colombo university|colombo": "University of Colombo",
            r"university of peradeniya|peradeniya university|peradeniya": "University of Peradeniya",
            r"university of moratuwa|moratuwa university|moratuwa": "University of Moratuwa",
            r"university of kelaniya|kelaniya university|kelaniya": "University of Kelaniya",
            r"university of sri jayewardenepura|sri jayewardenepura university|jayewardenepura": "University of Sri Jayewardenepura",
            r"university of ruhuna|ruhuna university|ruhuna": "University of Ruhuna",
            r"eastern university|eastern": "Eastern University",
            r"rajarata university|rajarata": "Rajarata University",
            r"sabaragamuwa university|sabaragamuwa": "Sabaragamuwa University",
            r"south eastern university|south eastern": "South Eastern University",
            r"wayamba university|wayamba": "Wayamba University",
            r"uva wellassa university|uva wellassa": "Uva Wellassa University",
            r"vavuniya university|vavuniya": "Vavuniya University"
        }
        
        for pattern, university_name in university_map.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.info(f"Detected university: {university_name}")
                return university_name
        
        return None
    
    def detect_stage(self, message: str) -> Optional[str]:
        """
        Detect user stage from message
        
        Args:
            message: User message text
        
        Returns:
            Stage: 'pre-application', 'selected', or 'enrolled', or None
        """
        message_lower = message.lower()
        
        # Check each stage pattern
        for stage, patterns in self.STAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    logger.info(f"Detected stage: {stage}")
                    return stage
        
        return None
    
    def detect_course(self, message: str) -> Optional[str]:
        """
        Extract course name from message
        
        Args:
            message: User message text
        
        Returns:
            Course name or None
        """
        message_lower = message.lower()
        
        # Common course patterns
        course_map = {
            r"computer.*science|cs|computing": "Computer Science",
            r"engineering|eng": "Engineering",
            r"medicine|medical": "Medicine",
            r"law|legal": "Law",
            r"business.*administration|mba|business": "Business Administration",
            r"management": "Management",
            r"agriculture": "Agriculture",
            r"veterinary": "Veterinary Science"
        }
        
        for pattern, course_name in course_map.items():
            if re.search(pattern, message_lower, re.IGNORECASE):
                logger.info(f"Detected course: {course_name}")
                return course_name
        
        return None
    
    def update_context(
        self,
        message: str,
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Automatically update user context based on message
        
        Args:
            message: User message
            current_context: Current context dict
        
        Returns:
            Updated context dict
        """
        updated_context = current_context.copy()
        
        # Detect university
        university = self.detect_university(message)
        if university:
            updated_context["university"] = university
            logger.info(f"Updated context: university = {university}")
        
        # Detect stage
        stage = self.detect_stage(message)
        if stage:
            updated_context["stage"] = stage
            logger.info(f"Updated context: stage = {stage}")
        
        # Detect course
        course = self.detect_course(message)
        if course:
            updated_context["course"] = course
            logger.info(f"Updated context: course = {course}")
        
        return updated_context
    
    def should_filter_by_university(self, context: Dict[str, Any]) -> bool:
        """
        Check if answers should be filtered by university
        
        Args:
            context: User context
        
        Returns:
            True if university context is set
        """
        return context.get("university") is not None
    
    def get_university_filter(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Get university name for filtering
        
        Args:
            context: User context
        
        Returns:
            University name or None
        """
        return context.get("university")

