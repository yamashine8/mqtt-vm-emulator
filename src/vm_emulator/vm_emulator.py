import asyncio
import json
from dataclasses import asdict

import aio_pika

from src.mixins.hardware_config_mixin import HardwareConfigMixin
from src.mixins.message_generator_mixin import MessageGeneratorMixin
from src.model.rmq_message_type import RMQMessage
from src.utils.vm_emulator_utils import collect_handler, MessageHandlers

import logging

logger = logging.getLogger(__name__)

class VMEmulator(MessageGeneratorMixin, HardwareConfigMixin):
    message_handlers: MessageHandlers = {}
    MESSAGE_TYPE_STATUS = "status"

    def __init__(self, identity: str, amqp_url):
        self.identity: str = identity
        self._life_cycle_task: asyncio.Task = None
        self.log_counter = 0

        self.command_router = self.message_handlers

        self.hardware_config = self.get_config()
        self._amqp_url = amqp_url
        self.amqp_connection = None
        self.amqp_exchange = None
        self.amqp_queue = None
        self.amqp_channel = None


    def __str__(self):
        return f"VM Emulator {self.identity}, logs sent: {self.log_counter}"

    async def start(self):
        await self.connect_to_channel()
        self._life_cycle_task = asyncio.create_task(self._life_cycle())


    async def connect_to_channel(self):
        self.amqp_connection = await aio_pika.connect_robust(self._amqp_url)
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
            topic = message.routing_key.split(".")[-1].lower()
            handler = self.command_router.get(topic)
            correlation_id = message.correlation_id

            if handler is None:
                raise NotImplementedError(f"{topic} Not Implemented")

            await handler(self, correlation_id, message.body.decode())

    async def send_message(self, message: RMQMessage):
        if self.amqp_exchange is None:
            raise RuntimeError("Publisher is not connected")

        payload = aio_pika.Message(
            body=json.dumps(message.message_payload, default=str).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            correlation_id=message.correlation_id,
        )

        await self.amqp_exchange.publish(
            payload,
            routing_key=message.topic,
        )

    async def _life_cycle(self):
        while True:
            try:
                message_body = self._generate_message()
                payload = RMQMessage(
                    self.MESSAGE_TYPE_STATUS,
                    self.identity,
                    asdict(message_body)
                )
                self.log_counter += 1

                await self.send_message(payload)

            except Exception as e:
                logger.error(f"{type(e).__name__}: {e}")
                logger.exception("Lifecycle error")

            await asyncio.sleep(self._get_message_timeout())

    async def stop(self):
        if self._life_cycle_task:
            self._life_cycle_task.cancel()
            try:
                await self._life_cycle_task
            except asyncio.CancelledError:
                pass


    @collect_handler(message_handlers)
    async def handle_get_hardware_config(self, correlation_id, *args):
        payload = RMQMessage(
            "HardwareConfig",
            self.identity,
            self.hardware_config,
            correlation_id,
        )

        return await self.send_message(payload)

    @collect_handler(message_handlers)
    async def handle_get_log_counter(self, correlation_id, *args):
        payload = RMQMessage(
            "LogCounter",
            self.identity,
            self.log_counter,
            correlation_id,
        )

        return await self.send_message(payload)


async def main():
    emu = VMEmulator("test", 'amqp://guest:guest@localhost/')
    await emu.start()

    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())