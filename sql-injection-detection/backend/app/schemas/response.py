from pydantic import BaseModel as _PydanticBaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime


class BaseSchema(_PydanticBaseModel):
    try:
        model_config = {"protected_namespaces": (), "from_attributes": True}
    except Exception:
        class Config:
            from_attributes = True


class XAIOutput(BaseSchema):
    method: str
    features: Dict[str, float]
    top_features: List[Dict[str, Any]]
    visualization_data: Optional[Dict] = None


class DetectionResponse(BaseSchema):
    is_malicious: bool
    confidence_score: float
    model_used: str
    model_version: Optional[str] = None
    
    # Ensemble info
    ensemble_used: bool = False
    ensemble_votes: Optional[Dict[str, Any]] = None
    
    # Attack classification
    attack_type: Optional[str] = None
    attack_confidence: Optional[float] = None
    
    # XAI
    xai_output: Optional[XAIOutput] = None
    
    # Gemini explanation
    gemini_explanation: Optional[str] = None
    
    # Metadata
    processing_time_ms: float
    request_id: int
    timestamp: datetime


class VulnerableResponse(BaseSchema):
    query_executed: str
    result: Any
    data_leaked: Optional[List[Dict]] = None
    attack_successful: bool
    impact_description: str
