import jwt
from datetime import datetime, timedelta
from app.api import schemas
from app.dependencies import verify_token, get_ble_provisioner
from fastapi import APIRouter,  HTTPException, Depends
from app.api import utils as api_utils
from app.config import (
    SECRET_KEY,
    EDGE_GATEWAY_DEVICE_NAME,
    EDGE_GATEWAY_WLAN_IFACE,
    EDGE_GATEWAY_POP_KEYWORD,
    EDGE_SENSOR_SERVICE_NAME_PREFIX,
    EDGE_SENSOR_OUI,
)
from typing import List

cloud_router = APIRouter(prefix="/cloud")

@cloud_router.post("/auth")
async def authenticate_gateway(auth_data: schemas.AuthData):
    if auth_data.pop == EDGE_GATEWAY_POP_KEYWORD:
        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(hours=1)},
            SECRET_KEY,
            algorithm="HS256",
        )
        return {"jwt_token": token}
    raise HTTPException(status_code=400, detail="Authentication failed.")


@cloud_router.get("/get-gateway-info", dependencies=[Depends(verify_token)])
async def get_gateway_data() -> schemas.EdgeGateway:
    return schemas.EdgeGateway(
        **{
            "device_name": EDGE_GATEWAY_DEVICE_NAME,
            "device_address": api_utils.get_wlan_iface_address(EDGE_GATEWAY_WLAN_IFACE),
        }
    )


@cloud_router.post("/upload-edgex-device-profile", dependencies=[Depends(verify_token)])
async def upload_edgex_device_profile():
    return api_utils.upload_edgex_device_profile()


@cloud_router.get("/discover-devices", dependencies=[Depends(verify_token)])
async def discover_devices(
    provisioner=Depends(get_ble_provisioner),
) -> List[schemas.BLEDevice]:
    return [
        schemas.BLEDevice(**d)
        for d in await provisioner.discover(
            service_name_prefix=EDGE_SENSOR_SERVICE_NAME_PREFIX,
            fallback_oui=EDGE_SENSOR_OUI,
        )
    ]


@cloud_router.post("/provision-wifi-credentials", dependencies=[Depends(verify_token)])
async def provision_device(
    devices: list[schemas.BLEDevice], provisioner=Depends(get_ble_provisioner)
):
    _devices = [device.model_dump() for device in devices]
    for device in _devices:
        _provisioned = False
        await provisioner.connect(**device)
        while not _provisioned:
            try:
                await provisioner.prov_device()
                _provisioned = True
            except:
                continue
        await provisioner.disconnect()


@cloud_router.post("/upload-edgex-devices", dependencies=[Depends(verify_token)])
async def upload_edgex_devices(devices: list[schemas.BLEDevice]) -> list[schemas.EdgeXDevice]:
    return api_utils.upload_edgex_devices(
        devices=[device.model_dump() for device in devices]
    )
    
@cloud_router.post("/mqtt-connection-status")
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

@cloud_router.post("/edge-sensor-measurement")
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

@cloud_router.post("/lock-devices", dependencies=[Depends(verify_token)])
async def lock_devices(devices: list[schemas.EdgeXDevice]):
    api_utils.set_edgex_devices_admin_state(
        device_names=[device.device_name for device in devices],
        status="LOCKED"
    )

@cloud_router.post("/unlock-devices", dependencies=[Depends(verify_token)])
async def lock_devices(devices: list[schemas.EdgeXDevice]):
    api_utils.set_edgex_devices_admin_state(
        device_names=[device.device_name for device in devices],
        status="UNLOCKED"
    )

@cloud_router.post("/start-devices", dependencies=[Depends(verify_token)])
async def start_devices(devices: list[schemas.EdgeXDevice]):
    api_utils.start_devices(
        device_names=[device.device_name for device in devices],
    )

@cloud_router.post("/stop-devices", dependencies=[Depends(verify_token)])
async def stop_devices(devices: list[schemas.EdgeXDevice]):
    api_utils.stop_devices(
        device_names=[device.device_name for device in devices],
    )

@cloud_router.post("/config-devices", dependencies=[Depends(verify_token)])
async def config_devices(devices: list[schemas.EdgeXDevice], config: schemas.DeviceConfig):
    api_utils.config_devices(
        device_names=[device.device_name for device in devices],
        config=config
    )