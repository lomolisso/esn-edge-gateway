"""
This module contains the callback routes for the Gateway API.
These routes are accessed only by microservices.
"""

from fastapi import APIRouter, status, HTTPException
from app.core.config import CLOUD_INFERENCE_LAYER, GATEWAY_INFERENCE_LAYER, LATENCY_BENCHMARK, ADAPTIVE_INFERENCE, GATEWAY_NAME
from app.api.schemas.mqtt_sensor_ms import export as export_schemas
from app.api.schemas.mqtt_sensor_ms import sensor_resp as s_resp_schemas
from app.api.schemas.mqtt_sensor_ms import sensor_cmd as s_cmd_schemas
from app.api import utils


callback_router = APIRouter(tags=["Callback Routes"])


# --- Command Responses ---

@callback_router.post("/store/sensor/response/get/sensor-state", status_code=status.HTTP_202_ACCEPTED)
async def store_sensor_state_response(response: s_resp_schemas.SensorStateResponse):
    response = await utils.store_sensor_state_response(response)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@callback_router.post("/store/sensor/response/get/inference-layer", status_code=status.HTTP_202_ACCEPTED)
async def store_sensor_inference_layer_response(response: s_resp_schemas.InferenceLayerResponse):
    response = await utils.store_sensor_inference_layer_response(response)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@callback_router.post("/store/sensor/response/get/sensor-config", status_code=status.HTTP_202_ACCEPTED)
async def store_sensor_config_response(response: s_resp_schemas.SensorConfigResponse):
    response = await utils.store_sensor_config_response(response)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

# --- Export Routes ---

@callback_router.post("/export/sensor-reading", status_code=status.HTTP_201_CREATED)
async def export_sensor_data(sensor_reading: export_schemas.SensorReadingExport):
    response = await utils.export_sensor_reading(sensor_reading)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
@callback_router.post("/export/prediction-request", status_code=status.HTTP_202_ACCEPTED)
async def export_prediction_request(prediction_request: export_schemas.PredictionRequestExport):
    request_inference_layer = prediction_request.export_value.inference_descriptor.inference_layer
    # Case 1: if the request's inference layer is cloud, send the request to the cloud api
    if request_inference_layer == CLOUD_INFERENCE_LAYER:
        response = await utils.export_prediction_request(prediction_request)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    
    # Case 2: if the request's inference layer is gateway, send the request to the inference microservice
    elif request_inference_layer == GATEWAY_INFERENCE_LAYER:
        response = await utils.send_prediction_request(prediction_request)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    
    # Case 3: else, return an error
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inference layer must be cloud or gateway.")

@callback_router.post("/export/prediction-result", status_code=status.HTTP_201_CREATED)
async def export_prediction_result(prediction_result: export_schemas.PredictionResultExport):    
    # Step 1: export prediction result to the cloud api
    response = await utils.export_prediction_result(prediction_result)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    sensor_name = prediction_result.metadata.sensor_name
    reading_uuid = prediction_result.export_value.reading_uuid
    inference_layer = prediction_result.export_value.inference_layer
    if inference_layer == GATEWAY_INFERENCE_LAYER:
        # Step 2: Handle heuristic result if adaptive inference is enabled.
        # Note only gateway predictions are handled as sensor predictions are handled by the sensor.
        if ADAPTIVE_INFERENCE:
            heuristic_result = prediction_result.export_value.heuristic_result
            await utils.handle_heuristic_result(GATEWAY_NAME, sensor_name, heuristic_result)
        if LATENCY_BENCHMARK:
            gateway_api_with_sensors = await utils.get_gateway_api_with_sensors(GATEWAY_NAME, [sensor_name])
            command = s_cmd_schemas.InferenceLatencyBenchmarkCommand(
                target=gateway_api_with_sensors,
                resource_value=s_cmd_schemas.InferenceLatencyBenchmark(
                    reading_uuid=reading_uuid,
                    send_timestamp=prediction_result.export_value.send_timestamp,
                )
            )
            response = await utils.send_inference_latency_benchmark_command(command)
            if response.status_code != status.HTTP_202_ACCEPTED:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        
@callback_router.post("/export/inference-latency-benchmark", status_code=status.HTTP_201_CREATED)
async def export_inference_latency_benchmark(inf_latency_bench: export_schemas.InferenceLatencyBenchmarkExport):
    if LATENCY_BENCHMARK:
        response = await utils.export_inference_latency_benchmark(inf_latency_bench)
        if response.status_code != status.HTTP_201_CREATED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
   
