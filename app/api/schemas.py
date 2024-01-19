"""
This module contains the pydantic models (schemas) for the API.
08/10/2023
"""

from typing import List
from pydantic import BaseModel, Field


# --- Auth ---
class AuthDataIn(BaseModel):
    pop: str


class AuthDataOut(BaseModel):
    jwt_token: str


# -- Edge Gateway --


class EdgeGateway(BaseModel):
    device_name: str
    device_address: str


# --- Device ---
class Device(BaseModel):
    device_name: str

class DeviceWithAddress(Device):
    device_address: str

class ConfigParams(BaseModel):
    measurement_interval_ms: int

class DeviceConfig(BaseModel):
    devices: list[str]
    params: ConfigParams


# --- BLE ---

BLEDevice = DeviceWithAddress


class BLEDeviceWithPoP(BLEDevice):
    device_pop: str


class BLEProvResponse(BaseModel):
    provisioned: list[str]
    not_provisioned: list[str]


# --- EdgeX ---

EdgeXDeviceIn = DeviceWithAddress


class EdgeXDeviceOut(DeviceWithAddress):
    edgex_device_uuid: str


class EdgeXReading(BaseModel):
    id: str
    origin: int
    deviceName: str
    resourceName: str
    profileName: str
    valueType: str
    value: str


class EdgeXDeviceData(BaseModel):
    apiVersion: str = Field(..., alias="apiVersion")
    id: str
    deviceName: str
    profileName: str
    sourceName: str
    origin: int
    readings: List[EdgeXReading]

class PredictionCommandPayload(BaseModel):
    prediction_source_layer: str
    request_timestamp: int
    measurement: float
    prediction: float
    