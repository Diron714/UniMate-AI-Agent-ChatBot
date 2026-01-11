"""
Tool Wrapper
Converts custom tools to LangChain-compatible tools
"""
from typing import Type, Optional, Any
from langchain_core.tools import BaseTool as LangChainBaseTool
from pydantic import BaseModel, Field
from app.tools.base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)

class LangChainToolWrapper(LangChainBaseTool):
    """
    Wrapper to convert custom BaseTool to LangChain tool
    """
    
    def __init__(self, custom_tool: BaseTool, **kwargs):
        # Store tool reference before calling super().__init__
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, 'custom_tool', custom_tool)
        
        # Create input schema from custom tool
        input_schema = self._create_input_schema()
        
        super().__init__(
            name=custom_tool.name,
            description=custom_tool.description,
            args_schema=input_schema
        )
    
    def _create_input_schema(self):
        """
        Create Pydantic model from tool's parameter schema
        """
        params_schema = self.custom_tool.get_parameters_schema()
        properties = params_schema.get("properties", {})
        required = params_schema.get("required", [])
        
        # Create dynamic Pydantic model
        field_definitions = {}
        for prop_name, prop_info in properties.items():
            prop_type = self._map_type(prop_info.get("type", "string"))
            description = prop_info.get("description", "")
            is_required = prop_name in required
            
            if is_required:
                field_definitions[prop_name] = (
                    prop_type,
                    Field(description=description)
                )
            else:
                field_definitions[prop_name] = (
                    Optional[prop_type],
                    Field(default=None, description=description)
                )
        
        # Create model class dynamically
        InputSchema = type(
            f"{self.custom_tool.name}_InputSchema",
            (BaseModel,),
            field_definitions
        )
        
        return InputSchema
    
    def _map_type(self, type_str: str):
        """Map JSON schema type to Python type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "object": dict,
            "array": list,
            "any": Any
        }
        return type_mapping.get(type_str, str)
    
    def _run(self, **kwargs) -> str:
        """
        Execute the tool and return result as string
        """
        try:
            result = self.custom_tool.execute(**kwargs)
            
            # Format result as string for LangChain
            if isinstance(result, dict):
                if result.get("success"):
                    # Return the message or formatted result
                    message = result.get("message", "")
                    if "results" in result:
                        # For search results, format nicely
                        results = result.get("results", [])
                        if results:
                            formatted = f"{message}\n\n"
                            for i, res in enumerate(results[:3], 1):  # Top 3
                                formatted += f"{i}. {res.get('title', 'Result')}\n"
                                formatted += f"   {res.get('content', '')[:200]}...\n\n"
                            return formatted
                    return message
                else:
                    return f"Error: {result.get('message', 'Unknown error')}"
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error executing tool {self.custom_tool.name}: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    async def _arun(self, **kwargs) -> str:
        """Async version"""
        return self._run(**kwargs)

