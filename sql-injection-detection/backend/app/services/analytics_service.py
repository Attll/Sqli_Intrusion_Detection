from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract, cast, Integer
from app.database import engine
from app.models.request_log import RequestLog
from app.models.model_version import ModelVersion
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_attack_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get overall attack statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total = self.db.query(RequestLog).filter(
            RequestLog.created_at >= cutoff_date
        ).count()
        
        malicious = self.db.query(RequestLog).filter(
            RequestLog.created_at >= cutoff_date,
            RequestLog.is_malicious == True
        ).count()
        
        benign = total - malicious
        attack_rate = (malicious / total * 100) if total > 0 else 0
        
        # Average confidence
        avg_confidence = self.db.query(func.avg(RequestLog.confidence_score)).filter(
            RequestLog.created_at >= cutoff_date
        ).scalar() or 0
        
        return {
            'total_requests': total,
            'malicious_requests': malicious,
            'benign_requests': benign,
            'attack_rate': round(attack_rate, 2),
            'avg_confidence': round(float(avg_confidence), 4)
        }
    
    def get_timeline_data(self, days: int = 7, interval: str = 'hour') -> Dict[str, List]:
        """Get attack timeline data"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query logs grouped by time
        if interval == 'hour':
            # Hourly buckets
            delta = timedelta(hours=1)
            # SQLite uses strftime, MySQL uses DATE_FORMAT, Postgres uses date_trunc
            if engine.dialect.name == 'sqlite':
                time_format = '%Y-%m-%d %H:00'
                time_bucket = func.strftime(time_format, RequestLog.created_at)
            elif engine.dialect.name in ('mysql', 'mariadb'):
                time_format = '%Y-%m-%d %H:00'
                time_bucket = func.date_format(RequestLog.created_at, time_format)
            elif engine.dialect.name == 'postgresql':
                # date_trunc returns a timestamp; cast to text for grouping
                time_bucket = func.date_trunc('hour', RequestLog.created_at)
            else:
                # Fallback: try SQLite-style strftime
                time_format = '%Y-%m-%d %H:00'
                time_bucket = func.strftime(time_format, RequestLog.created_at)
        else:  # day
            delta = timedelta(days=1)
            if engine.dialect.name == 'sqlite':
                time_format = '%Y-%m-%d'
                time_bucket = func.strftime(time_format, RequestLog.created_at)
            elif engine.dialect.name in ('mysql', 'mariadb'):
                time_format = '%Y-%m-%d'
                time_bucket = func.date_format(RequestLog.created_at, time_format)
            elif engine.dialect.name == 'postgresql':
                time_bucket = func.date_trunc('day', RequestLog.created_at)
            else:
                time_format = '%Y-%m-%d'
                time_bucket = func.strftime(time_format, RequestLog.created_at)

        logs = self.db.query(
            time_bucket.label('time_bucket'),
            func.count(RequestLog.id).label('count'),
            func.sum(cast(RequestLog.is_malicious, Integer)).label('malicious_count')
        ).filter(
            RequestLog.created_at >= cutoff_date
        ).group_by('time_bucket').order_by('time_bucket').all()
        
        timestamps = []
        total_values = []
        malicious_values = []
        
        for log in logs:
            timestamps.append(log.time_bucket)
            total_values.append(log.count)
            malicious_values.append(log.malicious_count or 0)
        
        return {
            'timestamps': timestamps,
            'total': total_values,
            'malicious': malicious_values,
            'benign': [t - m for t, m in zip(total_values, malicious_values)]
        }
    
    def get_attack_distribution(self, days: int = 7) -> List[Dict]:
        """Get distribution of attack types"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            RequestLog.attack_type,
            func.count(RequestLog.id).label('count')
        ).filter(
            RequestLog.created_at >= cutoff_date,
            RequestLog.is_malicious == True,
            RequestLog.attack_type.isnot(None)
        ).group_by(RequestLog.attack_type).all()
        
        total = sum(r.count for r in results)
        
        distribution = []
        for result in results:
            distribution.append({
                'attack_type': result.attack_type,
                'count': result.count,
                'percentage': round(result.count / total * 100, 2) if total > 0 else 0
            })
        
        # Sort by count
        distribution.sort(key=lambda x: x['count'], reverse=True)
        
        return distribution
    
    def get_model_performance(self) -> List[Dict]:
        """Get performance metrics for all models"""
        models = self.db.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).all()
        
        performance = []
        for model in models:
            # Count predictions made by this model
            total_predictions = self.db.query(RequestLog).filter(
                RequestLog.model_used == model.model_name
            ).count()
            
            performance.append({
                'model_name': model.model_name,
                'accuracy': round(model.accuracy or 0, 4),
                'precision': round(model.precision or 0, 4),
                'recall': round(model.recall or 0, 4),
                'f1_score': round(model.f1_score or 0, 4),
                'total_predictions': total_predictions
            })
        
        return performance
    
    def get_heatmap_data(self, days: int = 7) -> Dict:
        """Get attack heatmap data (hour x day of week)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        logs = self.db.query(RequestLog).filter(
            RequestLog.created_at >= cutoff_date,
            RequestLog.is_malicious == True
        ).all()
        
        # Create 24x7 matrix
        heatmap = [[0 for _ in range(24)] for _ in range(7)]
        
        for log in logs:
            day_of_week = log.created_at.weekday()
            hour = log.created_at.hour
            heatmap[day_of_week][hour] += 1
        
        return {
            'hours': list(range(24)),
            'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'values': heatmap
        }
    
    def get_top_endpoints(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get most attacked endpoints"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            RequestLog.endpoint,
            func.count(RequestLog.id).label('attack_count'),
            func.max(RequestLog.created_at).label('last_attack')
        ).filter(
            RequestLog.created_at >= cutoff_date,
            RequestLog.is_malicious == True,
            RequestLog.endpoint.isnot(None)
        ).group_by(RequestLog.endpoint).order_by(
            func.count(RequestLog.id).desc()
        ).limit(limit).all()
        
        endpoints = []
        for result in results:
            endpoints.append({
                'endpoint': result.endpoint,
                'attack_count': result.attack_count,
                'last_attack': result.last_attack
            })
        
        return endpoints
    
    def get_confidence_distribution(self, days: int = 7) -> Dict:
        """Get distribution of confidence scores"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        logs = self.db.query(RequestLog.confidence_score).filter(
            RequestLog.created_at >= cutoff_date
        ).all()
        
        # Create bins
        bins = [0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
        bin_labels = ['<50%', '50-70%', '70-80%', '80-90%', '90-95%', '95-100%']
        bin_counts = [0] * len(bin_labels)
        
        for log in logs:
            score = log.confidence_score
            for i in range(len(bins) - 1):
                if bins[i] <= score < bins[i + 1]:
                    bin_counts[i] += 1
                    break
        
        return {
            'labels': bin_labels,
            'counts': bin_counts
        }
