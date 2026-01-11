"""
LangChain Service for AI Agent
Integrates LangChain with Google Gemini for tool calling and memory management
"""
import os
from typing import List, Dict, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool as LangChainBaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import logging

# Simple in-memory conversation storage (replacing ConversationBufferMemory)
class SimpleMemory:
    """Simple memory implementation for conversation history"""
    def __init__(self):
        self.messages: List[BaseMessage] = []
    
    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))
    
    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))

logger = logging.getLogger(__name__)

class LangChainService:
    """
    LangChain service wrapper for Gemini with tool calling and memory
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        # Get model name from environment or use default
        # models/ prefix is mandatory for API compatibility
        # Updated to gemini-2.5-flash (latest stable version)
        model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
        # Ensure models/ prefix is present
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        
        # Initialize Gemini model via LangChain
        # Using models/gemini-1.5-flash with models/ prefix for API compatibility
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=0.3,
            max_tokens=2048,
        )
        
        # Memory stores (per session)
        self.memories: Dict[str, SimpleMemory] = {}
        
        logger.info("LangChain service initialized with Gemini")
    
    def get_memory(self, session_id: str) -> SimpleMemory:
        """
        Get or create memory for a session
        """
        if session_id not in self.memories:
            self.memories[session_id] = SimpleMemory()
        return self.memories[session_id]
    
    def clear_memory(self, session_id: str):
        """
        Clear memory for a session
        """
        if session_id in self.memories:
            del self.memories[session_id]
    
    def format_messages(self, history: List[Dict]) -> List[BaseMessage]:
        """
        Convert conversation history to LangChain messages
        """
        messages = []
        for msg in history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
        return messages
    
    async def generate_with_tools(
        self,
        message: str,
        tools: List[LangChainBaseTool],
        system_prompt: str,
        session_id: str,
        context: Optional[Dict] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Generate response using LangChain with tools
        
        Args:
            message: User message
            tools: List of LangChain tools
            system_prompt: System prompt for the agent
            session_id: Session ID for memory
            context: Additional context (university, preferences, etc.)
            conversation_history: Previous conversation messages
        
        Returns:
            Dict with response, sources, and metadata
        """
        try:
            # Get or create memory for this session
            memory = self.get_memory(session_id)
            
            # Build prompt with system message and context
            context_str = ""
            if context:
                context_parts = []
                if context.get("university"):
                    context_parts.append(f"University: {context['university']}")
                if context.get("stage"):
                    context_parts.append(f"Stage: {context['stage']}")
                if context.get("preferences"):
                    prefs = context["preferences"]
                    if prefs.get("language"):
                        context_parts.append(f"Language: {prefs['language']}")
                if context_parts:
                    context_str = "\n".join(context_parts)
            
            # Create prompt with tools
            if tools:
                # Bind tools to model
                model_with_tools = self.model.bind_tools(tools)
                
                # Build messages using LangChain message types
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
                messages = []
                
                # Add system prompt
                if system_prompt:
                    system_content = system_prompt + (f"\n\nContext:\n{context_str}" if context_str else "")
                    messages.append(SystemMessage(content=system_content))
                
                # Load conversation history
                if conversation_history:
                    for msg in conversation_history:
                        if msg.get("role") == "user":
                            messages.append(HumanMessage(content=msg.get("content", "")))
                        elif msg.get("role") == "assistant":
                            messages.append(AIMessage(content=msg.get("content", "")))
                
                # Add current user message
                messages.append(HumanMessage(content=message))
                
                # Generate response (may include tool calls)
                response = await model_with_tools.ainvoke(messages)
                
                # Handle tool calls if present
                sources = []
                tools_used = []
                final_response = response
                
                # If response has tool calls, execute them and get final response
                if hasattr(response, "tool_calls") and response.tool_calls:
                    # Create tool map for quick lookup
                    tool_map = {tool.name: tool for tool in tools}
                    
                    # Execute tool calls
                    tool_messages = []
                    for tool_call in response.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        tool_args = tool_call.get("args", {})
                        tools_used.append(tool_name)
                        sources.append(f"Tool: {tool_name}")
                        
                        if tool_name in tool_map:
                            try:
                                # Execute tool
                                tool_result = await tool_map[tool_name].ainvoke(tool_args)
                                
                                # Add tool result as ToolMessage
                                from langchain_core.messages import ToolMessage
                                tool_messages.append(
                                    ToolMessage(
                                        content=str(tool_result),
                                        tool_call_id=tool_call.get("id", tool_name)
                                    )
                                )
                                logger.info(f"Tool {tool_name} executed successfully")
                            except Exception as e:
                                logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                                from langchain_core.messages import ToolMessage
                                tool_messages.append(
                                    ToolMessage(
                                        content=f"Error: {str(e)}",
                                        tool_call_id=tool_call.get("id", tool_name)
                                    )
                                )
                    
                    # Add tool results to messages and get final response
                    if tool_messages:
                        messages.append(response)  # Add the tool call message
                        messages.extend(tool_messages)  # Add tool results
                        final_response = await model_with_tools.ainvoke(messages)
                
                # Extract final response text
                response_text = final_response.content if hasattr(final_response, "content") else str(final_response)
                
                return {
                    "response": response_text,
                    "sources": sources,
                    "metadata": {
                        "model": os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash"),
                        "tools_used": tools_used
                    }
                }
            else:
                # No tools, simple generation
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
                messages = []
                
                # Add system prompt
                system_content = system_prompt + (f"\n\nContext:\n{context_str}" if context_str else "")
                messages.append(SystemMessage(content=system_content))
                
                # Load conversation history
                if conversation_history:
                    for msg in conversation_history:
                        if msg.get("role") == "user":
                            messages.append(HumanMessage(content=msg.get("content", "")))
                        elif msg.get("role") == "assistant":
                            messages.append(AIMessage(content=msg.get("content", "")))
                
                # Add current user message
                messages.append(HumanMessage(content=message))
                
                response = await self.model.ainvoke(messages)
                
                return {
                    "response": response.content if hasattr(response, "content") else str(response),
                    "sources": [],
                    "metadata": {"model": os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")}
                }
                
        except Exception as e:
            logger.error(f"Error in LangChain generation: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "sources": [],
                "metadata": {"error": str(e)}
            }
    
    async def stream_response(
        self,
        message: str,
        tools: List[LangChainBaseTool],
        system_prompt: str,
        session_id: str,
        context: Optional[Dict] = None
    ):
        """
        Stream response (for future implementation)
        """
        # TODO: Implement streaming
        raise NotImplementedError("Streaming not yet implemented")

