import asyncio
import logging

from fastapi import HTTPException
from src.vm_supervisor.vm_supervisor import VMSupervisor

logger = logging.getLogger(__name__)


class VMService:
    def __init__(self, amqp_url):
        self.lock = asyncio.Lock()
        self._vm_supervisor: VMSupervisor = None
        self._amqp_url = amqp_url

    async def stop(self):
        if self._vm_supervisor is not None:
            await self.stop_vms()

    async def start_vms(self, vm_count):
        if not self._vm_supervisor:
            async with self.lock:
                if not self._vm_supervisor:
                    self._vm_supervisor = VMSupervisor(vm_count, self._amqp_url)
                    await self._vm_supervisor.start()
        else:
            raise HTTPException(status_code=500, detail="Error while starting supervisor")

    async def add_vms(self, vm_count):
        if self._vm_supervisor:
            await self._vm_supervisor.add_vms(vm_count)
        else:
            raise HTTPException(status_code=404, detail="Supervisor not created yet")

    async def stop_vms(self):
        if self._vm_supervisor:
            async with self.lock:
                if self._vm_supervisor:
                    await self._vm_supervisor.stop()
                    self._vm_supervisor = None
        else:
            raise HTTPException(status_code=404, detail="Supervisor not created yet")

    async def stop_vm(self, vm_id):
        if self._vm_supervisor:
            result = await self._vm_supervisor.stop_vm(vm_id)
            if not result:
                raise HTTPException(status_code=404, detail=f"VM {vm_id} not found")
        else:
            raise HTTPException(status_code=404, detail="Supervisor not created yet")

    async def get_vms(self):
        if self._vm_supervisor:
            result = self._vm_supervisor.get_vms_list()
            return [{"total": len(result)}, {"vms": result}]
        else:
            raise HTTPException(status_code=404, detail="Supervisor not created yet")

    async def ping_vm(self, vm_id):
        if self._vm_supervisor:
            result = await self._vm_supervisor.ping(vm_id)
            if not result:
                raise HTTPException(status_code=404, detail=f"VM {vm_id} not found")
        else:
            raise HTTPException(status_code=404, detail="Supervisor not created yet")
