"""
Sensor Command Response Schemas

GET Commands involving interaction with sensors whether it be direct (MQTT) or indirect (BLE)
require decoupling the response from the request (contrary to a SET command where HTTP status codes
are sufficient).

This module contains the response schemas for the Sensor Commands which fall under the requirements
mentioned above.
"""

from pydantic import BaseModel
from app.api.schemas.sensor.command import SensorConfig, InferenceLayer, SensorState, Method
from app.core.config import GATEWAY_NAME
from typing import Optional

class Metadata(BaseModel):
    """
    Metadata for the response
    """

    sender: str
    gateway_name: str = GATEWAY_NAME
    command_uuid: str

class BaseResponse(BaseModel):
    metadata: Metadata
    property_name: Optional[str] = None
    property_value: object = None
    method: Method = Method.GET

class SensorConfigResponse(BaseResponse):
    property_name: str = "sensor-config"
    property_value: SensorConfig

class InferenceLayerResponse(BaseResponse):
    property_name: str = "inference-layer"
    property_value: InferenceLayer

class SensorStateResponse(BaseResponse):
    property_name: str = "sensor-state"
    property_value: SensorState