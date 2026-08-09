from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.routers import routers
from src.services.vm_service import VMService


@asynccontextmanager
async def lifespan(app: FastAPI):
    vm_service = VMService()
    app.state.vm_service = vm_service
    yield
    await vm_service.stop()

app = FastAPI(lifespan=lifespan)

for router in routers:
    app.include_router(router, prefix="/api")

@app.get("/health")
def read_root():
    return {"status": "ok"}
