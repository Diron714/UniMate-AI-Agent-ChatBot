"""
Cut-off Data Model
Stores historical Z-score cut-off data for course predictions
"""
from typing import Optional
from datetime import datetime
import logging

from app.config.db import MongoDBConnection

logger = logging.getLogger(__name__)


class CutoffModel:
    """
    Model for managing cut-off data in MongoDB
    """
    
    def __init__(self, collection_name: str = "cutoffs"):
        """
        Initialize cut-off model
        
        Args:
            collection_name: Name of MongoDB collection
        """
        self.collection_name = collection_name
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB and get collection"""
        try:
            self.db = MongoDBConnection.get_db()
            if self.db is None:
                logger.warning("MongoDB not connected. Cutoff model operations will fail.")
                return
            
            self.collection = self.db[self.collection_name]
            self._ensure_indexes()
            logger.info(f"Cutoff model connected to collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}", exc_info=True)
            self.db = None
            self.collection = None
    
    def _ensure_indexes(self):
        """Create indexes for efficient queries"""
        if self.collection is None:
            return
        
        try:
            # Index on year, stream, district for fast lookups
            self.collection.create_index([("year", -1), ("stream", 1), ("district", 1)])
            # Index on course and university for grouping
            self.collection.create_index([("course", 1), ("university", 1)])
            # Index on stream for filtering
            self.collection.create_index([("stream", 1)])
            # Index on year for historical queries
            self.collection.create_index([("year", -1)])
            logger.info("Cutoff model indexes created")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    def insert_cutoff(
        self,
        year: int,
        stream: str,
        district: str,
        course: str,
        university: str,
        cutoff_zscore: float,
        quota_type: str = "merit"
    ) -> bool:
        """
        Insert a single cut-off record
        
        Args:
            year: Year of the cut-off
            stream: A/L stream (Bio, Maths, Arts, Commerce, Technology)
            district: District name
            course: Course name
            university: University name
            cutoff_zscore: Cut-off Z-score
            quota_type: Type of quota (merit, district)
        
        Returns:
            True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return False
        
        try:
            # Normalize stream name
            stream_normalized = stream.strip().title()
            
            # Validate stream
            valid_streams = ["Bio", "Maths", "Arts", "Commerce", "Technology"]
            if stream_normalized not in valid_streams:
                logger.debug(f"Normalizing stream: {stream}")
                # Map common variations (including full names from UGC data)
                stream_map = {
                    # Maths/Physical Science variations
                    "science": "Maths",
                    "mathematics": "Maths",
                    "maths": "Maths",
                    "mathematical": "Maths",
                    "physical science": "Maths",
                    "physical": "Maths",
                    # Bio/Biological Science variations
                    "biology": "Bio",
                    "biological": "Bio",
                    "biological science": "Bio",
                    "bio science": "Bio",
                    "bio": "Bio",
                    "indigenous medicine": "Bio",
                    "paramedical": "Bio",
                    # Commerce/Management variations
                    "commerce": "Commerce",
                    "commercial": "Commerce",
                    "management": "Commerce",
                    # Arts variations
                    "arts": "Arts",
                    "art": "Arts",
                    # Technology variations
                    "technology": "Technology",
                    "tech": "Technology",
                    "technological": "Technology"
                }
                stream_normalized = stream_map.get(stream.lower().strip(), None)
                # If still not valid, skip this record
                if stream_normalized not in valid_streams:
                    logger.warning(f"Invalid stream: {stream}. Skipping record.")
                    return False
            
            document = {
                "year": year,
                "stream": stream_normalized,
                "district": district.strip(),
                "course": course.strip(),
                "university": university.strip(),
                "cutoff_zscore": float(cutoff_zscore),
                "quota_type": quota_type.strip().lower(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Check if record already exists
            existing = self.collection.find_one({
                "year": year,
                "stream": stream_normalized,
                "district": district.strip(),
                "course": course.strip(),
                "university": university.strip(),
                "quota_type": quota_type.strip().lower()
            })
            
            if existing:
                # Update existing record
                self.collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "cutoff_zscore": float(cutoff_zscore),
                        "updated_at": datetime.now()
                    }}
                )
                logger.debug(f"Updated cut-off: {year} {stream_normalized} {course}")
            else:
                # Insert new record
                self.collection.insert_one(document)
                logger.debug(f"Inserted cut-off: {year} {stream_normalized} {course}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error inserting cut-off: {e}", exc_info=True)
            return False
    
    def get_historical_cutoffs(
        self,
        stream: str,
        district: Optional[str] = None,
        years: int = 5
    ) -> list:
        """
        Get historical cut-off data for the last N years
        
        Args:
            stream: A/L stream
            district: District name (optional)
            years: Number of years to retrieve (default: 5)
        
        Returns:
            List of cut-off documents
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return []
        
        try:
            # Normalize stream
            stream_normalized = stream.strip().title()
            
            # Calculate year range
            current_year = datetime.now().year
            start_year = current_year - years
            
            # Build query
            query = {
                "year": {"$gte": start_year, "$lte": current_year},
                "stream": stream_normalized
            }
            
            if district:
                query["district"] = district.strip()
            
            # Get cut-offs sorted by year (descending)
            cutoffs = list(self.collection.find(query).sort("year", -1))
            
            logger.info(f"Retrieved {len(cutoffs)} cut-off records for {stream_normalized}")
            return cutoffs
            
        except Exception as e:
            logger.error(f"Error getting historical cutoffs: {e}", exc_info=True)
            return []
    
    def get_course_cutoffs(
        self,
        stream: str,
        course: Optional[str] = None,
        university: Optional[str] = None,
        years: int = 5
    ) -> list:
        """
        Get cut-off data for specific course/university
        
        Args:
            stream: A/L stream
            course: Course name (optional)
            university: University name (optional)
            years: Number of years to retrieve
        
        Returns:
            List of cut-off documents
        """
        if self.collection is None:
            logger.error("MongoDB not connected")
            return []
        
        try:
            stream_normalized = stream.strip().title()
            current_year = datetime.now().year
            start_year = current_year - years
            
            query = {
                "year": {"$gte": start_year, "$lte": current_year},
                "stream": stream_normalized
            }
            
            if course:
                query["course"] = {"$regex": course.strip(), "$options": "i"}
            
            if university:
                query["university"] = {"$regex": university.strip(), "$options": "i"}
            
            cutoffs = list(self.collection.find(query).sort("year", -1))
            return cutoffs
            
        except Exception as e:
            logger.error(f"Error getting course cutoffs: {e}", exc_info=True)
            return []
    
    def get_average_cutoff(
        self,
        stream: str,
        course: str,
        university: str,
        district: Optional[str] = None,
        years: int = 5
    ) -> Optional[float]:
        """
        Calculate average cut-off Z-score for a course
        
        Args:
            stream: A/L stream
            course: Course name
            university: University name
            district: District name (optional)
            years: Number of years to consider
        
        Returns:
            Average cut-off Z-score or None
        """
        cutoffs = self.get_course_cutoffs(stream, course, university, years)
        
        if not cutoffs:
            return None
        
        # Filter by district if provided
        if district:
            cutoffs = [c for c in cutoffs if c.get("district", "").lower() == district.strip().lower()]
        
        if not cutoffs:
            return None
        
        # Calculate average
        scores = [c.get("cutoff_zscore", 0) for c in cutoffs if c.get("cutoff_zscore")]
        if not scores:
            return None
        
        avg_score = sum(scores) / len(scores)
        return round(avg_score, 2)
    
    def get_trend(
        self,
        stream: str,
        course: str,
        university: str,
        district: Optional[str] = None,
        years: int = 5
    ) -> str:
        """
        Determine trend (increasing, stable, decreasing) for a course
        
        Args:
            stream: A/L stream
            course: Course name
            university: University name
            district: District name (optional)
            years: Number of years to analyze
        
        Returns:
            Trend string: "increasing", "stable", or "decreasing"
        """
        cutoffs = self.get_course_cutoffs(stream, course, university, years)
        
        if not cutoffs or len(cutoffs) < 2:
            return "stable"
        
        # Filter by district if provided
        if district:
            cutoffs = [c for c in cutoffs if c.get("district", "").lower() == district.strip().lower()]
        
        if len(cutoffs) < 2:
            return "stable"
        
        # Sort by year
        cutoffs.sort(key=lambda x: x.get("year", 0))
        
        # Get first and last scores
        first_score = cutoffs[0].get("cutoff_zscore", 0)
        last_score = cutoffs[-1].get("cutoff_zscore", 0)
        
        # Calculate change
        change = last_score - first_score
        
        if change > 0.1:
            return "increasing"
        elif change < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def count(self) -> int:
        """
        Count total number of cut-off records
        
        Returns:
            Total count of records
        """
        if self.collection is None:
            return 0
        
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Error counting cutoffs: {e}", exc_info=True)
            return 0

