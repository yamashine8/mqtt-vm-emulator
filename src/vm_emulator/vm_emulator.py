import asyncio
import json
import random
from dataclasses import asdict

import aio_pika

from src.mixins.message_generator_mixin import MessageGeneratorMixin
from src.model.rmq_message_type import RMQMessage, RMQMessagePayload
from src.utils.vm_emulator_utils import collect_handler, MessageHandlers

import logging

logger = logging.getLogger(__name__)

class VMEmulator(MessageGeneratorMixin):
    message_handlers: MessageHandlers = {}
    MESSAGE_TYPE_STATUS = "status"

    def __init__(self, identity: str, queue):
        self.identity: str = identity
        self._life_cycle_task: asyncio.Task = None
        self._command_task = None
        self.event_queue = queue
        self.log_counter = 0

        self.command_router = self.message_handlers

        self.url = "amqp://guest:guest@localhost/"
        self.amqp_connection = None
        self.amqp_exchange = None
        self.amqp_queue = None
        self.amqp_channel = None


    def __str__(self):
        return f"VM Emulator {self.identity}, logs sent: {self.log_counter}"

    async def start(self):
        await self.connect_to_channel()
        self._life_cycle_task = asyncio.create_task(self._life_cycle())
        self._command_task = asyncio.create_task(self._command_loop())


    async def connect_to_channel(self):
        self.amqp_connection = await aio_pika.connect_robust(self.url)
        self.amqp_channel = await self.amqp_connection.channel()

        self.amqp_exchange = await self.amqp_channel.declare_exchange(
            "app.events",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        self.amqp_queue = await self.amqp_channel.declare_queue(
            f"virtual_machine.{self.identity}.commands",
            durable=False,
            exclusive=True,
        )

        await self.amqp_queue.bind(
            self.amqp_exchange,
            routing_key=f"virtual_machines.{self.identity}.commands.*",
        )

        await self.amqp_queue.consume(self.handle_message)

    async def handle_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            body = message.body.decode()
            await self.send_message(RMQMessage("response", RMQMessagePayload(self.identity, {"message": "response"})))
            print(body, self.identity, message.routing_key)

    async def send_message(self, message: RMQMessage):
        if self.amqp_exchange is None:
            raise RuntimeError("Publisher is not connected")

        payload = aio_pika.Message(
            body=json.dumps(asdict(message.message), default=str).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self.amqp_exchange.publish(
            payload,
            routing_key=message.topic,
        )

    async def _life_cycle(self):
        while True:
            message_body = self._generate_message()
            payload = RMQMessage(self.MESSAGE_TYPE_STATUS, RMQMessagePayload(self.identity, message_body))
            asyncio.create_task(self.send_message(payload))
            self.log_counter = self.log_counter + 1
            await asyncio.sleep(self._get_message_timeout())

    async def stop(self):
        if self._life_cycle_task:
            self._life_cycle_task.cancel()
            try:
                await self._life_cycle_task
            except asyncio.CancelledError:
                pass
        if self._command_task:
            self._command_task.cancel()
            try:
                await self._command_task
            except asyncio.CancelledError:
                pass

    @collect_handler(message_handlers)
    async def handle_ping(self):
        pass

    @collect_handler(message_handlers)
    async def handle_get_counter(self):
        pass


async def main():
    queue = asyncio.Queue()
    emu = VMEmulator("test", queue)
    await emu.start()

    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())