from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_api_key
from app.services.analytics_service import AnalyticsService
from app.models.api_key import APIKey

router = APIRouter()

@router.get("/stats")
async def get_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get overall attack statistics"""
    service = AnalyticsService(db)
    return service.get_attack_stats(days=days)

@router.get("/timeline")
async def get_timeline(
    days: int = Query(7, ge=1, le=90),
    interval: str = Query('hour', regex='^(hour|day)$'),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get attack timeline data"""
    service = AnalyticsService(db)
    return service.get_timeline_data(days=days, interval=interval)

@router.get("/attack-distribution")
async def get_attack_distribution(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get distribution of attack types"""
    service = AnalyticsService(db)
    return service.get_attack_distribution(days=days)

@router.get("/model-performance")
async def get_model_performance(
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get model performance metrics"""
    service = AnalyticsService(db)
    return service.get_model_performance()

@router.get("/heatmap")
async def get_heatmap(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get attack heatmap data"""
    service = AnalyticsService(db)
    return service.get_heatmap_data(days=days)

@router.get("/top-endpoints")
async def get_top_endpoints(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get most attacked endpoints"""
    service = AnalyticsService(db)
    return service.get_top_endpoints(days=days, limit=limit)

@router.get("/confidence-distribution")
async def get_confidence_distribution(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get confidence score distribution"""
    service = AnalyticsService(db)
    return service.get_confidence_distribution(days=days)

@router.get("/dashboard")
async def get_dashboard_data(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """Get all dashboard data in one call"""
    service = AnalyticsService(db)
    
    return {
        'attack_stats': service.get_attack_stats(days=days),
        'timeline_data': service.get_timeline_data(days=days),
        'attack_distribution': service.get_attack_distribution(days=days),
        'model_performance': service.get_model_performance(),
        'heatmap_data': service.get_heatmap_data(days=days),
        'top_endpoints': service.get_top_endpoints(days=days)
    }
