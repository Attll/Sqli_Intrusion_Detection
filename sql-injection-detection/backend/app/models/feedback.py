from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    request_log_id = Column(Integer, ForeignKey("request_logs.id"), nullable=False)
    
    feedback_type = Column(String(50), nullable=False)  # false_positive, false_negative, correct
    comment = Column(Text, nullable=True)
    
    # For retraining
    used_for_training = Column(Boolean, default=False)
    trained_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, type={self.feedback_type})>"