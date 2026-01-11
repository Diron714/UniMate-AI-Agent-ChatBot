"""
Chat Endpoint Handler
Main endpoint for AI conversations with LangChain integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import logging
from pathlib import Path

from app.services.langchain_service import LangChainService
from app.services.memory_service import MemoryService
from app.services.context_service import ContextService
from app.tools import (
    DetectUniversityTool,
    UGCSearchTool,
    ZScorePredictTool,
    RuleEngineTool,
    MemoryStoreTool
)
from app.tools.tool_wrapper import LangChainToolWrapper
from app.config.db import MongoDBConnection

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
langchain_service = None
memory_service = MemoryService()
context_service = ContextService()

def get_langchain_service():
    """Get or initialize LangChain service"""
    global langchain_service
    if langchain_service is None:
        try:
            langchain_service = LangChainService()
        except Exception as e:
            logger.error(f"Failed to initialize LangChain service: {e}")
            raise
    return langchain_service

def load_system_prompt() -> str:
    """Load system prompt from file"""
    try:
        # Try multiple possible paths
        prompt_paths = [
            Path(__file__).parent.parent.parent.parent / "packages" / "prompts" / "system_prompt.txt",
            Path(__file__).parent.parent.parent / "packages" / "prompts" / "system_prompt.txt",
            Path("packages") / "prompts" / "system_prompt.txt",
        ]
        
        for path in prompt_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
        
        # Fallback to default prompt
        logger.warning("System prompt file not found, using default")
        return """You are UniMate, Sri Lanka's official AI-powered university guidance companion.

Your role is to help students navigate their university journey from A/L results to graduation.

CRITICAL RULES:
1. Use ONLY verified information from UGC handbooks and official university documents
2. If you don't know something, say "I don't know" and suggest contacting the university
3. Never guess or hallucinate information
4. Always cite your sources when providing information
5. Be empathetic, clear, and helpful
6. Support Sinhala, Tamil, and English languages
7. Remember user context (university, course, stage)

When answering:
- Be specific and accurate
- Explain reasoning when possible
- Provide actionable advice
- Escalate sensitive matters to appropriate authorities

