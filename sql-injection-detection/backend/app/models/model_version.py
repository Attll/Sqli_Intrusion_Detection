from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Training metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Training details
    training_samples = Column(Integer, nullable=True)
    hyperparameters = Column(JSON, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ModelVersion(model_name={self.model_name}, version={self.version})>"