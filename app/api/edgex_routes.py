from app.api import schemas
from fastapi import APIRouter, Depends, HTTPException
from app.api import utils as api_utils
from app.dependencies import get_redis
from app.config import EDGE_GATEWAY_DEVICE_NAME

edgex_router = APIRouter(prefix="/edgex")
    
@edgex_router.post("/device/export")
async def edge_sensors_measurement(device_data: schemas.EdgeXDeviceData):
    return api_utils.post_json_to_app_backend(
        endpoint=f"/gateway/{EDGE_GATEWAY_DEVICE_NAME}/device/{device_data.deviceName}/export",
        json_data={
            "device_name": device_data.deviceName,
            "measurements": [
                {
                    "resource_name": reading.resourceName,
                    "value": reading.value
                }
                for reading in device_data.readings
            ]
        },
    )

@edgex_router.post("/device/pending-commands")
async def pending_commands(device_data: schemas.EdgeXDeviceData, redis_client=Depends(get_redis)):
    if len(device_data.readings) != 1:
        raise HTTPException(status_code=400, detail="Only one reading is allowed for this endpoint.")
    
    await api_utils.pending_commands(
        redis_client=redis_client,
        device_name=device_data.deviceName,
    )