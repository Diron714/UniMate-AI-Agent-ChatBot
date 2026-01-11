"""
UniMate AI Agent - FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging

from app.routes import chat, zscore, university
from app.config.db import MongoDBConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = FastAPI(
    title="UniMate AI Agent",
    description="AI-powered university guidance system for Sri Lanka",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: Connect to MongoDB
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting UniMate AI Agent...")
    try:
        db = MongoDBConnection.connect()
        if db is not None:
            logger.info("✅ MongoDB connected successfully")
        else:
            logger.warning("⚠️ MongoDB connection failed - some features may not work")
        
        # Initialize ZScore tool to verify it works
        try:
            from app.tools.zscore_predict_tool import ZScorePredictTool
            zscore_tool = ZScorePredictTool()
            logger.info("✅ ZScore tool initialized")
        except Exception as e:
            logger.warning(f"⚠️ ZScore tool initialization warning: {e}")
            
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

# Shutdown event: Disconnect from MongoDB
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down UniMate AI Agent...")
    MongoDBConnection.disconnect()

# Health check
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "UniMate AI Agent Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check MongoDB (optional for AI service)
        db_status = "disconnected"
        try:
            db = MongoDBConnection.get_db()
            db_status = "connected" if db else "disconnected"
        except:
            pass  # MongoDB is optional for AI service
        
        # Check if Gemini API key is set
        gemini_status = "configured" if os.getenv("GEMINI_API_KEY") else "not_configured"
        
        # Determine overall health
        overall_status = "healthy" if gemini_status == "configured" else "degraded"
        
        return {
            "status": overall_status,
            "database": db_status,
            "gemini_api": gemini_status
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e) if os.getenv("NODE_ENV") == "development" else "Service error"
        }

# Routes
app.include_router(chat.router, prefix="/ai", tags=["chat"])
app.include_router(zscore.router, prefix="/ai", tags=["zscore"])
app.include_router(university.router, prefix="/ai", tags=["university"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

