from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route

from creative_os.api.company_routes import router as company_router
from creative_os.api.routes import router
from creative_os.config import get_settings
from creative_os.mcp.http_transport import mcp_asgi_app, mcp_session_manager
from creative_os.services.deployment import assert_local_operator_deployment


@asynccontextmanager
async def lifespan(_app: FastAPI):
    assert_local_operator_deployment(get_settings().api_host)
    async with mcp_session_manager.run():
        yield


app = FastAPI(title="Creative OS", version="0.4.1", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
app.include_router(company_router, prefix="/api")
app.router.routes.append(Route("/mcp", endpoint=mcp_asgi_app, methods=["GET", "POST", "DELETE"]))
