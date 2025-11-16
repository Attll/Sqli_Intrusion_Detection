from pydantic import BaseModel as _PydanticBaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseSchema(_PydanticBaseModel):
    try:
        model_config = {"protected_namespaces": (), "from_attributes": True}
    except Exception:
        class Config:
            from_attributes = True


class AttackStats(BaseSchema):
    total_requests: int
    malicious_requests: int
    benign_requests: int
    attack_rate: float
    avg_confidence: float


class TimeSeriesData(BaseSchema):
    timestamps: List[str]
    values: List[float]
    

class AttackTypeDistribution(BaseSchema):
    attack_type: str
    count: int
    percentage: float


class ModelPerformanceMetrics(BaseSchema):
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    total_predictions: int


class HeatmapData(BaseSchema):
    hours: List[int]
    days: List[str]
    values: List[List[int]]


class TopEndpoint(BaseSchema):
    endpoint: str
    attack_count: int
    last_attack: datetime


class AnalyticsResponse(BaseSchema):
    attack_stats: AttackStats
    timeline_data: TimeSeriesData
    attack_distribution: List[AttackTypeDistribution]
    model_performance: List[ModelPerformanceMetrics]
    heatmap_data: HeatmapData
    top_endpoints: List[TopEndpoint]
    

class LogFilters(BaseSchema):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_malicious: Optional[bool] = None
    model_used: Optional[str] = None
    min_confidence: Optional[float] = None
    attack_type: Optional[str] = None
