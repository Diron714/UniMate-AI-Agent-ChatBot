"""
Z-Score Prediction Endpoint
Predicts eligible courses based on Z-score using historical cut-off data
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from app.tools.zscore_predict_tool import ZScorePredictTool
from app.services.explanation_service import ExplanationService
from app.config.db import MongoDBConnection

logger = logging.getLogger(__name__)

router = APIRouter() // router

# Initialize services
zscore_tool = ZScorePredictTool()
explanation_service = ExplanationService()


class ZScoreRequest(BaseModel):
    stream: str
    district: Optional[str] = None
    z_score: float
    userId: Optional[str] = None  # For storing prediction history


class CoursePrediction(BaseModel):
    course: str
    university: str
    avg_cutoff: float
    min_cutoff: float
    max_cutoff: float
    years_data: int
    trend: str  # increasing, stable, decreasing
    district: str


class ZScoreResponse(BaseModel):
    status: str = "success"  # For compatibility with test expectations
    success: bool = True
    input: Optional[Dict] = None  # Input parameters for reference
    safe: List[CoursePrediction] = []
    probable: List[CoursePrediction] = []
    reach: List[CoursePrediction] = []
    explanation: str
    message: str


@router.post("/zscore")
async def zscore_prediction(request: ZScoreRequest):
    """
    Predict eligible courses based on Z-score
    
    Uses historical cut-off data to categorize courses into:
    - Safe: z_score > (avg_cutoff + 0.5)
    - Probable: z_score between (avg_cutoff - 0.3) and (avg_cutoff + 0.5)
    - Reach: z_score < (avg_cutoff - 0.3) but within 1.0 range
    """
    try:
        # Validate input
        if not request.stream:
            raise HTTPException(status_code=400, detail="Stream is required")
        
        if request.z_score < -5 or request.z_score > 5:
            raise HTTPException(status_code=400, detail="Z-score must be between -5 and 5")
        
        # Normalize stream
        stream_map = {
            "science": "Maths",
            "mathematics": "Maths",
            "biology": "Bio",
            "biological": "Bio",
            "commerce": "Commerce",
            "arts": "Arts",
            "technology": "Technology",
            "tech": "Technology"
        }
        stream_normalized = stream_map.get(request.stream.lower(), request.stream.strip().title())
        
        valid_streams = ["Bio", "Maths", "Arts", "Commerce", "Technology"]
        if stream_normalized not in valid_streams:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stream. Must be one of: {', '.join(valid_streams)}"
            )
        
        # Get predictions from tool
        result = zscore_tool.execute(
            z_score=request.z_score,
            stream=stream_normalized,
            district=request.district
        )
        
        if not result.get("success", False):
            error_message = result.get("message", "No predictions available")
            # If MongoDB is not connected, return 503 (Service Unavailable)
            if "unavailable" in error_message.lower() or "not connected" in error_message.lower():
                raise HTTPException(
                    status_code=503,
                    detail=error_message
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=error_message
                )
        
        # Generate LLM explanation (synchronous call)
        try:
            explanation = explanation_service.generate_zscore_explanation(
                z_score=request.z_score,
                stream=stream_normalized,
                district=request.district or "All districts",
                safe_courses=result.get("safe", []),
                probable_courses=result.get("probable", []),
                reach_courses=result.get("reach", [])
            )
        except Exception as e:
            logger.warning(f"Failed to generate LLM explanation: {e}")
            explanation = f"Based on your Z-score of {request.z_score} in the {stream_normalized} stream, you have {len(result.get('safe', []))} safe courses, {len(result.get('probable', []))} probable courses, and {len(result.get('reach', []))} reach courses."
        
        # Store prediction in user history (if userId provided)
        if request.userId:
            try:
                db = MongoDBConnection.get_db()
                if db is not None:
                    predictions_collection = db.get_collection("zscore_predictions")
                    from datetime import datetime
                    predictions_collection.insert_one({
                        "userId": request.userId,
                        "z_score": request.z_score,
                        "stream": stream_normalized,
                        "district": request.district,
                        "result": {
                            "safe_count": len(result.get("safe", [])),
                            "probable_count": len(result.get("probable", [])),
                            "reach_count": len(result.get("reach", []))
                        },
                        "createdAt": datetime.now()
                    })
            except Exception as e:
                logger.warning(f"Failed to store prediction history: {e}")
        
        # Format response
        return ZScoreResponse(
            status="success",
            success=True,
            input={
                "stream": stream_normalized,
                "district": request.district or "All districts",
                "z_score": request.z_score
            },
            safe=[CoursePrediction(**course) for course in result.get("safe", [])],
            probable=[CoursePrediction(**course) for course in result.get("probable", [])],
            reach=[CoursePrediction(**course) for course in result.get("reach", [])],
            explanation=explanation,
            message=result.get("message", "Predictions generated successfully")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Z-score prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

