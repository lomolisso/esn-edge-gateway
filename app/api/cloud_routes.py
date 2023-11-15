import jwt
from datetime import datetime, timedelta
from app.api import schemas
from app.dependencies import verify_token
from fastapi import APIRouter, HTTPException, Depends, Response
from app.api import utils as api_utils
from app.config import (
    SECRET_KEY,
    EDGE_GATEWAY_DEVICE_NAME,
    EDGE_GATEWAY_POP_KEYWORD,
)

cloud_router = APIRouter(prefix="/cloud")


@cloud_router.post("/auth")
async def authenticate_gateway(auth_data: schemas.AuthDataIn) -> schemas.AuthDataOut:
    if auth_data.pop == EDGE_GATEWAY_POP_KEYWORD:
        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(hours=1)},
            SECRET_KEY,
            algorithm="HS256",
        )
        return schemas.AuthDataOut(jwt_token=token)
    raise HTTPException(status_code=400, detail="Authentication failed.")


@cloud_router.get("/get-gateway-info", dependencies=[Depends(verify_token)])
async def get_gateway_data() -> schemas.EdgeGateway:
    return schemas.EdgeGateway(
        device_name=EDGE_GATEWAY_DEVICE_NAME,
        device_address=api_utils.get_wlan_iface_address(),
    )


@cloud_router.get("/discover-devices", dependencies=[Depends(verify_token)])
async def discover_devices() -> list[schemas.BLEDevice]:
    return api_utils.discover_ble_devices()


@cloud_router.post("/provision-devices", dependencies=[Depends(verify_token)])
async def provision_devices(
    devices: list[schemas.BLEDeviceWithPoP],
) -> schemas.BLEProvResponse:
    return api_utils.provision_ble_devices(devices)


@cloud_router.post("/upload-edgex-devices", dependencies=[Depends(verify_token)])
async def upload_edgex_devices(
    devices: list[schemas.EdgeXDeviceIn],
) -> Response:
    devices = [device.model_dump() for device in devices]
    return api_utils.upload_edgex_devices(devices)


@cloud_router.post("/lock-devices", dependencies=[Depends(verify_token)])
async def lock_devices(devices: list[schemas.EdgeXDeviceIn]) -> Response:
    device_names = [device.device_name for device in devices]
    api_utils.set_edgex_devices_admin_state(device_names=device_names, status="LOCKED")


@cloud_router.post("/unlock-devices", dependencies=[Depends(verify_token)])
async def lock_devices(devices: list[schemas.EdgeXDeviceIn]) -> Response:
    device_names = [device.device_name for device in devices]
    api_utils.set_edgex_devices_admin_state(
        device_names=device_names, status="UNLOCKED"
    )


@cloud_router.post("/start-devices", dependencies=[Depends(verify_token)])
async def start_devices(devices: list[schemas.EdgeXDeviceIn]) -> Response:
    device_names = [device.device_name for device in devices]
    api_utils.start_devices(
        device_names=device_names,
    )


@cloud_router.post("/stop-devices", dependencies=[Depends(verify_token)])
async def stop_devices(devices: list[schemas.EdgeXDeviceIn]) -> Response:
    device_names = [device.device_name for device in devices]
    api_utils.stop_devices(
        device_names=device_names,
    )


@cloud_router.post("/config-devices", dependencies=[Depends(verify_token)])
async def config_devices(
    devices: list[schemas.EdgeXDeviceIn], config: schemas.DeviceConfig
) -> Response:
    device_names = [device.device_name for device in devices]
    api_utils.config_devices(device_names=device_names, config=config)
