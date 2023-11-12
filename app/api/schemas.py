"""
This module contains the pydantic models (schemas) for the API.
08/10/2023
"""

from typing import List
from pydantic import BaseModel, Field

class AuthData(BaseModel):
    pop: str

class EdgeGateway(BaseModel):
    device_name: str
    device_address: str

class BLEDevice(BaseModel):
    device_name: str
    device_address: str

class EdgeXDevice(BaseModel):
    device_name: str
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
    apiVersion: str = Field(..., alias='apiVersion')
    id: str
    deviceName: str
    profileName: str
    sourceName: str
    origin: int
    readings: List[EdgeXReading]

class DeviceConfig(BaseModel):
    ml_model: bool