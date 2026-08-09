from fastapi import Request

from src.services.vm_service import VMService


def get_vm_service(
    request: Request,
) -> VMService:
    return request.app.state.vm_service
