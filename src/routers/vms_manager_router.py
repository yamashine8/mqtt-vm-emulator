from typing import Annotated
from fastapi import APIRouter, Depends
from src.dependencies import get_vm_service
from src.services.vm_service import VMService

router = APIRouter(prefix="/manager", tags=["VM manager handlers"])


@router.post("/start_vms")
async def start_vms(
        vm_service: Annotated[
            VMService,
            Depends(get_vm_service),
        ],
        vm_count: int
):
    await vm_service.start_vms(vm_count)
    return {"status": "ok"}

@router.post("/add_vms")
async def add_vms(
        vm_service: Annotated[
            VMService,
            Depends(get_vm_service),
        ],
        vm_count: int
):
    await vm_service.add_vms(vm_count)
    return {"status": "ok"}


@router.post("/stop_vms")
async def stop_vms(
        vm_service: Annotated[
            VMService,
            Depends(get_vm_service),
        ]
):
    await vm_service.stop_vms()
    return {"status": "ok"}


@router.post("/stop_vm")
async def stop_vms(
        vm_service: Annotated[
            VMService,
            Depends(get_vm_service),
        ],
        vm_id
):
    await vm_service.stop_vm(vm_id)
    return {"status": "ok"}


@router.post("/ping_vm")
async def get_vms_list(
        vm_service: Annotated[
            VMService,
            Depends(get_vm_service),
        ],
        vm_id: str
):
    return await vm_service.ping_vm(vm_id)
