from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class AttackPattern(Base):
    __tablename__ = "attack_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    
    pattern_name = Column(String(255), nullable=False)
    pattern = Column(Text, nullable=False)
    attack_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    
    is_active = Column(Boolean, default=True)
    is_whitelist = Column(Boolean, default=False)
    
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AttackPattern(name={self.pattern_name}, type={self.attack_type})>"