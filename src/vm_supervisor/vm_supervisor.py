import asyncio
import logging
from dataclasses import dataclass

from src.utils.publisher_utils import generate_name
from src.vm_emulator.vm_emulator import VMEmulator

logger = logging.getLogger(__name__)


@dataclass
class VMContext:
    vm: VMEmulator
    queue: asyncio.Queue


class VMSupervisor:
    CREATE_EMULATOR_TIMEOUT = 1

    def __init__(self, vm_count: int):
        self.vm_count = vm_count
        self.vm_storage = {}

    def get_vms_list(self):
        result = [str(ctx.vm) for ctx in self.vm_storage.values()]
        return result

    async def start(self):
        asyncio.create_task(self.create_vms(), name="Create VMs task")

    async def stop(self):
        if self.vm_storage:
            await self.stop_all()

    async def _spawn_vm(self):
        queue = asyncio.Queue()
        vm_name = generate_name()

        while vm_name in self.vm_storage:
            vm_name = generate_name()

        vm = VMEmulator(vm_name, queue)

        try:
            await vm.start()
            self.vm_storage[vm_name] = VMContext(vm, queue)
        except Exception as e:
            logger.error("Failed to create vm %s: %s", vm, e)

    async def create_vms(self):
        try:
            for i in range(self.vm_count):
                await self._spawn_vm()
        except Exception as e:
            logger.error("Failed to create: %s", e)

    async def add_vms(self, vm_count):
        try:
            for i in range(vm_count):
                await self._spawn_vm()
        except Exception as e:
            logger.error("Failed to create: %s", e)

    async def stop_vm(self, vm_id):
        vm_context = self.vm_storage.get(vm_id, None)
        if vm_context:
            self.vm_storage.pop(vm_id)
            await vm_context.vm.stop()
            return True
        return False

    async def stop_all(self):
        for ctx in self.vm_storage.values():
            try:
                await ctx.vm.stop()
            except Exception as e:
                logger.error("ctx didnt stop after request: %s",  e)

    async def ping(self, vm_id):
        vm_context = self.vm_storage.get(vm_id, None)
        if vm_context:
            await vm_context.queue.put("ping")
            return True
        return False
