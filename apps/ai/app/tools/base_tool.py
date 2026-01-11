"""
Base tool class for AI agent tools
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """
    Base class for all AI agent tools
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        Returns: Dict with result and metadata
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for LLM function calling
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_schema()
        }
    
    @abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get parameters schema for the tool
        """
        pass

