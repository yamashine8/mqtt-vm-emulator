from dataclasses import dataclass
from typing import Any

from src.model.log_message import LogMessage


@dataclass
class RMQMessagePayload:
    host: str
    message_payload: dict[Any, Any] | LogMessage

@dataclass
class RMQMessage:
    topic: str
    message: RMQMessagePayload

