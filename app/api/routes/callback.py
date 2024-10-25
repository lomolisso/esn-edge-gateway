"""
This module contains the callback routes for the Gateway API.
These routes are accessed only by microservices.
"""

from fastapi import APIRouter, status, HTTPException
from app.core.config import LATENCY_BENCHMARK, ADAPTIVE_INFERENCE, GATEWAY_NAME, POLLING_INTERVAL_MS
from app.api import utils
from app.api.schemas.sensor import command as s_cmd
from app.api.schemas.sensor import response as s_resp
from app.api.schemas.sensor import export as s_export

import time

callback_router = APIRouter(tags=["Callback Routes"])

# --- Command Responses ---

@callback_router.post("/store/sensor/response/get/sensor-state", status_code=status.HTTP_202_ACCEPTED)
async def store_sensor_state_response(response: s_resp.SensorStateResponse):
    response = await utils.store_sensor_state_response(response)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@callback_router.post("/store/sensor/response/get/inference-layer", status_code=status.HTTP_202_ACCEPTED)
async def store_sensor_inference_layer_response(response: s_resp.InferenceLayerResponse):
    response = await utils.store_sensor_inference_layer_response(response)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

@callback_router.post("/store/sensor/response/get/sensor-config", status_code=status.HTTP_202_ACCEPTED)
async def store_sensor_config_response(response: s_resp.SensorConfigResponse):
    response = await utils.store_sensor_config_response(response)
    if response.status_code != status.HTTP_201_CREATED:
        raise HTTPException(status_code=response.status_code, detail=response.json())

# --- Export Routes ---

@callback_router.post("/export/sensor-data", status_code=status.HTTP_201_CREATED)
async def export_sensor_data(sensor_data: s_export.SensorDataExport):
    t0 = time.time() * 1000 # in milliseconds
    print(f"Received sensor data from {sensor_data.metadata.sensor_name}")
    print(f"Receiving from MQTT took {t0-sensor_data.export_value.inference_descriptor.send_timestamp} ms")
    
    # Step 1: verify if sender is registered in the metadata microservice
    sensor_name = sensor_data.metadata.sensor_name
    await utils.verify_target_sensors([sensor_name])

    # Step 2 (Case 1): perform inference if needed
    _inference_descriptor: s_export.InferenceDescriptor = sensor_data.export_value.inference_descriptor
    _inference_layer = _inference_descriptor.inference_layer
    if _inference_layer == s_export.InferenceLayer.GATEWAY:
        # Step 2.1: send prediction request to gateway-inference-ms
        response = await utils.send_prediction_request(sensor_data)
        if response.status_code != status.HTTP_202_ACCEPTED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
        # Step 2.2: poll for prediction result
        task_id = response.json()["task_id"]
        prediction_result, heuristic_result = None, None
        while True:
            response = await utils.get_prediction_result(task_id)
            if response.status_code == status.HTTP_200_OK:
                json_response = response.json()
                if json_response["status"] == "SUCCESS":
                    prediction_result = json_response["result"]["prediction_result"]
                    heuristic_result = json_response["result"]["heuristic_result"]
                    break
                elif json_response["status"] == "FAILURE":
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction task failed.")
                else:   # status == "PENDING"
                    await utils.async_sleep(POLLING_INTERVAL_MS)
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        
        # Step 2.3: Update sensor data with prediction result
        sensor_data.export_value.inference_descriptor.prediction = prediction_result

        # Step 2.4: Export inference latency benchmark if enabled
        if LATENCY_BENCHMARK:
            cmd = s_cmd.InferenceLatencyBenchmark(
                sensor_name=sensor_name,
                inference_layer=s_cmd.InferenceLayer.GATEWAY,
                send_timestamp=_inference_descriptor.send_timestamp,
            )
            await utils.send_inference_latency_benchmark_command(GATEWAY_NAME, sensor_name, cmd)
        
        # Step 2.5: Handle heuristic result if adaptive inference is enabled.
        if ADAPTIVE_INFERENCE:
            await utils.handle_heuristic_result(GATEWAY_NAME, sensor_name, heuristic_result)
            
    # Step 2 (Case 2): export sensor data to the cloud api
    if _inference_layer == s_export.InferenceLayer.CLOUD:
        response = await utils.export_sensor_data(sensor_data)
        if response.status_code != status.HTTP_201_CREATED:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        
@callback_router.post("/export/inference-latency-benchmark", status_code=status.HTTP_201_CREATED)
async def export_inference_latency_benchmark(inf_latency_bench: s_export.InferenceLatencyBenchmarkExport):
    if LATENCY_BENCHMARK:
        response = await utils.export_inference_latency_benchmark(inf_latency_bench)
        if response.status_code != status.HTTP_201_CREATED:
            raise HTTPException(status_code=response.status_code, detail=response.json())
   
