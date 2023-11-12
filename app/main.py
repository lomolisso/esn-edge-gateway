from fastapi import APIRouter, FastAPI

from app.config import SECRET_KEY, ORIGINS
from .api.edgex_routes import edgex_router
from .api.cloud_routes import cloud_router

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(debug=True)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
main_router = APIRouter(prefix="/gateway-api")
main_router.include_router(cloud_router)
main_router.include_router(edgex_router)
app.include_router(main_router)
