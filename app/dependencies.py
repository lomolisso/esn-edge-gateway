import jwt
from app.api import schemas
from datetime import datetime, timezone
from app.config import SECRET_KEY, EDGE_SENSOR_POP_KEYWORD, EDGE_GATEWAY_WIFI_SSID, EDGE_GATEWAY_WIFI_PASSPHRASE, EDGE_GATEWAY_BLE_IFACE
from fastapi import HTTPException, Header
from app.ble_wifi_provisioner import BLEWiFiProvisioner

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
    

def get_ble_provisioner():
    provisioner = BLEWiFiProvisioner(
        pop=EDGE_SENSOR_POP_KEYWORD,
        wifi_ssid=EDGE_GATEWAY_WIFI_SSID,
        wifi_passphrase=EDGE_GATEWAY_WIFI_PASSPHRASE,
        iface=EDGE_GATEWAY_BLE_IFACE
    )
    yield provisioner