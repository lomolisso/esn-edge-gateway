import os
from dotenv import load_dotenv

# Retrieve enviroment variables from .env file
load_dotenv()

# --- Gateway API configuration ---
SECRET_KEY: str = os.environ.get("SECRET_KEY", "secret_key")
GATEWAY_NAME: str = os.environ.get("GATEWAY_NAME", "gateway_1")
GATEWAY_API_HOST: str = os.environ.get("GATEWAY_API_HOST", "127.0.0.1")
GATEWAY_API_PORT: int = os.environ.get("GATEWAY_API_PORT", 8004)

# --- Microservice URLs ---
INFERENCE_MICROSERVICE_URL: str = os.environ.get("INFERENCE_MICROSERVICE_URL", "http://127.0.0.1:8005/api/v1")
BLE_PROV_MICROSERVICE_URL: str = os.environ.get("BLE_PROV_MICROSERVICE_URL", "http://127.0.0.1:8006/api/v1")
METADATA_MICROSERVICE_URL: str = os.environ.get("METADATA_MICROSERVICE_URL", "http://127.0.0.1:8007/api/v1")
MQTT_SENSOR_MICROSERVICE_URL: str = os.environ.get("MQTT_SENSOR_MICROSERVICE_URL", "http://127.0.0.1:8008/api/v1")

# --- Cloud API configuration ---
CLOUD_API_URL: str = os.environ.get("CLOUD_API_URL", "http://192.168.0.196:8000/api/v1")


# --- Inference Approach & Benchmarking ---
LATENCY_BENCHMARK: bool = bool(int(os.environ.get("LATENCY_BENCHMARK", "1")))
ADAPTIVE_INFERENCE: bool = bool(int(os.environ.get("ADAPTIVE_INFERENCE", "0")))
POLLING_INTERVAL_MS: int = int(os.environ.get("POLLING_INTERVAL_MS", "100"))

# --- Inference Layer Constants ---
CLOUD_INFERENCE_LAYER = 2
GATEWAY_INFERENCE_LAYER = 1
SENSOR_INFERENCE_LAYER = 0
HEURISTIC_ERROR_CODE = -1

ORIGINS: list = ["*"]
