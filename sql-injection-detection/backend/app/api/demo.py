from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_api_key
from app.schemas.request import VulnerableDemoRequest, DetectionRequest
from app.schemas.response import VulnerableResponse, DetectionResponse
from app.services.detection_service import DetectionService
from app.models.api_key import APIKey
import sqlite3
import os

router = APIRouter()

# Create demo database
DEMO_DB_PATH = "demo_vulnerable.db"

def init_demo_db():
    """Initialize vulnerable demo database"""
    conn = sqlite3.connect(DEMO_DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT
        )
    """)
    
    # Insert demo data
    cursor.execute("DELETE FROM users")
    demo_users = [
        (1, 'admin', 'admin123', 'admin@example.com', 'admin'),
        (2, 'john_doe', 'password123', 'john@example.com', 'user'),
        (3, 'jane_smith', 'secret456', 'jane@example.com', 'user'),
        (4, 'bob_wilson', 'pass789', 'bob@example.com', 'user'),
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", demo_users)
    
    conn.commit()
    conn.close()

# Initialize on startup
init_demo_db()

@router.post("/protected", response_model=DetectionResponse)
async def protected_demo(
    request: DetectionRequest,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """
    Protected demo - queries are analyzed and blocked if malicious
    """
    try:
        service = DetectionService(db)
        result = service.detect(
            query=request.query,
            endpoint="/demo/protected",
            use_ensemble=request.use_ensemble,
            xai_method=request.xai_method,
            explanation_style=request.explanation_style
        )
        
        # Add execution result
        if not result['is_malicious']:
            # Safe to execute
            result['execution_status'] = 'Query would be executed safely'
            result['data_returned'] = 'Sample data (protected)'
        else:
            # Blocked
            result['execution_status'] = 'Query blocked by protection system'
            result['data_returned'] = None
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vulnerable", response_model=VulnerableResponse)
async def vulnerable_demo(
    request: VulnerableDemoRequest,
    api_key: APIKey = Depends(verify_api_key)
):
    """
    Vulnerable demo - queries are executed without protection (demo database only)
    """
    try:
        conn = sqlite3.connect(DEMO_DB_PATH)
        cursor = conn.cursor()
        
        attack_successful = False
        data_leaked = []
        impact_description = ""
        
        try:
            # Execute query (DANGEROUS - only for demo!)
            cursor.execute(request.query)
            results = cursor.fetchall()
            
            # Check if data was leaked
            if results:
                data_leaked = [
                    {
                        'id': row[0],
                        'username': row[1] if len(row) > 1 else None,
                        'password': row[2] if len(row) > 2 else '***',
                        'email': row[3] if len(row) > 3 else None,
                    }
                    for row in results[:10]  # Limit to 10 rows
                ]
                attack_successful = True
                impact_description = f"⚠️ ATTACK SUCCESSFUL: {len(results)} rows of sensitive data exposed including usernames and passwords!"
            else:
                impact_description = "Query executed but returned no data."
            
        except sqlite3.Error as e:
            # SQL error (might still reveal info)
            impact_description = f"SQL Error: {str(e)} - This error message could reveal database structure to attackers!"
            attack_successful = False
        
        conn.close()
        
        return {
            'query_executed': request.query,
            'result': 'Success' if not attack_successful else 'Attack Successful',
            'data_leaked': data_leaked if attack_successful else None,
            'attack_successful': attack_successful,
            'impact_description': impact_description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_protected_vs_vulnerable(
    request: DetectionRequest,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """
    Side-by-side comparison of protected vs vulnerable execution
    """
    try:
        # Get protected result
        service = DetectionService(db)
        protected_result = service.detect(
            query=request.query,
            endpoint="/demo/compare",
            use_ensemble=request.use_ensemble,
            xai_method=request.xai_method,
            explanation_style=request.explanation_style
        )
        
        # Get vulnerable result
        conn = sqlite3.connect(DEMO_DB_PATH)
        cursor = conn.cursor()
        
        vulnerable_data = []
        vulnerable_success = False
        
        try:
            cursor.execute(request.query)
            results = cursor.fetchall()
            if results:
                vulnerable_data = [dict(zip(['id', 'username', 'password', 'email', 'role'], row)) for row in results[:5]]
                vulnerable_success = True
        except:
            pass
        
        conn.close()
        
        return {
            'protected': {
                'blocked': protected_result['is_malicious'],
                'confidence': protected_result['confidence_score'],
                'explanation': protected_result['gemini_explanation'],
                'data_protected': protected_result['is_malicious']
            },
            'vulnerable': {
                'executed': True,
                'attack_successful': vulnerable_success,
                'data_leaked': vulnerable_data,
                'impact': 'HIGH RISK' if vulnerable_success else 'Query executed'
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
