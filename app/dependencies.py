import jwt
from app.api import schemas
from datetime import datetime, timezone
from app.config import SECRET_KEY
from fastapi import HTTPException, Header

def verify_token(authorization: str = Header(None)):
    try:
        token = authorization.split("Bearer ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        exp_datetime = datetime.fromtimestamp(payload["exp"], timezone.utc)
        if exp_datetime < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid token or no token provided.")
    