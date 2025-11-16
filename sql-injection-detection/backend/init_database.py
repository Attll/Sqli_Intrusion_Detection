"""
Database initialization script
Run this to create tables and seed initial data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.request_log import RequestLog
from app.models.api_key import APIKey
from app.models.model_version import ModelVersion
from app.models.feedback import Feedback
from app.models.attack_pattern import AttackPattern
from app.models.system_config import SystemConfig
from datetime import datetime

def generate_simple_api_key(prefix: str = "sk") -> str:
    """Generate a simple API key for initial setup"""
    import secrets
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

def seed_initial_data():
    """Seed initial data"""
    print("\nSeeding initial data...")
    db = SessionLocal()
    
    try:
        # Create API keys
        print("Creating API keys...")
        
        # Check if keys already exist
        existing_keys = db.query(APIKey).count()
        if existing_keys == 0:
            demo_key = APIKey(
                key="demo-key-change-this",
                name="Demo Key",
                role="demo",
                is_active=True
            )
            
            admin_key = APIKey(
                key="admin-key-change-this",
                name="Admin Key",
                role="admin",
                is_active=True
            )
            
            user_key_value = generate_simple_api_key("us")
            user_key = APIKey(
                key=user_key_value,
                name="User Key",
                role="user",
                is_active=True
            )
            
            db.add(demo_key)
            db.add(admin_key)
            db.add(user_key)
            db.commit()
            print(f"✓ Created 3 API keys")
        else:
            print(f"✓ API keys already exist ({existing_keys} keys)")
            user_key_value = "Already created"
        
        # Create attack patterns
        print("Creating attack patterns...")
        existing_patterns = db.query(AttackPattern).count()
        if existing_patterns == 0:
            patterns = [
                AttackPattern(
                    pattern_name="UNION SELECT",
                    pattern="UNION.*SELECT",
                    attack_type="Union-based SQLi",
                    severity="high",
                    is_active=True
                ),
                AttackPattern(
                    pattern_name="OR 1=1",
                    pattern="(OR|AND).*1.*=.*1",
                    attack_type="Boolean-based SQLi",
                    severity="high",
                    is_active=True
                ),
                AttackPattern(
                    pattern_name="DROP TABLE",
                    pattern="DROP.*TABLE",
                    attack_type="Stacked Queries",
                    severity="critical",
                    is_active=True
                ),
                AttackPattern(
                    pattern_name="EXEC/EXECUTE",
                    pattern="(EXEC|EXECUTE).*xp_",
                    attack_type="Command Injection",
                    severity="critical",
                    is_active=True
                ),
                AttackPattern(
                    pattern_name="SLEEP/WAITFOR",
                    pattern="(SLEEP|WAITFOR|BENCHMARK)",
                    attack_type="Time-based Blind SQLi",
                    severity="medium",
                    is_active=True
                ),
            ]
            
            for pattern in patterns:
                db.add(pattern)
            
            db.commit()
            print(f"✓ Created {len(patterns)} attack patterns")
        else:
            print(f"✓ Attack patterns already exist ({existing_patterns} patterns)")
        
        # Create system config
        print("Creating system configuration...")
        existing_config = db.query(SystemConfig).count()
        if existing_config == 0:
            configs = [
                SystemConfig(
                    key="confidence_threshold",
                    value="0.7",
                    description="Minimum confidence threshold for detection"
                ),
                SystemConfig(
                    key="log_retention_days",
                    value="90",
                    description="Number of days to retain logs"
                ),
                SystemConfig(
                    key="enable_active_learning",
                    value="true",
                    description="Enable active learning pipeline"
                ),
            ]
            
            for config in configs:
                db.add(config)
            
            db.commit()
            print(f"✓ Created {len(configs)} configuration entries")
        else:
            print(f"✓ Configuration already exists ({existing_config} entries)")
        
        print("\n✓ Database initialized successfully!")
        print("\n" + "="*60)
        print("API KEYS:")
        print("="*60)
        print(f"Demo Key:  demo-key-change-this")
        print(f"Admin Key: admin-key-change-this")
        print(f"User Key:  {user_key_value}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("SQL Injection Detection System - Database Initialization")
    print("="*60)
    
    # Initialize database
    if not init_database():
        sys.exit(1)
    
    # Seed initial data
    if not seed_initial_data():
        sys.exit(1)
    
    print("\n✓ All done! You can now train models and start the API server.")