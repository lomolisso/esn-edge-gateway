from typing import Union
import netifaces
import json
from app.api import schemas
import copy
import requests
from app.config import (
    EDGEX_FOUNDRY_CORE_METADATA_API_URL,
    EDGEX_FOUNDRY_CORE_COMMAND_API_URL,
    EDGEX_DEVICE_PROFILE_FILE,
    EDGEX_DEVICE_CONFIG_TEMPLATE_FILE,
    APP_BACKEND_URL,
    APP_BACKEND_JWT_TOKEN,
)


# --- APP BACKEND API CALLS ---
def post_json_to_app_backend(endpoint: str, json_data: Union[dict, list]):
    # Sends a POST request to the app backend
    response = requests.post(
        url=f"{APP_BACKEND_URL}{endpoint}",
        json=json_data,
        headers={"Authorization": f"Bearer {APP_BACKEND_JWT_TOKEN}"},
    )
    if response.status_code != 200:
        raise Exception(f"API call failed. Status code: {response.status_code}")
    return response.json()


# --- NETWORK UTILS ---
def get_wlan_iface_address(iface: str):
    try:
        mac = netifaces.ifaddresses(iface)[netifaces.AF_LINK][0]["addr"]
        return mac.upper()
    except (KeyError, IndexError):
        return None


# --- EDGEX MICROSERVICES API CALLS ---
def _patch_edgex_metadata_devices(device_names: list[str], template: dict):
    """
    Makes a PATCH request to EdgeX core-metadata API to update devices
    based on a provided template.
    """
    edgex_devices_payload = []
    for dev_name in device_names:
        edgex_device = copy.deepcopy(template)
        edgex_device["device"]["name"] = dev_name
        edgex_devices_payload.append(edgex_device)

    response = requests.patch(
        url=f"{EDGEX_FOUNDRY_CORE_METADATA_API_URL}/device", json=edgex_devices_payload
    )
    if response.status_code != 207:
        raise Exception(f"API call failed. Status code: {response.status_code}")

    for dev_name, dev_response in zip(device_names, response.json()):
        if dev_response["statusCode"] != 200:
            raise Exception(
                f"API call failed. Failed to update device {dev_name} in edgeX. Status code: {dev_response['statusCode']}"
            )

    return response.json()


def _post_edgex_metadata_devices(devices):
    """
    Makes a POST request to EdgeX core-metadata API to create devices.
    """
    response = requests.post(
        url=f"{EDGEX_FOUNDRY_CORE_METADATA_API_URL}/device", json=devices
    )
    if response.status_code != 207:
        raise Exception(f"API call failed. Status code: {response.status_code}")

    # Check if all devices were created successfully
    device_names = [device["device"]["name"] for device in devices]
    dev_iterator = zip(device_names, response.json())

    _edgex_devices = []
    for dev_name, dev_response in dev_iterator:
        if dev_response["statusCode"] != 201:
            raise Exception(f"Failed to create device {dev_name} in edgeX. Status code: {dev_response['statusCode']}")

        _edgex_devices.append(schemas.EdgeXDevice(device_name=dev_name, edgex_device_uuid=dev_response["id"]))
    return _edgex_devices


def upload_edgex_device_profile():
    """
    Reads the device profile file and uploads it to EdgeX core-metadata API.
    """
    with open(f"app/static/{EDGEX_DEVICE_PROFILE_FILE}", "rb") as yaml_file:
        response = requests.post(
            url=f"{EDGEX_FOUNDRY_CORE_METADATA_API_URL}/deviceprofile/uploadfile",
            files={"file": (EDGEX_DEVICE_PROFILE_FILE, yaml_file)},
        )
        if response.status_code != 201:
            raise Exception(
                f"API call failed. Status code: {response.status_code, response.json()}"
            )

    return response.json()


def upload_edgex_devices(devices):
    """
    Uploads to EdgeX core-metadata API the provided devices based on the
    device config template file.
    """
    # Load edgex device template for core metadata API
    with open(f"app/static/{EDGEX_DEVICE_CONFIG_TEMPLATE_FILE}", "r") as json_file:
        edgex_device_template = json.load(json_file)

    # Create edgex device config for each device
    edgex_devices_payload = []
    for device in devices:
        edgex_device = copy.deepcopy(edgex_device_template)
        edgex_device["device"]["name"] = device["device_name"]
        edgex_device["device"]["description"] = device["device_address"]
        edgex_device["device"]["protocols"]["mqtt"][
            "CommandTopic"
        ] = f"command/{device['device_name']}"
        edgex_devices_payload.append(edgex_device)

    return _post_edgex_metadata_devices(edgex_devices_payload)


def set_edgex_device_operating_state(device_name, status):
    """
    Sets the 'operatingState' of a device in EdgeX core-metadata API
    to a given status. Valid statuses are: "UP" and "DOWN".
    """
    assert status in ["UP", "DOWN"]
    _patch_edgex_metadata_devices(
        [device_name],
        template={
            "apiVersion": "v3",
            "device": {
                "operatingState": f"{status}",
            },
        },
    )


def set_edgex_devices_admin_state(device_names, status):
    """
    Sets the 'adminState' of a device in EdgeX core-metadata API
    to a given status. Valid statuses are: "UNLOCKED" and "LOCKED".
    """
    assert status in ["UNLOCKED", "LOCKED"]
    _patch_edgex_metadata_devices(
        device_names,
        template={
            "apiVersion": "v3",
            "device": {
                "adminState": f"{status}",
            },
        },
    )


def _run_edgex_device_set_command(device_name, command, payload):
    """
    Runs a SET command for a given device by making a PUT request
    to EdgeX core-command API. The payload must be a dict that
    includes the deviceResource name and the value to set.
    """
    response = requests.put(
        url=f"{EDGEX_FOUNDRY_CORE_COMMAND_API_URL}/device/name/{device_name}/{command}",
        json=payload,
    )
    print("EdgeX SET command response:", response.json())
    if response.status_code != 200:
        raise Exception(f"API call failed. Status code: {response.status_code}")

    return response.json()


def _run_edgex_device_get_command(device, command):
    """
    Runs a GET command for a given device by making a GET request
    to EdgeX core-command API.
    """
    response = requests.get(
        url=f"{EDGEX_FOUNDRY_CORE_COMMAND_API_URL}/device/name/{device}/{command}",
    )
    print("EdgeX GET command response:", response.json())
    if response.status_code != 200:
        raise Exception(f"API call failed. Status code: {response.status_code}")

    return response.json()


def start_devices(device_names):
    """
    Starts the devices by setting the 'working-status' deviceResource to true.
    """
    for dev_name in device_names:
        _run_edgex_device_set_command(
            device_name=dev_name,
            command="working-status",
            payload={'working-status': 'true'},
        )

def stop_devices(device_names):
    """
    Stops the devices by setting the 'working-status' deviceResource to false.
    """
    for dev_name in device_names:
        _run_edgex_device_set_command(
            device_name=dev_name,
            command="working-status",
            payload={"working-status": "false"},
        )

def config_devices(device_names, config):
    """
    Configures the devices by setting the 'ml-model' deviceResource to true or false.
    """
    for dev_name in device_names:
        _run_edgex_device_set_command(
            device_name=dev_name,
            command="config",
            payload={"ml-model": "true" if config.ml_model else "false"},
        )