You are a trusted advisor, not just a chatbot."""
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return "You are UniMate, Sri Lanka's official AI-powered university guidance companion."

def get_tools() -> List:
    """Get all available tools as LangChain tools"""
    try:
        # Initialize tools
        tools = [
            DetectUniversityTool(),
            UGCSearchTool(),
            ZScorePredictTool(),
            RuleEngineTool(),
            MemoryStoreTool(),
        ]
        
        # Convert to LangChain tools
        langchain_tools = [LangChainToolWrapper(tool) for tool in tools]
        
        return langchain_tools
    except Exception as e:
        logger.error(f"Error initializing tools: {e}", exc_info=True)
        return []

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict] = {}
    userId: str
    sessionId: str

class ChatResponse(BaseModel):
    message: str
    sources: List[str] = []
    context: Optional[Dict] = {}

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for AI conversations
    
    Receives:
    - message: User's message
    - context: User context (university, stage, preferences)
    - userId: User ID
    - sessionId: Session ID for conversation history
    
    Returns:
    - message: AI response
    - sources: List of sources used
    - context: Updated context
    """
    try:
        # Validate request
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not request.userId:
            raise HTTPException(status_code=400, detail="userId is required")
        
        if not request.sessionId:
            raise HTTPException(status_code=400, detail="sessionId is required")
        
        # Initialize services
        try:
            service = get_langchain_service()
        except Exception as e:
            logger.error(f"LangChain service initialization failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="AI service is currently unavailable. Please try again later."
            )
        
        # Load system prompt
        system_prompt = load_system_prompt()
        
        # Get tools
        tools = get_tools()
        
        # Load user memory from MongoDB
        user_context = {}
        try:
            user_context = memory_service.get_context(
                userId=request.userId,
                sessionId=request.sessionId
            )
            logger.info(f"Loaded context for user {request.userId}: university={user_context.get('university')}, stage={user_context.get('stage')}")
        except Exception as e:
            logger.warning(f"Failed to load user memory: {e}")
            user_context = {
                "university": None,
                "course": None,
                "stage": None,
                "preferences": {},
                "conversation_history": []
            }
        
        # Detect and update context from current message
        try:
            user_context = context_service.update_context(
                message=request.message,
                current_context=user_context
            )
            
            # If university was detected, update memory
            detected_university = context_service.detect_university(request.message)
            if detected_university:
                if detected_university != user_context.get("university"):
                    success = memory_service.update_long_term(
                        userId=request.userId,
                        sessionId=request.sessionId,
                        university=detected_university
                    )
                    if success:
                        user_context["university"] = detected_university
                        logger.info(f"Updated university context: {detected_university}")
                    else:
                        logger.warning(f"Failed to update university in memory: {detected_university}")
                else:
                    # University already in context, ensure it's set
                    user_context["university"] = detected_university
            
            # If stage was detected, update memory
            detected_stage = context_service.detect_stage(request.message)
            if detected_stage:
                if detected_stage != user_context.get("stage"):
                    success = memory_service.update_long_term(
                        userId=request.userId,
                        sessionId=request.sessionId,
                        stage=detected_stage
                    )
                    if success:
                        user_context["stage"] = detected_stage
                        logger.info(f"Updated stage context: {detected_stage}")
                    else:
                        logger.warning(f"Failed to update stage in memory: {detected_stage}")
                else:
                    # Stage already in context, ensure it's set
                    user_context["stage"] = detected_stage
            
            # If course was detected, update memory
            detected_course = context_service.detect_course(request.message)
            if detected_course:
                if detected_course != user_context.get("course"):
                    success = memory_service.update_long_term(
                        userId=request.userId,
                        sessionId=request.sessionId,
                        course=detected_course
                    )
                    if success:
                        user_context["course"] = detected_course
                        logger.info(f"Updated course context: {detected_course}")
                    else:
                        logger.warning(f"Failed to update course in memory: {detected_course}")
                else:
                    # Course already in context, ensure it's set
                    user_context["course"] = detected_course
                    
        except Exception as e:
            logger.warning(f"Failed to detect/update context: {e}")
        
        # Merge with request context (request context takes precedence, but don't overwrite with None)
        request_context = request.context if isinstance(request.context, dict) else {}
        # Only merge non-None values from request_context to preserve memory values
        context = user_context.copy()
        for key, value in request_context.items():
            if value is not None:  # Only overwrite if request has a non-None value
                context[key] = value
        
        # Get conversation history from memory
        conversation_history = user_context.get("conversation_history", [])
        
        # Add current user message to short-term memory
        try:
            memory_service.add_to_short_term(
                userId=request.userId,
                sessionId=request.sessionId,
                role="user",
                content=request.message
            )
        except Exception as e:
            logger.warning(f"Failed to add message to short-term memory: {e}")
        
        # Enhance system prompt with user context
        enhanced_prompt = system_prompt
        if context.get("university"):
            enhanced_prompt += f"\n\nIMPORTANT CONTEXT: The user is associated with {context['university']}. All answers should be specific to this university when relevant."
        if context.get("stage"):
            enhanced_prompt += f"\n\nUSER STAGE: The user is at the '{context['stage']}' stage of their university journey."
        if context.get("course"):
            enhanced_prompt += f"\n\nUSER COURSE: The user is interested in or enrolled in {context['course']}."
        
        # Generate response using LangChain
        try:
            result = await service.generate_with_tools(
                message=request.message,
                tools=tools,
                system_prompt=enhanced_prompt,
                session_id=request.sessionId,
                context=context,
                conversation_history=conversation_history
            )
            
            response_text = result.get("response", "I apologize, but I couldn't generate a response.")
            sources = result.get("sources", [])
            
            # Add assistant response to short-term memory
            try:
                memory_service.add_to_short_term(
                    userId=request.userId,
                    sessionId=request.sessionId,
                    role="assistant",
                    content=response_text
                )
            except Exception as e:
                logger.warning(f"Failed to add assistant response to memory: {e}")
            
            # AI service is stateless - backend API is the single source of truth
            # Do NOT store conversations here - backend handles all persistence
            
            # Ensure context is properly formatted before returning
            # Reload context from memory to ensure we have the latest values
            try:
                final_context = memory_service.get_context(
                    userId=request.userId,
                    sessionId=request.sessionId
                )
                # Merge with current context (current context takes precedence for newly detected values)
                for key, value in context.items():
                    if value is not None:
                        final_context[key] = value
                context = final_context
            except Exception as e:
                logger.warning(f"Failed to reload context from memory: {e}")
                # Use existing context if reload fails
            
            # Return response with updated context
            logger.info(f"Returning context: university={context.get('university')}, stage={context.get('stage')}, course={context.get('course')}")
            return ChatResponse(
                message=response_text,
                sources=sources,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            
            # Graceful degradation: return "I don't know" response
            return ChatResponse(
                message="I apologize, but I'm having trouble processing your request right now. Please try again, or contact your university directly for assistance.",
                sources=[],
                context=request.context
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )

