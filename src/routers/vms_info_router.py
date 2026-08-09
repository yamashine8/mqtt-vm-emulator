from typing import Annotated
from fastapi import APIRouter, Depends
from src.dependencies import get_vm_service
from src.services.vm_service import VMService

router = APIRouter(prefix="/status", tags=["VM Status handlers"])


@router.get("/vms_list")
async def get_vms_list(
        vm_service: Annotated[
            VMService,
            Depends(get_vm_service),
        ]
):
    return await vm_service.get_vms()
