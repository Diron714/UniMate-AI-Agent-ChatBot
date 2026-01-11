"""
Cut-off Data Seeding Script
Loads cut-off data from CSV/JSON and stores in MongoDB
"""
import os
import sys
import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.cutoff import CutoffModel
from app.config.db import MongoDBConnection
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def load_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Load cut-off data from CSV file
    
    Expected CSV format:
    year,stream,district,course,university,cutoff_zscore,quota_type
    
    Args:
        file_path: Path to CSV file
    
    Returns:
        List of cut-off dictionaries
    """
    cutoffs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cutoff = {
                        "year": int(row.get("year", 0)),
                        "stream": row.get("stream", "").strip(),
                        "district": row.get("district", "").strip(),
                        "course": row.get("course", "").strip(),
                        "university": row.get("university", "").strip(),
                        "cutoff_zscore": float(row.get("cutoff_zscore", 0)),
                        "quota_type": row.get("quota_type", "merit").strip().lower()
                    }
                    cutoffs.append(cutoff)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid row: {row} - {e}")
                    continue
        
        logger.info(f"Loaded {len(cutoffs)} cut-off records from CSV")
        return cutoffs
        
    except Exception as e:
        logger.error(f"Error loading CSV: {e}", exc_info=True)
        return []


def load_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Load cut-off data from JSON file
    
    Expected JSON format:
    [
        {
            "year": 2023,
            "stream": "Maths",
            "district": "Colombo",
            "course": "Computer Science",
            "university": "University of Colombo",
            "cutoff_zscore": 1.85,
            "quota_type": "merit"
        },
        ...
    ]
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        List of cut-off dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if not isinstance(data, list):
                logger.error("JSON file must contain an array of cut-off objects")
                return []
            
            cutoffs = []
            for item in data:
                try:
                    cutoff = {
                        "year": int(item.get("year", 0)),
                        "stream": str(item.get("stream", "")).strip(),
                        "district": str(item.get("district", "")).strip(),
                        "course": str(item.get("course", "")).strip(),
                        "university": str(item.get("university", "")).strip(),
                        "cutoff_zscore": float(item.get("cutoff_zscore", 0)),
                        "quota_type": str(item.get("quota_type", "merit")).strip().lower()
                    }
                    cutoffs.append(cutoff)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid item: {item} - {e}")
                    continue
            
            logger.info(f"Loaded {len(cutoffs)} cut-off records from JSON")
            return cutoffs
            
    except Exception as e:
        logger.error(f"Error loading JSON: {e}", exc_info=True)
        return []


def validate_cutoff(cutoff: Dict[str, Any]) -> bool:
    """
    Validate a cut-off record
    
    Args:
        cutoff: Cut-off dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["year", "stream", "district", "course", "university", "cutoff_zscore"]
    
    for field in required_fields:
        if field not in cutoff or not cutoff[field]:
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Validate year
    if not isinstance(cutoff["year"], int) or cutoff["year"] < 2000 or cutoff["year"] > 2100:
        logger.warning(f"Invalid year: {cutoff['year']}")
        return False
    
    # Validate stream (will be normalized in insert_cutoff, so just check it's not empty)
    if not cutoff["stream"] or not cutoff["stream"].strip():
        logger.warning(f"Empty stream field")
        return False
    
    # Validate Z-score
    if not isinstance(cutoff["cutoff_zscore"], (int, float)) or cutoff["cutoff_zscore"] < -5 or cutoff["cutoff_zscore"] > 5:
        logger.warning(f"Invalid Z-score: {cutoff['cutoff_zscore']}")
        return False
    
    return True


