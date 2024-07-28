"""
Routes for the commands sent by the cloud layer.
"""

from fastapi import APIRouter, status, HTTPException

from app.api.schemas.mqtt_sensor_ms import gateway_cmd as gw_cmd_schemas
from app.api.schemas.mqtt_sensor_ms import sensor_cmd as s_cmd_schemas
from app.api.schemas.metadata_ms import metadata as meta_schemas

from app.api import utils

command_router = APIRouter(tags=["Command Routes"])

# --- Gateway Command Routes ---
@command_router.post("/gateway/command/get/available-sensors", status_code=status.HTTP_200_OK)
async def get_avaliable_sensors(_: gw_cmd_schemas.GetAvailableSensors) -> list[gw_cmd_schemas.BLEDevice]:
    response = await utils.ble_discover_sensors()
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return [
        gw_cmd_schemas.BLEDevice(**device) for device in response.json()
    ]
    
@command_router.post("/gateway/command/get/provisioned-sensors", status_code=status.HTTP_200_OK)
async def get_provisioned_sensors(_: gw_cmd_schemas.GetProvisionedSensors) -> list[gw_cmd_schemas.BLEDevice]:
    prov_sensors = await utils.get_provisioned_sensors()
    
    return [
        gw_cmd_schemas.BLEDevice(**device) for device in prov_sensors
    ]

@command_router.post("/gateway/command/add/provisioned-sensors", status_code=status.HTTP_200_OK)
async def add_provisioned_sensor(command: gw_cmd_schemas.AddProvisionedSensors):
    response = await utils.ble_provision_sensors(command.resource_value)
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    prov_sensors = [meta_schemas.SensorDescriptor(**device) for device in response.json()]
    await utils.add_provisioned_sensors(prov_sensors)

    return {
        "message": "Devices provisioned successfully",
    }

@command_router.post("/gateway/command/add/registered-sensors", status_code=status.HTTP_200_OK)
async def add_registered_sensors(command: gw_cmd_schemas.AddRegisteredSensors):
    await utils.metadata_create_sensors(command.resource_value)
    
    return {
        "message": "Devices registered successfully",
    }

@command_router.post("/gateway/command/set/gateway-model", status_code=status.HTTP_202_ACCEPTED)
async def set_gateway_model(command: gw_cmd_schemas.SetGatewayModel):
    response = await utils.set_gateway_model(command.resource_value)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "SET gateway-model Command sent to Gateway Microservice",
    }

# --- Sensor Command Routes ---
@command_router.post("/sensor/command/set/sensor-state", status_code=status.HTTP_202_ACCEPTED)
async def set_sensor_state(command: s_cmd_schemas.SetSensorState):
    await utils.verify_target_sensors(command.target.target_sensors)
    
    # set the sensor state
    response = await utils.set_sensor_state(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "SET sensor-state Command sent to Sensor Microservice",
    }

@command_router.post("/sensor/command/get/sensor-state", status_code=status.HTTP_202_ACCEPTED)
async def get_sensor_state(command: s_cmd_schemas.GetSensorState):
    await utils.verify_target_sensors(command.target.target_sensors)

    # get the sensor state
    response = await utils.get_sensor_state(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "GET sensor-state Command sent to Sensor Microservice",
        "command_uuids": response.json().get("command_uuids"),
    }

@command_router.post("/sensor/command/set/inference-layer", status_code=status.HTTP_202_ACCEPTED)
async def set_inference_layer(command: s_cmd_schemas.SetInferenceLayer):
    await utils.verify_target_sensors(command.target.target_sensors)
    
    # set the inference layer
    response = await utils.set_inference_layer(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "SET inference-layer Command sent to Sensor Microservice",
    }

@command_router.post("/sensor/command/get/inference-layer", status_code=status.HTTP_202_ACCEPTED)
async def get_inference_layer(command: s_cmd_schemas.GetInferenceLayer):
    await utils.verify_target_sensors(command.target.target_sensors)

    # get the inference layer
    response = await utils.get_inference_layer(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "GET inference-layer Command sent to Sensor Microservice",
        "command_uuids": response.json().get("command_uuids"),
    }


@command_router.post("/sensor/command/set/sensor-config", status_code=status.HTTP_202_ACCEPTED)
async def set_sensor_config(command: s_cmd_schemas.SetSensorConfig):
    await utils.verify_target_sensors(command.target.target_sensors)
    
    # set the sensor config
    response = await utils.set_sensor_config(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "SET sensor-config Command sent to Sensor Microservice",
    }

@command_router.post("/sensor/command/get/sensor-config", status_code=status.HTTP_202_ACCEPTED)
async def get_sensor_config(command: s_cmd_schemas.GetSensorConfig):
    await utils.verify_target_sensors(command.target.target_sensors)

    # get the sensor config
    response = await utils.get_sensor_config(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "GET sensor-config Command sent to Sensor Microservice",
        "command_uuids": response.json().get("command_uuids"),    
    }

@command_router.post("/sensor/command/set/sensor-model", status_code=status.HTTP_202_ACCEPTED)
async def set_sensor_model(command: s_cmd_schemas.SetSensorModel):
    await utils.verify_target_sensors(command.target.target_sensors)
    
    # set the sensor model
    response = await utils.set_sensor_model(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "SET sensor-model Command sent to Sensor Microservice",
    }

@command_router.post("/sensor/command/set/inf-latency-bench", status_code=status.HTTP_202_ACCEPTED)
async def set_inf_latency_bench(command: s_cmd_schemas.InferenceLatencyBenchmarkCommand):
    await utils.verify_target_sensors(command.target.target_sensors)
    
    # set the inference latency benchmark
    response = await utils.send_inference_latency_benchmark_command(command)
    if response.status_code != status.HTTP_202_ACCEPTED:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return {
        "message": "SET inf-latency-bench Command sent to Sensor Microservice",
    }
