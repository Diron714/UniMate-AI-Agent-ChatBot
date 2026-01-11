# Z-Score Prediction System

Complete implementation of Z-score-based course prediction system using historical cut-off data.

## Overview

The Z-score prediction system helps students understand which university courses they're eligible for based on their A/L Z-score, stream, and district. It uses historical cut-off data from the last 5 years to categorize courses into Safe, Probable, and Reach categories.

## Components

### 1. Cut-off Data Model (`app/models/cutoff.py`)

**Purpose:** Manages cut-off data in MongoDB

**Features:**
- `insert_cutoff()` - Insert/update cut-off records
- `get_historical_cutoffs()` - Get cut-offs for last N years
- `get_course_cutoffs()` - Get cut-offs for specific course/university
- `get_average_cutoff()` - Calculate average cut-off
- `get_trend()` - Determine trend (increasing/stable/decreasing)

**Schema:**
```python
{
    "year": int,
    "stream": string,  # Bio, Maths, Arts, Commerce, Technology
    "district": string,
    "course": string,
    "university": string,
    "cutoff_zscore": float,
    "quota_type": string,  # merit, district
    "created_at": datetime,
    "updated_at": datetime
}
```

### 2. Z-Score Predictor Tool (`app/tools/zscore_predict_tool.py`)

**Purpose:** Predicts eligible courses based on Z-score

**Input:**
- `z_score`: Student's Z-score
- `stream`: A/L stream (Bio, Maths, Arts, Commerce, Technology)
- `district`: Student's district (optional)

**Categorization Logic:**
- **Safe:** `z_score > (avg_cutoff + 0.5)` - Well above average
- **Probable:** `z_score between (avg_cutoff - 0.3) and (avg_cutoff + 0.5)` - Close to average
- **Reach:** `z_score < (avg_cutoff - 0.3)` but within 1.0 range - Below average but possible

**Output:**
```python
{
    "success": bool,
    "safe": [CourseInfo],
    "probable": [CourseInfo],
    "reach": [CourseInfo],
    "message": string
}
```

### 3. Data Seeding Script (`scripts/seed_cutoffs.py`)

**Purpose:** Load cut-off data from CSV/JSON files and store in MongoDB

**Usage:**
```bash
cd apps/ai
python scripts/seed_cutoffs.py
```

**Data Directory:**
- Default: `apps/ai/data/cutoffs/`
- Custom: Set `CUTOFF_DATA_DIR` environment variable

**Supported Formats:**

**CSV Format:**
```csv
year,stream,district,course,university,cutoff_zscore,quota_type
2023,Maths,Colombo,Computer Science,University of Colombo,1.85,merit
2023,Maths,Colombo,Engineering,University of Moratuwa,1.92,merit
```

**JSON Format:**
```json
[
    {
        "year": 2023,
        "stream": "Maths",
        "district": "Colombo",
        "course": "Computer Science",
        "university": "University of Colombo",
        "cutoff_zscore": 1.85,
        "quota_type": "merit"
    }
]
```

### 4. Prediction Endpoint (`app/routes/zscore.py`)

**Endpoint:** `POST /ai/zscore`

**Request:**
```json
{
    "stream": "Maths",
    "district": "Colombo",
    "z_score": 1.8,
    "userId": "optional_user_id"
}
```

**Response:**
```json
{
    "success": true,
    "safe": [
        {
            "course": "Computer Science",
            "university": "University of Colombo",
            "avg_cutoff": 1.75,
            "min_cutoff": 1.70,
            "max_cutoff": 1.80,
            "years_data": 5,
            "trend": "increasing",
            "district": "Colombo"
        }
    ],
    "probable": [...],
    "reach": [...],
    "explanation": "LLM-generated explanation...",
    "message": "Found X safe, Y probable, Z reach courses"
}
```

### 5. LLM Explanation Generator (`app/services/explanation_service.py`)

**Purpose:** Generates human-readable explanations using Gemini

**Features:**
- Explains what Safe/Probable/Reach categories mean
- Analyzes trends (increasing/stable/decreasing cut-offs)
- Provides actionable advice
- District-specific considerations
- Multi-language support (Sinhala, Tamil, English)
- Fallback explanation if Gemini unavailable

## Setup Instructions

### 1. Prepare Cut-off Data

Create data files in `apps/ai/data/cutoffs/`:

```bash
mkdir -p apps/ai/data/cutoffs
# Add your CSV or JSON files
```

### 2. Seed Data

```bash
cd apps/ai
python scripts/seed_cutoffs.py
```

### 3. Test Endpoint

```bash
# Start FastAPI server
uvicorn main:app --reload --port 8000

# Test prediction
curl -X POST http://localhost:8000/ai/zscore \
  -H "Content-Type: application/json" \
  -d '{
    "stream": "Maths",
    "district": "Colombo",
    "z_score": 1.8
  }'
```

## Integration with Chat

The Z-score prediction tool is automatically available to the LLM. When users ask:
- "What courses can I get with Z-score 1.8?"
- "I have Z-score 2.0 in Maths stream, what are my options?"
- "Predict courses for Z-score 1.5, Commerce stream, Colombo district"

The LLM will automatically call the `zscore_predict` tool and provide detailed predictions with explanations.

## Data Requirements

### Minimum Data:
- At least 1 year of cut-off data
- Data for the student's stream
- District-specific data (optional but recommended)

### Recommended Data:
- Last 5 years of cut-off data
- All streams (Bio, Maths, Arts, Commerce, Technology)
- All districts
- Both merit and district quota types

## Features

✅ Historical data analysis (last 5 years)  
✅ Trend detection (increasing/stable/decreasing)  
✅ District-specific predictions  
✅ LLM-powered explanations  
✅ Prediction history storage  
✅ Automatic categorization  
✅ Multi-language support  

## Files Structure

```
apps/ai/
├── app/
│   ├── models/
│   │   └── cutoff.py              # Cut-off data model
│   ├── tools/
│   │   └── zscore_predict_tool.py # Prediction tool
│   ├── routes/
│   │   └── zscore.py              # Prediction endpoint
│   └── services/
│       └── explanation_service.py # LLM explanations
├── scripts/
│   └── seed_cutoffs.py            # Data seeding script
└── data/
    └── cutoffs/                   # Cut-off data files (CSV/JSON)
```

---

**Status:** ✅ **FULLY IMPLEMENTED**  
**Ready for:** Data seeding and testing

