from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.models.request_log import RequestLog
from app.models.feedback import Feedback
from datetime import datetime
from typing import List, Dict, Optional
import csv
import json
import io

class LoggingService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_malicious: Optional[bool] = None,
        model_used: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        attack_type: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> Dict:
        """Get filtered logs with pagination"""
        
        query = self.db.query(RequestLog)
        
        # Apply filters
        if start_date:
            query = query.filter(RequestLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(RequestLog.created_at <= end_date)
        
        if is_malicious is not None:
            query = query.filter(RequestLog.is_malicious == is_malicious)
        
        if model_used:
            query = query.filter(RequestLog.model_used == model_used)
        
        if min_confidence is not None:
            query = query.filter(RequestLog.confidence_score >= min_confidence)
        
        if max_confidence is not None:
            query = query.filter(RequestLog.confidence_score <= max_confidence)
        
        if attack_type:
            query = query.filter(RequestLog.attack_type == attack_type)
        
        if search_query:
            query = query.filter(RequestLog.query.contains(search_query))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(desc(RequestLog.created_at)).offset(skip).limit(limit).all()
        
        return {
            'logs': logs,
            'total': total,
            'page': (skip // limit) + 1,
            'pages': (total + limit - 1) // limit
        }
    
    def get_log_by_id(self, log_id: int) -> Optional[RequestLog]:
        """Get single log entry"""
        return self.db.query(RequestLog).filter(RequestLog.id == log_id).first()
    
    def submit_feedback(
        self,
        request_log_id: int,
        feedback_type: str,
        comment: Optional[str] = None
    ) -> Feedback:
        """Submit user feedback for a prediction"""
        
        # Check if feedback already exists
        existing = self.db.query(Feedback).filter(
            Feedback.request_log_id == request_log_id
        ).first()
        
        if existing:
            existing.feedback_type = feedback_type
            existing.comment = comment
            feedback = existing
        else:
            feedback = Feedback(
                request_log_id=request_log_id,
                feedback_type=feedback_type,
                comment=comment
            )
            self.db.add(feedback)
        
        self.db.commit()
        self.db.refresh(feedback)
        
        return feedback
    
    def export_logs_csv(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_malicious: Optional[bool] = None
    ) -> str:
        """Export logs to CSV format"""
        
        query = self.db.query(RequestLog)
        
        if start_date:
            query = query.filter(RequestLog.created_at >= start_date)
        if end_date:
            query = query.filter(RequestLog.created_at <= end_date)
        if is_malicious is not None:
            query = query.filter(RequestLog.is_malicious == is_malicious)
        
        logs = query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Timestamp', 'Query', 'Is Malicious', 'Confidence',
            'Model Used', 'Attack Type', 'Gemini Explanation'
        ])
        
        # Rows
        for log in logs:
            writer.writerow([
                log.id,
                log.created_at.isoformat(),
                log.query,
                'Yes' if log.is_malicious else 'No',
                log.confidence_score,
                log.model_used,
                log.attack_type or 'N/A',
                log.gemini_explanation or ''
            ])
        
        return output.getvalue()
    
    def export_logs_json(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_malicious: Optional[bool] = None
    ) -> str:
        """Export logs to JSON format"""
        
        query = self.db.query(RequestLog)
        
        if start_date:
            query = query.filter(RequestLog.created_at >= start_date)
        if end_date:
            query = query.filter(RequestLog.created_at <= end_date)
        if is_malicious is not None:
            query = query.filter(RequestLog.is_malicious == is_malicious)
        
        logs = query.all()
        
        # Convert to dict
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'timestamp': log.created_at.isoformat(),
                'query': log.query,
                'is_malicious': log.is_malicious,
                'confidence_score': log.confidence_score,
                'model_used': log.model_used,
                'attack_type': log.attack_type,
                'xai_features': log.xai_features,
                'gemini_explanation': log.gemini_explanation
            })
        
        return json.dumps(logs_data, indent=2)
    
    def delete_old_logs(self, days: int = 90) -> int:
        """Delete logs older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = self.db.query(RequestLog).filter(
            RequestLog.created_at < cutoff_date
        ).delete()
        
        self.db.commit()
        
        return deleted
