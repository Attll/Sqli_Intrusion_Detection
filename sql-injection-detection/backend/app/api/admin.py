from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import verify_admin
from app.models.api_key import APIKey as APIKeyModel
from app.models.system_config import SystemConfig
from app.models.attack_pattern import AttackPattern
from app.services.logging_service import LoggingService
from app.ml.active_learning import ActiveLearningPipeline
from app.utils.helpers import generate_api_key
from app.config import settings
from typing import List
import os

router = APIRouter()

@router.get("/system-info")
async def get_system_info(
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Get system information"""
    
    from app.models.request_log import RequestLog
    from app.models.model_version import ModelVersion
    
    total_requests = db.query(RequestLog).count()
    total_models = db.query(ModelVersion).count()
    active_models = db.query(ModelVersion).filter(ModelVersion.is_active == True).count()
    
    return {
        'total_requests_logged': total_requests,
        'total_models': total_models,
        'active_models': active_models,
        'current_model': settings.DEFAULT_MODEL,
        'confidence_threshold': settings.CONFIDENCE_THRESHOLD,
        'database_url': settings.DB_HOST,
        'gemini_model': settings.GEMINI_MODEL
    }

@router.get("/api-keys")
async def list_api_keys(
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """List all API keys"""
    
    keys = db.query(APIKeyModel).all()
    
    return {
        'api_keys': [
            {
                'id': key.id,
                'name': key.name,
                'role': key.role,
                'is_active': key.is_active,
                'created_at': key.created_at,
                'last_used': key.last_used,
                'key_preview': key.key[:10] + '...' if len(key.key) > 10 else key.key
            }
            for key in keys
        ]
    }

@router.post("/api-keys")
async def create_api_key(
    name: str,
    role: str,
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Create new API key"""
    
    if role not in ['admin', 'user', 'demo']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    new_key = generate_api_key(prefix=role[:2])
    
    api_key_obj = APIKeyModel(
        key=new_key,
        name=name,
        role=role,
        is_active=True
    )
    
    db.add(api_key_obj)
    db.commit()
    
    return {
        'message': 'API key created',
        'key': new_key,
        'name': name,
        'role': role
    }

@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Delete API key"""
    
    key = db.query(APIKeyModel).filter(APIKeyModel.id == key_id).first()
    
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(key)
    db.commit()
    
    return {'message': 'API key deleted'}

@router.post("/retrain")
async def trigger_retraining(
    model_name: str,
    days: int = 7,
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Trigger active learning retraining"""
    
    try:
        pipeline = ActiveLearningPipeline(db)
        
        data_path = os.path.join(settings.DATA_PATH, 'raw', 'sql_injection_dataset.csv')
        
        result = pipeline.retrain_model(
            model_name=model_name,
            original_data_path=data_path,
            days=days
        )
        
        if result['status'] == 'success':
            # Save to database
            from app.models.model_version import ModelVersion
            
            model_version = ModelVersion(
                model_name=result['model_name'],
                version=result['version'],
                file_path=result['model_path'],
                accuracy=result['metrics']['accuracy'],
                precision=result['metrics']['precision'],
                recall=result['metrics']['recall'],
                f1_score=result['metrics']['f1_score'],
                training_samples=result['total_samples'],
                is_active=False,
                notes=f"Retrained with {result['new_samples_added']} new samples"
            )
            
            db.add(model_version)
            db.commit()
            
            result['model_id'] = model_version.id
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_config(
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Get system configuration"""
    
    configs = db.query(SystemConfig).all()
    
    config_dict = {}
    for config in configs:
        config_dict[config.key] = config.value or config.value_json
    
    return {
        'configurations': config_dict,
        'default_model': settings.DEFAULT_MODEL,
        'confidence_threshold': settings.CONFIDENCE_THRESHOLD
    }

@router.post("/config")
async def update_config(
    key: str,
    value: str,
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Update system configuration"""
    
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    if config:
        config.value = value
    else:
        config = SystemConfig(key=key, value=value)
        db.add(config)
    
    db.commit()
    
    return {'message': f'Configuration {key} updated'}

@router.get("/attack-patterns")
async def get_attack_patterns(
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Get known attack patterns"""
    
    patterns = db.query(AttackPattern).filter(AttackPattern.is_active == True).all()
    
    return {
        'patterns': [
            {
                'id': p.id,
                'pattern_name': p.pattern_name,
                'pattern': p.pattern,
                'attack_type': p.attack_type,
                'severity': p.severity,
                'is_whitelist': p.is_whitelist
            }
            for p in patterns
        ]
    }

@router.post("/attack-patterns")
async def add_attack_pattern(
    pattern_name: str,
    pattern: str,
    attack_type: str,
    severity: str,
    is_whitelist: bool = False,
    db: Session = Depends(get_db),
    api_key: APIKeyModel = Depends(verify_admin)
):
    """Add a new attack pattern"""
    
    new_pattern = AttackPattern(
        pattern_name=pattern_name,
        pattern=pattern,
        attack_type=attack_type,
        severity=severity,
        is_whitelist=is_whitelist
    )
    
    db.add(new_pattern)
    db.commit()
    
    return {'message': 'Attack pattern added', 'pattern_id': new_pattern.id}
