from dataclasses import dataclass
from typing import Any

from src.model.log_message import LogMessage

@dataclass
class RMQMessage:
    topic: str
    host: str
    message_payload: dict[Any, Any] | LogMessage
    correlation_id: None | str = None