from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib
import secrets

def generate_api_key(prefix: str = "sk") -> str:
    """Generate a secure API key"""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

def hash_query(query: str) -> str:
    """Create hash of query for caching"""
    return hashlib.sha256(query.encode()).hexdigest()

def classify_attack_type(query: str) -> str:
    """Classify type of SQL injection attack"""
    query_lower = query.lower()
    
    if 'union' in query_lower and 'select' in query_lower:
        return 'Union-based SQLi'
    elif any(pattern in query_lower for pattern in ["' or '", '1=1', "' or 1=1"]):
        return 'Boolean-based SQLi'
    elif any(pattern in query_lower for pattern in ['sleep', 'waitfor', 'benchmark']):
        return 'Time-based Blind SQLi'
    elif any(pattern in query_lower for pattern in ['drop table', 'delete from', 'insert into']) and ';' in query:
        return 'Stacked Queries'
    elif query.count("'") % 2 != 0 or query.count('"') % 2 != 0:
        return 'Error-based SQLi'
    elif 'exec' in query_lower or 'xp_' in query_lower:
        return 'Command Injection'
    else:
        return 'Generic SQLi Pattern'

def calculate_attack_confidence(query: str, base_confidence: float) -> float:
    """Calculate confidence that query is specific attack type"""
    query_lower = query.lower()
    
    # Count suspicious patterns
    suspicious_count = 0
    patterns = ['union', 'select', 'drop', 'insert', 'delete', 'exec', '--', '#', '/*']
    
    for pattern in patterns:
        if pattern in query_lower:
            suspicious_count += 1
    
    # Adjust confidence based on patterns
    adjustment = min(suspicious_count * 0.05, 0.3)
    return min(base_confidence + adjustment, 1.0)

def get_date_range(period: str = '7d') -> tuple:
    """Get date range for analytics"""
    end_date = datetime.utcnow()
    
    if period == '24h':
        start_date = end_date - timedelta(hours=24)
    elif period == '7d':
        start_date = end_date - timedelta(days=7)
    elif period == '30d':
        start_date = end_date - timedelta(days=30)
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=7)
    
    return start_date, end_date

def format_processing_time(milliseconds: float) -> str:
    """Format processing time for display"""
    if milliseconds < 1:
        return f"{milliseconds*1000:.2f}μs"
    elif milliseconds < 1000:
        return f"{milliseconds:.2f}ms"
    else:
        return f"{milliseconds/1000:.2f}s"