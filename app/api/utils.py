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

from app.api.schemas.mqtt_sensor_ms import export as export_schemas
from app.api.schemas.mqtt_sensor_ms import sensor_cmd as s_cmd_schemas
from app.api.schemas.mqtt_sensor_ms import sensor_resp as s_resp_schemas

from app.api.schemas.ble_prov_ms import ble as ble_schemas
from app.api.schemas.inference_ms import inference as inf_schemas
from app.api.schemas.metadata_ms import metadata as meta_schemas



# --- Primitive functions for microservice communication ---

async def _post_json_to_microservice(url: str, json_data: dict):
    async with httpx.AsyncClient() as client:
        return await client.post(url, json=json_data)

async def _put_json_to_microservice(url: str, json_data: dict):
    async with httpx.AsyncClient() as client:
        return await client.put(url, json=json_data)

async def _get_from_microservice(url: str):
    async with httpx.AsyncClient() as client:
        return await client.get(url)

async def _delete_from_microservice(url: str):
    async with httpx.AsyncClient() as client:
        return await client.delete(url)

# --- Cloud API functions ---
async def store_sensor_state_response(response: s_resp_schemas.SensorStateResponse):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/store/sensor/response/get/sensor-state", response.model_dump())

async def store_sensor_inference_layer_response(response: s_resp_schemas.InferenceLayerResponse):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/store/sensor/response/get/inference-layer", response.model_dump())

async def store_sensor_config_response(response: s_resp_schemas.SensorConfigResponse):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/store/sensor/response/get/sensor-config", response.model_dump())
                                            
async def export_sensor_reading(sensor_reading: export_schemas.SensorReadingExport):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/export/sensor-reading", sensor_reading.model_dump())

async def export_prediction_request(prediction_request: export_schemas.PredictionRequestExport):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/export/prediction-request", prediction_request.model_dump())

async def export_prediction_result(prediction_result: export_schemas.PredictionResultExport):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/export/prediction-result", prediction_result.model_dump())

async def export_inference_latency_benchmark(inference_latency_benchmark: export_schemas.InferenceLatencyBenchmarkExport):
    return await _post_json_to_microservice(f"{CLOUD_API_URL}/export/inference-latency-benchmark", inference_latency_benchmark.model_dump())



# --- BLE Provisioning microservice functions ---

async def ble_discover_sensors():
    return await _get_from_microservice(f"{BLE_PROV_MICROSERVICE_URL}/discover")

async def ble_provision_sensors(devices: list[ble_schemas.BLEDeviceWithPoP]):
    json_payload = [device.model_dump() for device in devices]
    return await _post_json_to_microservice(f"{BLE_PROV_MICROSERVICE_URL}/provision", json_data=json_payload)

# --- Inference microservice functions ---

async def set_gateway_model(gateway_model: inf_schemas.GatewayModel):
    return await _post_json_to_microservice(f"{INFERENCE_MICROSERVICE_URL}/model/upload", gateway_model.model_dump())

async def send_prediction_request(prediction_request: inf_schemas.PredictionRequestExport):
    return await _put_json_to_microservice(f"{INFERENCE_MICROSERVICE_URL}/model/prediction/request", prediction_request.model_dump())

# --- Metadata microservice functions ---
async def get_registered_sensors():
    return await _get_from_microservice(f"{METADATA_MICROSERVICE_URL}/sensors")

async def verify_target_sensors(target_names: list[str]):
    response = await get_registered_sensors()
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    registered_names = [meta_schemas.SensorDescriptor(**sensor).device_name for sensor in response.json()]

    for name in target_names:
        if name not in registered_names:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sensor '{name}' is not registered")

async def metadata_create_sensors(sensors: list[meta_schemas.SensorDescriptor]):
    for sensor in sensors:
        response = await _post_json_to_microservice(f"{METADATA_MICROSERVICE_URL}/sensor", sensor.model_dump())
        if response.status_code != status.HTTP_201_CREATED:
            raise HTTPException(status_code=response.status_code, detail=response.json())

async def metadata_update_sensors(sensors: list[meta_schemas.SensorDescriptor], fields: dict):
    for sensor in sensors:
        response = await _put_json_to_microservice(
            url=f"{METADATA_MICROSERVICE_URL}/sensor/{sensor.device_name}", 
            json_data={**fields, **sensor.model_dump()}
        )
        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
async def metadata_get_sensors():
    return await _get_from_microservice(f"{METADATA_MICROSERVICE_URL}/sensor")

async def get_provisioned_sensors():
    response = await metadata_get_sensors()
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return [sensor for sensor in response.json() if sensor["provisioned"]]

async def add_provisioned_sensors(sensors: list[meta_schemas.SensorDescriptor]):
    await metadata_update_sensors(sensors, fields={"provisioned": True})


# --- Sensor microservice functions ---

async def set_sensor_state(
    command: s_cmd_schemas.SetSensorState,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/sensor-state",
        command.model_dump(),
    )

async def get_sensor_state(
    command: s_cmd_schemas.GetSensorState,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/get/sensor-state",
        command.model_dump(),
    )

async def set_inference_layer(
    command: s_cmd_schemas.SetInferenceLayer,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/inference-layer",
        command.model_dump(),
    )

async def get_inference_layer(
    command: s_cmd_schemas.GetInferenceLayer,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/get/inference-layer",
        command.model_dump(),
    )

async def set_sensor_config(
    command: s_cmd_schemas.SetSensorConfig,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/sensor-config",
        command.model_dump(),
    )

async def get_sensor_config(
    command: s_cmd_schemas.GetSensorConfig,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/get/sensor-config",
        command.model_dump(),
    )

async def set_sensor_model(
    command: s_cmd_schemas.SetSensorModel,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/sensor-model",
        command.model_dump(),
    )

async def send_inference_latency_benchmark_command(
    command: s_cmd_schemas.InferenceLatencyBenchmarkCommand,
):
    return await _post_json_to_microservice(
        f"{MQTT_SENSOR_MICROSERVICE_URL}/sensor/command/set/inf-latency-bench",
        command.model_dump(),
    )

# --- Gateway Adaptive Heuristic ---
async def get_gateway_api_with_sensors(gateway_name: str, target_sensors: list[str]):
    return s_cmd_schemas.GatewayAPIWithSensors(
        gateway_name=gateway_name,
        target_sensors=target_sensors
    )

async def handle_heuristic_result(gateway_name: str, sensor_name: str, heuristic_result: int):
    gateway_api_with_sensors = await get_gateway_api_with_sensors(gateway_name, [sensor_name])
    if heuristic_result == HEURISTIC_ERROR_CODE:    # set sensor state to error
        command = s_cmd_schemas.SetSensorState(
            target=gateway_api_with_sensors,
            resource_value=s_cmd_schemas.SensorState.ERROR
        )
        response = await set_sensor_state(command)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    elif heuristic_result == SENSOR_INFERENCE_LAYER:    # set sensor inference layer to sensor
        command = s_cmd_schemas.SetInferenceLayer(
            target=gateway_api_with_sensors,
            resource_value=s_cmd_schemas.InferenceLayer.SENSOR
        )
        response = await set_inference_layer(command)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    elif heuristic_result == CLOUD_INFERENCE_LAYER:
        command = s_cmd_schemas.SetInferenceLayer(
            target=gateway_api_with_sensors,
            resource_value=s_cmd_schemas.InferenceLayer.CLOUD
        )
        response = await set_inference_layer(command)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
