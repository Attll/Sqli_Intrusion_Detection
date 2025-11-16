from pydantic import BaseModel as _PydanticBaseModel
from typing import Optional, Dict, List
from datetime import datetime


class BaseSchema(_PydanticBaseModel):
    try:
        model_config = {"protected_namespaces": (), "from_attributes": True}
    except Exception:
        class Config:
            from_attributes = True


class ModelMetrics(BaseSchema):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    
class ModelInfo(BaseSchema):
    id: int
    model_name: str
    version: str
    is_active: bool
    metrics: Optional[ModelMetrics] = None
    hyperparameters: Optional[Dict] = None
    feature_importance: Optional[Dict] = None
    created_at: datetime
    

class ModelComparisonResult(BaseSchema):
    model_a: str
    model_b: str
    test_samples: int
    agreement_rate: float
    model_a_metrics: ModelMetrics
    model_b_metrics: ModelMetrics
    disagreement_cases: List[Dict]
