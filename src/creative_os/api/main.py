from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from creative_os.api.routes import router
from creative_os.config import get_settings
from creative_os.services.deployment import assert_local_operator_deployment


@asynccontextmanager
async def lifespan(_app: FastAPI):
    assert_local_operator_deployment(get_settings().api_host)
    yield


app = FastAPI(title="Creative OS", version="0.2.1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
