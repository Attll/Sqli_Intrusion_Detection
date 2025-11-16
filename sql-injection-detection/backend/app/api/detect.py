from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_api_key
from app.schemas.request import DetectionRequest
from app.schemas.response import DetectionResponse
from app.services.detection_service import DetectionService
from app.models.api_key import APIKey

router = APIRouter()

@router.post("/detect", response_model=DetectionResponse)
async def detect_sql_injection(
    request: DetectionRequest,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """
    Detect SQL injection in a query with XAI and Gemini explanation
    """
    try:
        service = DetectionService(db)
        result = service.detect(
            query=request.query,
            endpoint=request.endpoint,
            use_ensemble=request.use_ensemble,
            xai_method=request.xai_method,
            explanation_style=request.explanation_style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-detect")
async def batch_detect(
    queries: list[str],
    use_ensemble: bool = False,
    db: Session = Depends(get_db),
    api_key: APIKey = Depends(verify_api_key)
):
    """
    Batch detection for multiple queries
    """
    try:
        service = DetectionService(db)
        if not use_ensemble:
            service.load_model()
        else:
            service.load_ensemble()
        
        results = []
        for query in queries:
            result = service.detect(
                query=query,
                use_ensemble=use_ensemble,
                xai_method='feature_importance',  # Faster for batch
                explanation_style='simple'
            )
            results.append(result)
        
        return {
            'total': len(queries),
            'results': results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
