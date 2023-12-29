import os
from dotenv import load_dotenv

# Retrieve enviroment variables from .env file
load_dotenv()

SECRET_KEY: str = os.environ.get("SECRET_KEY")
APP_BACKEND_URL = os.environ.get("APP_BACKEND_URL")
APP_BACKEND_JWT_TOKEN = os.getenv("APP_BACKEND_JWT_TOKEN")

EDGE_GATEWAY_DEVICE_NAME = os.getenv("EDGE_GATEWAY_DEVICE_NAME")
EDGE_GATEWAY_POP_KEYWORD = os.getenv("EDGE_GATEWAY_POP_KEYWORD")

EDGEX_FOUNDRY_CORE_METADATA_API_URL = os.getenv("EDGEX_FOUNDRY_CORE_METADATA_API_URL")
EDGEX_FOUNDRY_CORE_COMMAND_API_URL = os.getenv("EDGEX_FOUNDRY_CORE_COMMAND_API_URL")
EDGEX_DEVICE_PROFILE_FILE = os.getenv("EDGEX_DEVICE_PROFILE_FILE", "device-profile.yaml")
EDGEX_DEVICE_CONFIG_TEMPLATE_FILE = os.getenv("EDGEX_DEVICE_CONFIG_TEMPLATE_FILE", "edgex-device-config-template.json")

EDGEX_REDIS_URL = os.getenv("EDGEX_REDIS_URL", "redis://localhost:6379")

ESN_BLE_PROV_URL = os.getenv("ESN_BLE_PROV_URL")

TIMEZONE = os.environ.get("TIMEZONE", "Chile/Continental")

ORIGINS: list = [
    APP_BACKEND_URL,
]