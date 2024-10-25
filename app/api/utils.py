from app.core.config import (
    CLOUD_API_URL,
    INFERENCE_MICROSERVICE_URL,
    BLE_PROV_MICROSERVICE_URL,
    METADATA_MICROSERVICE_URL,
    MQTT_SENSOR_MICROSERVICE_URL,
    CLOUD_INFERENCE_LAYER,
    SENSOR_INFERENCE_LAYER,
    HEURISTIC_ERROR_CODE,
)

from fastapi import status, HTTPException
import httpx
import asyncio

from app.api.schemas.gateway import command as gw_cmd
from app.api.schemas.sensor import command as s_cmd
from app.api.schemas.sensor import response as s_resp
from app.api.schemas.sensor import export as s_export
from app.api.schemas import metadata

# --- Async Polling ---
async def async_sleep(ms: int):
    await asyncio.sleep(ms / 1000)


# --- Primitive functions for microservice communication ---

async def _post_json_to_microservice(url: str, json_data: dict):
    async with httpx.AsyncClient() as client:
        return await client.post(url, json=json_data, timeout=30)

async def _put_json_to_microservice(url: str, json_data: dict):
    async with httpx.AsyncClient() as client:
        return await client.put(url, json=json_data, timeout=30)

async def _get_from_microservice(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url, timeout=30)

async def _delete_from_microservice(url: str):
    async with httpx.AsyncClient() as client:
        return await client.delete(url, timeout=30)

# --- Cloud API functions ---
async def store_sensor_state_response(response: s_resp.SensorStateResponse):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/store/sensor/response/get/sensor-state", response.model_dump())

async def store_sensor_inference_layer_response(response: s_resp.InferenceLayerResponse):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/store/sensor/response/get/inference-layer", response.model_dump())

async def store_sensor_config_response(response: s_resp.SensorConfigResponse):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/store/sensor/response/get/sensor-config", response.model_dump())
                                            
async def export_sensor_data(sensor_data: s_export.SensorDataExport):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/export/sensor-data", sensor_data.model_dump())

async def export_inference_latency_benchmark(inference_latency_benchmark: s_export.InferenceLatencyBenchmarkExport):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/export/inference-latency-benchmark", inference_latency_benchmark.model_dump())



# --- BLE Provisioning microservice functions ---

async def ble_discover_sensors():
    return await _get_from_microservice(f"{BLE_PROV_MICROSERVICE_URL}/discover")

async def ble_provision_sensors(devices: list[gw_cmd.BLEDeviceWithPoP]):
    json_payload = [device.model_dump() for device in devices]
    return await _post_json_to_microservice(f"{BLE_PROV_MICROSERVICE_URL}/provision", json_data=json_payload)

# --- Inference microservice functions ---

async def set_gateway_model(gateway_model: gw_cmd.GatewayModel):
    return await _post_json_to_microservice(f"{INFERENCE_MICROSERVICE_URL}/model/upload", gateway_model.model_dump())

async def send_prediction_request(prediction_request: s_export.SensorDataExport):
    return await _put_json_to_microservice(f"{INFERENCE_MICROSERVICE_URL}/model/prediction/request", prediction_request.model_dump())

async def get_prediction_result(task_id: str):
    return await _get_from_microservice(f"{INFERENCE_MICROSERVICE_URL}/model/prediction/result/{task_id}")

# --- Metadata microservice functions ---
async def get_registered_sensors():
    return await _get_from_microservice(f"{METADATA_MICROSERVICE_URL}/sensors")

async def verify_target_sensors(target_names: list[str]):
    response = await get_registered_sensors()
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    registered_names = [metadata.SensorDescriptor(**sensor).device_name for sensor in response.json()]

    for name in target_names:
        if name not in registered_names:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sensor '{name}' is not registered")

async def metadata_create_sensors(sensors: list[metadata.SensorDescriptor]):
    for sensor in sensors:
        response = await _post_json_to_microservice(f"{METADATA_MICROSERVICE_URL}/sensor", sensor.model_dump())
        if response.status_code != status.HTTP_201_CREATED:
            raise HTTPException(status_code=response.status_code, detail=response.json())

async def metadata_update_sensors(sensors: list[metadata.SensorDescriptor], fields: dict):
    for sensor in sensors:
        response = await _put_json_to_microservice(
            url=f"{METADATA_MICROSERVICE_URL}/sensor/{sensor.device_name}", 
            json_data={**fields, **sensor.model_dump()}
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
async def metadata_get_sensors():
    return await _get_from_microservice(f"{METADATA_MICROSERVICE_URL}/sensors")

async def get_provisioned_sensors():
    response = await metadata_get_sensors()
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return [sensor for sensor in response.json() if sensor["provisioned"]]

async def add_provisioned_sensors(sensors: list[metadata.SensorDescriptor]):
    await metadata_update_sensors(sensors, fields={"provisioned": True})


# --- Sensor microservice functions ---

async def set_sensor_state(
    command: s_cmd.SetSensorState,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/sensor-state",
        command.model_dump(),
    )

async def get_sensor_state(
    command: s_cmd.GetSensorState,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/get/sensor-state",
        command.model_dump(),
    )

async def set_inference_layer(
    command: s_cmd.SetInferenceLayer,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/inference-layer",
        command.model_dump(),
    )

async def get_inference_layer(
    command: s_cmd.GetInferenceLayer,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/get/inference-layer",
        command.model_dump(),
    )

async def set_sensor_config(
    command: s_cmd.SetSensorConfig,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/sensor-config",
        command.model_dump(),
    )

async def get_sensor_config(
    command: s_cmd.GetSensorConfig,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/get/sensor-config",
        command.model_dump(),
    )

async def set_sensor_model(
    command: s_cmd.SetSensorModel,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/sensor-model",
        command.model_dump(),
    )

async def send_inference_latency_benchmark_command(
    gateway_name: str,
    sensor_name: str,
    inf_latency_bench: s_cmd.InferenceLatencyBenchmark,
):
    command = s_cmd.InferenceLatencyBenchmarkCommand(
        target = await get_gateway_api_with_sensors(gateway_name, [sensor_name]),
        property_value=inf_latency_bench
    )
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/inf-latency-bench",
        command.model_dump(),
    )

# --- Gateway Adaptive Heuristic ---
async def get_gateway_api_with_sensors(gateway_name: str, target_sensors: list[str]):
    return s_cmd.GatewayAPIWithSensors(
        gateway_name=gateway_name,
        target_sensors=target_sensors
    )

async def handle_heuristic_result(gateway_name: str, sensor_name: str, heuristic_result: int):
    gateway_api_with_sensors = await get_gateway_api_with_sensors(gateway_name, [sensor_name])
    if heuristic_result == HEURISTIC_ERROR_CODE:    # set sensor state to error
        command = s_cmd.SetSensorState(
            target=gateway_api_with_sensors,
            property_value=s_cmd.SensorState.ERROR
        )
        response = await set_sensor_state(command)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    elif heuristic_result == SENSOR_INFERENCE_LAYER:    # set sensor inference layer to sensor
        command = s_cmd.SetInferenceLayer(
            target=gateway_api_with_sensors,
            property_value=s_cmd.InferenceLayer.SENSOR
        )
        response = await set_inference_layer(command)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    elif heuristic_result == CLOUD_INFERENCE_LAYER:
        command = s_cmd.SetInferenceLayer(
            target=gateway_api_with_sensors,
            property_value=s_cmd.InferenceLayer.CLOUD
        )
        response = await set_inference_layer(command)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
