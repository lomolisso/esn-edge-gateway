from app.api import schemas
from fastapi import APIRouter, HTTPException
from app.api import utils as api_utils

edgex_router = APIRouter(prefix="/edgex")
    
@edgex_router.post("/mqtt-connection-status")
async def mqtt_device_connected(device_data: schemas.EdgeXDeviceData):
    if len(device_data.readings) != 1:
        raise HTTPException(status_code=400, detail="Only one reading is allowed for this endpoint.")
    
    _bool_conn_status = device_data.readings[0].value == "true"
    mqtt_connection_status = "UP" if _bool_conn_status else "DOWN"

    # Update edgex device operating state
    api_utils.set_edgex_device_operating_state(
        device_name=device_data.deviceName,
        status=mqtt_connection_status
    )

    # Send mqtt connection status to app backend
    return api_utils.post_json_to_app_backend(
        endpoint="/mqtt-connection-status",
        json_data={
            "device_name": device_data.deviceName,
            "mqtt_connection_status": mqtt_connection_status
        },
    )

@edgex_router.post("/edge-sensor-measurement")
async def edge_sensors_measurement(device_data: schemas.EdgeXDeviceData):
    return api_utils.post_json_to_app_backend(
        endpoint="/edge-sensor-measurement",
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