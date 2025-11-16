from fastapi import HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.api_key import APIKey
from app.config import settings
from datetime import datetime

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> APIKey:
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")
    
    # Check admin key
    if api_key == settings.ADMIN_API_KEY:
        # Return pseudo APIKey for admin
        return APIKey(id=0, key=api_key, name="Admin", role="admin", is_active=True)
    
    # Check demo key
    if api_key == settings.DEMO_API_KEY:
        return APIKey(id=-1, key=api_key, name="Demo", role="demo", is_active=True)
    
    # Check database
    db_key = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active == True).first()
    
    if not db_key:
        raise HTTPException(status_code=401, detail="Invalid or inactive API Key")
    
    # Update last used
    db_key.last_used = datetime.utcnow()
    db.commit()
    
    return db_key

async def verify_admin(api_key: APIKey = Depends(verify_api_key)) -> APIKey:
    if api_key.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return api_key
