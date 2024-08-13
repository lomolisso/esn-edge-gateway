from pydantic import BaseModel

class SensorDescriptor(BaseModel):
    device_name: str
    device_address: str