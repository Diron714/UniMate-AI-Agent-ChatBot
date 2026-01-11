"""
Rule Engine Tool
Validates policies and rules from UGC documents
"""
from typing import Dict, Any, List, Optional
from app.tools.base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)

class RuleEngineTool(BaseTool):
    """
    Tool for validating policies and rules
    """
    
    def __init__(self):
        super().__init__(
            name="rule_engine",
            description="Validates university policies, admission rules, and UGC regulations. Use this when the user asks about specific rules, policies, or whether something is allowed/prohibited."
        )
        # Common rules cache (in production, this would be from database)
        self.rules = {
            "admission": {
                "minimum_z_score": 0.0,
                "required_subjects": ["General English"],
                "age_limit": 25,
            },
            "course_change": {
                "allowed": True,
                "conditions": ["Within first year", "Subject to availability", "Approval required"]
            },
            "scholarship": {
                "eligibility": ["Merit-based", "Need-based", "Sports", "Arts"],
                "application_period": "Annually"
            }
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "rule_type": {
                    "type": "string",
                    "description": "Type of rule to validate (e.g., 'admission', 'course_change', 'scholarship')",
                    "enum": ["admission", "course_change", "scholarship", "graduation", "attendance", "examination"]
                },
                "query": {
                    "type": "string",
                    "description": "Specific question about the rule or policy"
                },
                "context": {
                    "type": "object",
                    "description": "Additional context (university, course, etc.)"
                }
            },
            "required": ["rule_type", "query"]
        }
    
    def execute(
        self,
        rule_type: str = "",
        query: str = "",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Validate rule or policy
        
        Args:
            rule_type: Type of rule to check
            query: Specific question about the rule
            context: Additional context
        
        Returns:
            Dict with rule validation result
        """
        if not rule_type or not query:
            return {
                "success": False,
                "valid": False,
                "rule": None,
                "message": "Rule type and query are required"
            }
        
        try:
            rule_type_lower = rule_type.lower()
            
            # Get rule from cache or database
            rule = self.rules.get(rule_type_lower)
            
            if not rule:
                return {
                    "success": False,
                    "valid": False,
                    "rule": None,
                    "message": f"Rule type '{rule_type}' not found. Available types: {', '.join(self.rules.keys())}"
                }
            
            # Simple validation logic
            # In production, this would use a more sophisticated rule engine
            query_lower = query.lower()
            
            # Check if query matches rule conditions
            is_valid = True
            explanation = f"Rule for {rule_type}: {rule}"
            
            # Example validations
            if "minimum" in query_lower or "z-score" in query_lower:
                if "minimum_z_score" in rule:
                    explanation = f"Minimum Z-score requirement: {rule['minimum_z_score']}"
            
            if "age" in query_lower:
                if "age_limit" in rule:
                    explanation = f"Age limit: {rule['age_limit']} years"
            
            if "allowed" in query_lower or "permitted" in query_lower:
                if "allowed" in rule:
                    is_valid = rule["allowed"]
                    explanation = f"This is {'allowed' if is_valid else 'not allowed'} according to UGC regulations"
            
            return {
                "success": True,
                "valid": is_valid,
                "rule": rule,
                "explanation": explanation,
                "message": f"Rule validation for {rule_type}: {explanation}"
            }
            
        except Exception as e:
            logger.error(f"Rule Engine Tool error: {e}", exc_info=True)
            return {
                "success": False,
                "valid": False,
                "rule": None,
                "message": f"Rule validation error: {str(e)}"
            }

