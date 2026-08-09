from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config.settings import get_settings
from src.routers import routers
from src.services.vm_service import VMService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    vm_service = VMService(settings.AMQP_URL)
    app.state.vm_service = vm_service
    yield
    await vm_service.stop()

app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router, prefix="/api")

@app.get("/health")
def read_root():
    return {"status": "ok"}
