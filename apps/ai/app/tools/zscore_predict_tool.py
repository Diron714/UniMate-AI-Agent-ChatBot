"""
Z-Score Prediction Tool
Predicts eligible courses based on Z-score using historical cut-off data
"""
from typing import Dict, Any, List, Optional
from app.tools.base_tool import BaseTool
from app.models.cutoff import CutoffModel
from app.config.db import MongoDBConnection
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class ZScorePredictTool(BaseTool):
    """
    Tool for predicting eligible courses based on Z-score and historical cut-off data
    """
    
    def __init__(self):
        super().__init__(
            name="zscore_predict",
            description="Predicts which courses a student is eligible for based on their Z-score, stream, and district using historical cut-off data. Use this when the user provides their Z-score or asks about course eligibility."
        )
        self.cutoff_model = CutoffModel()
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "z_score": {
                    "type": "number",
                    "description": "The student's Z-score"
                },
                "stream": {
                    "type": "string",
                    "description": "A/L stream",
                    "enum": ["Bio", "Maths", "Arts", "Commerce", "Technology"]
                },
                "district": {
                    "type": "string",
                    "description": "Student's district (optional but recommended for better predictions)"
                }
            },
            "required": ["z_score", "stream"]
        }
    
    def execute(
        self,
        z_score: float = 0.0,
        stream: str = "",
        district: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict eligible courses based on Z-score using historical cut-off data
        
        Args:
            z_score: Student's Z-score
            stream: A/L stream (Bio, Maths, Arts, Commerce, Technology)
            district: Student's district (optional)
        
        Returns:
            Dict with course predictions categorized by safety level
        """
        if not stream:
            return {
                "success": False,
                "safe": [],
                "probable": [],
                "reach": [],
                "message": "Stream is required for prediction"
            }
        
        if self.cutoff_model.collection is None:
            logger.warning("Z-Score Predict Tool: MongoDB not connected")
            return {
                "success": False,
                "safe": [],
                "probable": [],
                "reach": [],
                "message": "Prediction service is currently unavailable"
            }
        
        try:
            # Get historical cut-offs (last 5 years)
            historical_cutoffs = self.cutoff_model.get_historical_cutoffs(
                stream=stream,
                district=district,
                years=5
            )
            
            if not historical_cutoffs:
                return {
                    "success": False,
                    "safe": [],
                    "probable": [],
                    "reach": [],
                    "message": f"No historical cut-off data found for {stream} stream. Please ensure cut-off data has been seeded."
                }
            
            # Group cut-offs by course and university
            course_groups = defaultdict(list)
            for cutoff in historical_cutoffs:
                key = (cutoff.get("course", ""), cutoff.get("university", ""))
                course_groups[key].append(cutoff)
            
            # Categorize courses
            safe_courses = []
            probable_courses = []
            reach_courses = []
            
            for (course, university), cutoffs in course_groups.items():
                if not course or not university:
                    continue
                
                # Calculate average cut-off
                scores = [c.get("cutoff_zscore", 0) for c in cutoffs if c.get("cutoff_zscore")]
                if not scores:
                    continue
                
                avg_cutoff = sum(scores) / len(scores)
                min_cutoff = min(scores)
                max_cutoff = max(scores)
                
                # Get trend
                trend = self.cutoff_model.get_trend(stream, course, university, district, years=5)
                
                # Build course info
                course_info = {
                    "course": course,
                    "university": university,
                    "avg_cutoff": round(avg_cutoff, 2),
                    "min_cutoff": round(min_cutoff, 2),
                    "max_cutoff": round(max_cutoff, 2),
                    "years_data": len(cutoffs),
                    "trend": trend,
                    "district": district if district else "All districts"
                }
                
                # Categorize based on Z-score vs average cut-off
                # Safe: z_score > (avg_cutoff + 0.5)
                # Probable: z_score between (avg_cutoff - 0.3) and (avg_cutoff + 0.5)
                # Reach: z_score < (avg_cutoff - 0.3)
                
                if z_score > (avg_cutoff + 0.5):
                    # Safe: Z-score is well above average
                    safe_courses.append(course_info)
                elif z_score >= (avg_cutoff - 0.3):
                    # Probable: Z-score is close to or above average
                    probable_courses.append(course_info)
                else:
                    # Reach: Z-score is below average but might still be possible
                    if z_score >= (avg_cutoff - 1.0):  # Only include if within 1.0
                        reach_courses.append(course_info)
            
            # Sort by average cut-off (descending for safe, ascending for reach)
            safe_courses.sort(key=lambda x: x.get("avg_cutoff", 0), reverse=True)
            probable_courses.sort(key=lambda x: x.get("avg_cutoff", 0), reverse=True)
            reach_courses.sort(key=lambda x: x.get("avg_cutoff", 0))
            
            # Limit results
            safe_courses = safe_courses[:15]
            probable_courses = probable_courses[:15]
            reach_courses = reach_courses[:10]
            
            return {
                "success": True,
                "safe": safe_courses,
                "probable": probable_courses,
                "reach": reach_courses,
                "message": f"Found {len(safe_courses)} safe, {len(probable_courses)} probable, and {len(reach_courses)} reach courses based on historical data"
            }
            
        except Exception as e:
            logger.error(f"Z-Score Predict Tool error: {e}", exc_info=True)
            return {
                "success": False,
                "safe": [],
                "probable": [],
                "reach": [],
                "message": f"Prediction error: {str(e)}"
            }