def seed_cutoffs(cutoffs: List[Dict[str, Any]], cutoff_model: CutoffModel) -> int:
    """
    Seed cut-off data into MongoDB
    
    Args:
        cutoffs: List of cut-off dictionaries
        cutoff_model: CutoffModel instance
    
    Returns:
        Number of successfully inserted records
    """
    if not cutoffs:
        logger.warning("No cut-off data to seed")
        return 0
    
    success_count = 0
    fail_count = 0
    
    for cutoff in cutoffs:
        if not validate_cutoff(cutoff):
            fail_count += 1
            continue
        
        if cutoff_model.insert_cutoff(
            year=cutoff["year"],
            stream=cutoff["stream"],
            district=cutoff["district"],
            course=cutoff["course"],
            university=cutoff["university"],
            cutoff_zscore=cutoff["cutoff_zscore"],
            quota_type=cutoff.get("quota_type", "merit")
        ):
            success_count += 1
        else:
            fail_count += 1
    
    logger.info(f"Seeded {success_count} cut-off records ({fail_count} failed)")
    return success_count


def main():
    """Main seeding function"""
    logger.info("=" * 60)
    logger.info("Cut-off Data Seeding Script")
    logger.info("=" * 60)
    
    # Check MongoDB connection
    db = MongoDBConnection.connect()
    if db is None:
        logger.error("❌ MongoDB connection failed. Please check MONGODB_URI in .env")
        sys.exit(1)
    
    logger.info("✅ MongoDB connected")
    
    # Initialize cut-off model
    cutoff_model = CutoffModel()
    if cutoff_model.collection is None:
        logger.error("❌ Failed to initialize cut-off model")
        sys.exit(1)
    
    logger.info("✅ Cut-off model initialized")
    
    # Find data files
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data" / "cutoffs"
    
    # Allow custom data directory via environment variable
    custom_data_dir = os.getenv("CUTOFF_DATA_DIR")
    if custom_data_dir:
        data_dir = Path(custom_data_dir)
    
    if not data_dir.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        logger.info("Creating data directory...")
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Please add cut-off data files (CSV or JSON) to: {data_dir}")
        logger.info("\nExpected CSV format:")
        logger.info("year,stream,district,course,university,cutoff_zscore,quota_type")
        logger.info("2023,Maths,Colombo,Computer Science,University of Colombo,1.85,merit")
        logger.info("\nOr JSON format: Array of objects with same fields")
        sys.exit(0)
    
    # Find data files
    csv_files = list(data_dir.glob("*.csv"))
    json_files = list(data_dir.glob("*.json"))
    
    if not csv_files and not json_files:
        logger.warning(f"No CSV or JSON files found in {data_dir}")
        logger.info("Please add cut-off data files to the data directory")
        sys.exit(0)
    
    # Load and seed data
    all_cutoffs = []
    
    # Load from CSV files
    for csv_file in csv_files:
        logger.info(f"Loading from CSV: {csv_file.name}")
        cutoffs = load_from_csv(str(csv_file))
        all_cutoffs.extend(cutoffs)
    
    # Load from JSON files
    for json_file in json_files:
        logger.info(f"Loading from JSON: {json_file.name}")
        cutoffs = load_from_json(str(json_file))
        all_cutoffs.extend(cutoffs)
    
    if not all_cutoffs:
        logger.warning("No valid cut-off data loaded")
        sys.exit(0)
    
    logger.info(f"\nTotal cut-off records loaded: {len(all_cutoffs)}")
    logger.info("-" * 60)
    
    # Seed data
    success_count = seed_cutoffs(all_cutoffs, cutoff_model)
    
    # Summary
    logger.info("=" * 60)
    logger.info("Seeding Summary")
    logger.info("=" * 60)
    logger.info(f"Total records loaded: {len(all_cutoffs)}")
    logger.info(f"✅ Successfully seeded: {success_count}")
    logger.info(f"❌ Failed: {len(all_cutoffs) - success_count}")
    logger.info("=" * 60)
    
    if success_count > 0:
        logger.info("✅ Cut-off data seeding completed successfully!")
    else:
        logger.warning("⚠️ No cut-off data was successfully seeded")


if __name__ == "__main__":
    main()

