from src.routers.vms_info_router import router as vms_info_router
from src.routers.vms_manager_router import router as vms_manager_router

routers = [
    vms_info_router,
    vms_manager_router,
]