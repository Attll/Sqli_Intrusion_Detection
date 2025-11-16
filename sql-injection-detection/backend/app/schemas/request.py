from pydantic import BaseModel as _PydanticBaseModel, Field
from typing import Optional, List
from datetime import datetime


class BaseSchema(_PydanticBaseModel):
    try:
        model_config = {"protected_namespaces": (), "from_attributes": True}
    except Exception:
        class Config:
            from_attributes = True


class DetectionRequest(BaseSchema):
    query: str = Field(..., description="SQL query to analyze")
    endpoint: Optional[str] = Field(None, description="API endpoint being accessed")
    use_ensemble: bool = Field(False, description="Use ensemble of models")
    xai_method: str = Field("lime", description="XAI method to use (lime, shap, feature_importance)")
    explanation_style: str = Field("simple", description="Gemini explanation style (simple, technical, detailed)")
    
class VulnerableDemoRequest(BaseSchema):
    query: str
    
class FeedbackRequest(BaseSchema):
    request_log_id: int
    feedback_type: str = Field(..., description="correct, false_positive, false_negative")
    comment: Optional[str] = None

class ModelSwitchRequest(BaseSchema):
    model_name: str = Field(..., description="Model to switch to")
    
class ThresholdUpdateRequest(BaseSchema):
    threshold: float = Field(..., ge=0.0, le=1.0, description="Confidence threshold")

class StressTestRequest(BaseSchema):
    num_requests: int = Field(100, ge=1, le=10000)
    attack_types: Optional[List[str]] = None
    include_benign: bool = True
