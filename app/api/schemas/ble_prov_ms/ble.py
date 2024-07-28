from pydantic import BaseModel

class BLEDevice(BaseModel):
    """
    Schema for the BLE Device
    """

    device_name: str
    device_address: str

class BLEDeviceWithPoP(BLEDevice):
    """
    Schema for the BLE Device with PoP
    """

    device_pop: str