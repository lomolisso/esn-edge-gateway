import base64
import jwt
from datetime import datetime, timedelta
from app.api import schemas
from app.dependencies import verify_token, get_redis
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Depends,
    Path,
    Response,
    UploadFile,
)
from app.api import utils as api_utils
from app.config import (
    SECRET_KEY,
    EDGE_GATEWAY_DEVICE_NAME,
    EDGE_GATEWAY_POP_KEYWORD,
)

cloud_router = APIRouter(prefix="/cloud")

# --- Gateway Commands ---

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


@cloud_router.get("/gateway", dependencies=[Depends(verify_token)])
async def get_gateway_data() -> schemas.EdgeGateway:
    return schemas.EdgeGateway(
        device_name=EDGE_GATEWAY_DEVICE_NAME,
        device_address=api_utils.get_wlan_iface_address(),
    )

@cloud_router.post("/gateway/predictive-model", dependencies=[Depends(verify_token)])
async def upload_gateway_predictive_model(
    predictive_model: UploadFile = File(...),
) -> Response:
    model_bytes = await predictive_model.read()
    model_size = len(model_bytes)
    b64_encoded_model = base64.b64encode(model_bytes).decode("utf-8")
    
    # Send the model to the gateway predictive node
    return await api_utils.update_predictive_model(
        model={"model_size": model_size, "b64_encoded_model": b64_encoded_model},
    )

# --- Device Commands ---

@cloud_router.post("/devices/upload-edgex", dependencies=[Depends(verify_token)])
async def upload_edgex_devices(
    devices: list[schemas.EdgeXDeviceIn],
) -> Response:
    devices = [device.model_dump() for device in devices]
    return api_utils.upload_edgex_devices(devices)


@cloud_router.get("/devices/discover", dependencies=[Depends(verify_token)])
async def discover_devices() -> list[schemas.BLEDevice]:
    return api_utils.discover_ble_devices()


@cloud_router.post("/devices/provision", dependencies=[Depends(verify_token)])
async def provision_devices(
    devices: list[schemas.BLEDeviceWithPoP],
) -> schemas.BLEProvResponse:
    return api_utils.provision_ble_devices(devices)


@cloud_router.post("/devices/predictive-model", dependencies=[Depends(verify_token)])
async def devices_predictive_model(
    predictive_model: UploadFile = File(...),
    devices: list[str] = Form(...),
    redis_client=Depends(get_redis),
) -> Response:
    model_bytes = await predictive_model.read()
    model_size = len(model_bytes)
    b64_encoded_model = base64.b64encode(model_bytes).decode("utf-8")
    await api_utils.update_predictive_model(
        redis_client=redis_client,
        devices=devices,
        model={"model_size": model_size, "b64_encoded_model": b64_encoded_model},
    )


@cloud_router.post("/devices/config", dependencies=[Depends(verify_token)])
async def config_devices(
    config: schemas.DeviceConfig,
    redis_client=Depends(get_redis),
) -> Response:
    await api_utils.config_devices(
        redis_client=redis_client,
        devices=config.devices,
        config=config.params.model_dump(),
    )


@cloud_router.post("/devices/ready", dependencies=[Depends(verify_token)])
async def ready_devices(
    devices: list[str] = Form(...),
    redis_client=Depends(get_redis),
) -> Response:
    await api_utils.devices_ready(
        redis_client=redis_client,
        devices=devices,
    )


@cloud_router.post("/devices/start", dependencies=[Depends(verify_token)])
async def start_devices(
    devices: list[str] = Form(...),
    redis_client=Depends(get_redis)
) -> Response:
    await api_utils.start_devices(
        redis_client=redis_client,
        devices=devices,
    )


@cloud_router.post("/devices/stop", dependencies=[Depends(verify_token)])
async def stop_devices(
    devices: list[str] = Form(...),
    redis_client=Depends(get_redis)
) -> Response:
    await api_utils.stop_devices(
        redis_client=redis_client,
        devices=devices,
    )


@cloud_router.post("/devices/reset", dependencies=[Depends(verify_token)])
async def reset_devices(
    devices: list[str] = Form(...),
    redis_client=Depends(get_redis)
) -> Response:
    await api_utils.reset_devices(
        redis_client=redis_client,
        devices=devices,
    )

