"""
Quick test script to verify MongoDB cut-off data exists
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.cutoff import CutoffModel

def main():
    cutoff_model = CutoffModel()
    count = cutoff_model.count()
    print(f"Records: {count}")
    
    if count > 3000:
        print("✅ Data is loaded correctly")
        return 0
    elif count > 0:
        print(f"⚠️ Only {count} records found (expected > 3000)")
        return 1
    else:
        print("❌ No data found. Please seed the database.")
        return 1

if __name__ == "__main__":
    exit(main())

