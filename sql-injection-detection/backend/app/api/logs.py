from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_api_key
from app.services.logging_service import LoggingService
from app.schemas.request import FeedbackRequest
from app.models.api_key import APIKey
from datetime import datetime
from typing import Optional
import io

router = APIRouter()

@router.get("/")
async def get_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    is_malicious: Optional[bool] = None,
    model_used: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0, le=1),
    max_confidence: Optional[float] = Query(None, ge=0, le=1),
    attack_type: Optional[str] = None,
    search_query: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get filtered logs with pagination"""
    service = LoggingService(db)
    
    result = service.get_logs(
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        is_malicious=is_malicious,
        model_used=model_used,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        attack_type=attack_type,
        search_query=search_query
    )
    
    # Convert logs to dict
    logs_data = []
    for log in result['logs']:
        logs_data.append({
            'id': log.id,
            'query': log.query,
            'endpoint': log.endpoint,
            'is_malicious': log.is_malicious,
            'confidence_score': log.confidence_score,
            'model_used': log.model_used,
            'attack_type': log.attack_type,
            'gemini_explanation': log.gemini_explanation,
            'xai_features': log.xai_features,
            'processing_time_ms': log.processing_time_ms,
            'created_at': log.created_at
        })
    
    return {
        'logs': logs_data,
        'total': result['total'],
        'page': result['page'],
        'pages': result['pages']
    }

@router.get("/{log_id}")
async def get_log_detail(
    log_id: int,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get detailed information about a specific log"""
    service = LoggingService(db)
    log = service.get_log_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    return {
        'id': log.id,
        'query': log.query,
        'endpoint': log.endpoint,
        'ip_address': log.ip_address,
        'is_malicious': log.is_malicious,
        'confidence_score': log.confidence_score,
        'model_used': log.model_used,
        'model_version': log.model_version,
        'ensemble_used': log.ensemble_used,
        'ensemble_votes': log.ensemble_votes,
        'xai_method': log.xai_method,
        'xai_features': log.xai_features,
        'xai_scores': log.xai_scores,
        'gemini_explanation': log.gemini_explanation,
        'explanation_style': log.explanation_style,
        'attack_type': log.attack_type,
        'attack_confidence': log.attack_confidence,
        'processing_time_ms': log.processing_time_ms,
        'created_at': log.created_at,
        'user_feedback': log.user_feedback,
        'feedback_comment': log.feedback_comment
    }

@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Submit feedback for a prediction"""
    service = LoggingService(db)
    
    result = service.submit_feedback(
        request_log_id=feedback.request_log_id,
        feedback_type=feedback.feedback_type,
        comment=feedback.comment
    )
    
    return {
        'message': 'Feedback submitted successfully',
        'feedback_id': result.id
    }

@router.get("/export/csv")
async def export_csv(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    is_malicious: Optional[bool] = None,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Export logs to CSV"""
    service = LoggingService(db)
    csv_data = service.export_logs_csv(start_date, end_date, is_malicious)
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs.csv"}
    )

@router.get("/export/json")
async def export_json(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    is_malicious: Optional[bool] = None,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Export logs to JSON"""
    service = LoggingService(db)
    json_data = service.export_logs_json(start_date, end_date, is_malicious)
    
    return StreamingResponse(
        io.StringIO(json_data),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=logs.json"}
    )
