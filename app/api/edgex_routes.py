from app.api import schemas
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api import utils as api_utils
from app.dependencies import get_redis
from app.config import EDGE_GATEWAY_DEVICE_NAME

import asyncio

edgex_router = APIRouter(prefix="/edgex")
    
def _preprocess_prediction_request(device_data: schemas.EdgeXDeviceData):
    device_name = device_data.deviceName
    device_data = {reading.resourceName.replace("-", "_"): reading.value for reading in device_data.readings}
    return device_name, device_data          


@edgex_router.post("/device/export")
async def edge_sensors_export(device_data: schemas.EdgeXDeviceData, background_tasks: BackgroundTasks):
    device_name, device_data = _preprocess_prediction_request(device_data)
    background_tasks.add_task(api_utils.post_json_to_app_backend,
        endpoint=f"/gateway/{EDGE_GATEWAY_DEVICE_NAME}/device/{device_name}/export",
        json_data=device_data
    )


@edgex_router.post("/gateway/predict")
async def gateway_pred_request(device_data: schemas.EdgeXDeviceData, background_tasks: BackgroundTasks):    
    device_name, device_data = _preprocess_prediction_request(device_data)
    background_tasks.add_task(api_utils.post_json_to_predictive_node,
        endpoint="/predict",
        json_data={
            "device_name": device_name,
            "gateway_name": EDGE_GATEWAY_DEVICE_NAME,
            **device_data
        },
    )
    

@edgex_router.post("/cloud/predict")
async def cloud_pred_request(device_data: schemas.EdgeXDeviceData, background_tasks: BackgroundTasks):
    device_name, device_data = _preprocess_prediction_request(device_data)
    background_tasks.add_task(api_utils.post_json_to_app_backend,
        endpoint=f"/gateway/{EDGE_GATEWAY_DEVICE_NAME}/device/{device_name}/predict",
        json_data=device_data
    )
    

@edgex_router.post("/device/debug/prediction-log")
async def edge_sensors_prediction_log(device_data: schemas.EdgeXDeviceData):
    return api_utils.post_json_to_app_backend(
        endpoint=f"/gateway/{EDGE_GATEWAY_DEVICE_NAME}/device/{device_data.deviceName}/debug/prediction-log",
        json_data={
            "device_name": device_data.deviceName,
            **{reading.resourceName.replace("-", "_"): reading.value for reading in device_data.readings}
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