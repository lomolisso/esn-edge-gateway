import os
from dotenv import load_dotenv

# Retrieve enviroment variables from .env file
load_dotenv()

# --- Gateway API configuration ---
SECRET_KEY: str = os.environ.get("SECRET_KEY")
GATEWAY_NAME: str = os.environ.get("GATEWAY_NAME")
GATEWAY_API_HOST: str = os.environ.get("GATEWAY_API_HOST")
GATEWAY_API_PORT: int = os.environ.get("GATEWAY_API_PORT")

# --- Microservice URLs ---
INFERENCE_MICROSERVICE_URL: str = os.environ.get("INFERENCE_MICROSERVICE_URL")
BLE_PROV_MICROSERVICE_URL: str = os.environ.get("BLE_PROV_MICROSERVICE_URL")
METADATA_MICROSERVICE_URL: str = os.environ.get("METADATA_MICROSERVICE_URL")
MQTT_SENSOR_MICROSERVICE_URL: str = os.environ.get("MQTT_SENSOR_MICROSERVICE_URL")

# --- Cloud API configuration ---
CLOUD_API_URL: str = os.environ.get("CLOUD_API_URL")


# --- Inference Approach & Benchmarking ---
LATENCY_BENCHMARK: bool = bool(int(os.environ.get("LATENCY_BENCHMARK", "0")))
ADAPTIVE_INFERENCE: bool = bool(int(os.environ.get("ADAPTIVE_INFERENCE", "1")))
POLLING_INTERVAL_MS: int = int(os.environ.get("POLLING_INTERVAL_MS", "100"))

# --- Inference Layer Constants ---
CLOUD_INFERENCE_LAYER = 2
GATEWAY_INFERENCE_LAYER = 1
SENSOR_INFERENCE_LAYER = 0
HEURISTIC_ERROR_CODE = -1

ORIGINS: list = ["*"]
