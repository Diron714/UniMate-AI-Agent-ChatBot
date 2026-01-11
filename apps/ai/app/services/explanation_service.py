"""
Explanation Service
Generates LLM-powered explanations for Z-score predictions
"""
import os
import logging
from typing import Dict, Any, List
from app.services.gemini_service import get_gemini_model

logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Service for generating explanations using Gemini
    """
    
    def __init__(self):
        self.model = get_gemini_model()
    
    def generate_zscore_explanation(
        self,
        z_score: float,
        stream: str,
        district: str,
        safe_courses: List[Dict[str, Any]],
        probable_courses: List[Dict[str, Any]],
        reach_courses: List[Dict[str, Any]]
    ) -> str:
        """
        Generate LLM explanation for Z-score predictions
        
        Args:
            z_score: Student's Z-score
            stream: A/L stream
            district: Student's district
            safe_courses: List of safe course predictions
            probable_courses: List of probable course predictions
            reach_courses: List of reach course predictions
        
        Returns:
            Explanation string
        """
        if not self.model:
            # Fallback explanation if Gemini is not available
            return self._generate_fallback_explanation(
                z_score, stream, district, safe_courses, probable_courses, reach_courses
            )
        
        try:
            # Build prompt for explanation
            prompt = self._build_explanation_prompt(
                z_score, stream, district, safe_courses, probable_courses, reach_courses
            )
            
            # Generate explanation
            response = self.model.generate_content(prompt)
            explanation = response.text.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}", exc_info=True)
            # Fallback to simple explanation
            return self._generate_fallback_explanation(
                z_score, stream, district, safe_courses, probable_courses, reach_courses
            )
    
    def _build_explanation_prompt(
        self,
        z_score: float,
        stream: str,
        district: str,
        safe_courses: List[Dict[str, Any]],
        probable_courses: List[Dict[str, Any]],
        reach_courses: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM explanation"""
        
        prompt = f"""You are UniMate, Sri Lanka's official university guidance AI. Generate a clear, helpful explanation for a student's Z-score prediction results.

Student Information:
- Z-Score: {z_score}
- Stream: {stream}
- District: {district}

Course Predictions:

SAFE COURSES (Z-score well above average cut-off):
"""
        
        if safe_courses:
            for course in safe_courses[:5]:  # Top 5 for explanation
                prompt += f"- {course.get('course', 'Unknown')} at {course.get('university', 'Unknown')} (Avg cut-off: {course.get('avg_cutoff', 0)}, Trend: {course.get('trend', 'stable')})\n"
        else:
            prompt += "- None\n"
        
        prompt += "\nPROBABLE COURSES (Z-score close to or above average cut-off):\n"
        if probable_courses:
            for course in probable_courses[:5]:
                prompt += f"- {course.get('course', 'Unknown')} at {course.get('university', 'Unknown')} (Avg cut-off: {course.get('avg_cutoff', 0)}, Trend: {course.get('trend', 'stable')})\n"
        else:
            prompt += "- None\n"
        
        prompt += "\nREACH COURSES (Z-score below average but within range):\n"
        if reach_courses:
            for course in reach_courses[:3]:
                prompt += f"- {course.get('course', 'Unknown')} at {course.get('university', 'Unknown')} (Avg cut-off: {course.get('avg_cutoff', 0)}, Trend: {course.get('trend', 'stable')})\n"
        else:
            prompt += "- None\n"
        
        prompt += """
Generate a comprehensive explanation that:
1. Explains what the categories mean (Safe, Probable, Reach)
2. Analyzes trends (increasing/stable/decreasing cut-offs) and what they mean
3. Provides actionable advice for the student
4. Mentions district-specific considerations if relevant
5. Is encouraging and supportive
6. Is written in clear, simple language (can be in Sinhala, Tamil, or English)

Keep the explanation concise (2-3 paragraphs) but informative.
"""
        
        return prompt
    
    def _generate_fallback_explanation(
        self,
        z_score: float,
        stream: str,
        district: str,
        safe_courses: List[Dict[str, Any]],
        probable_courses: List[Dict[str, Any]],
        reach_courses: List[Dict[str, Any]]
    ) -> str:
        """Generate fallback explanation without LLM"""
        
        explanation = f"Based on your Z-score of {z_score} in the {stream} stream"
        if district:
            explanation += f" from {district} district"
        explanation += ", here are your course predictions:\n\n"
        
        if safe_courses:
            explanation += f"**Safe Courses ({len(safe_courses)}):** Your Z-score is well above the average cut-off for these courses, making them highly likely options. "
            explanation += f"Top recommendations include {safe_courses[0].get('course', 'courses')} at {safe_courses[0].get('university', 'universities')}.\n\n"
        
        if probable_courses:
            explanation += f"**Probable Courses ({len(probable_courses)}):** Your Z-score is close to or above the average cut-off. These are good options to consider. "
            explanation += f"Keep in mind that cut-off trends may vary, so stay updated with the latest information.\n\n"
        
        if reach_courses:
            explanation += f"**Reach Courses ({len(reach_courses)}):** Your Z-score is below the average cut-off but within a reasonable range. "
            explanation += "These courses are more competitive, but still possible depending on the year's competition level.\n\n"
        
        explanation += "Remember: Cut-off scores can vary from year to year. Always check the latest UGC announcements and consider multiple options when making your choices."
        
        return explanation

