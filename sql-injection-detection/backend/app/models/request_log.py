from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Request details
    query = Column(Text, nullable=False)
    endpoint = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Detection results
    is_malicious = Column(Boolean, nullable=False)
    confidence_score = Column(Float, nullable=False)
    model_used = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    
    # Ensemble info
    ensemble_used = Column(Boolean, default=False)
    ensemble_votes = Column(JSON, nullable=True)
    
    # XAI outputs
    xai_method = Column(String(50), nullable=True)
    xai_features = Column(JSON, nullable=True)
    xai_scores = Column(JSON, nullable=True)
    
    # Gemini explanation
    gemini_explanation = Column(Text, nullable=True)
    explanation_style = Column(String(50), default="simple")
    
    # Attack classification
    attack_type = Column(String(100), nullable=True)
    attack_confidence = Column(Float, nullable=True)
    
    # Metadata
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Feedback
    user_feedback = Column(String(50), nullable=True)
    feedback_comment = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<RequestLog(id={self.id}, is_malicious={self.is_malicious}, confidence={self.confidence_score})>"