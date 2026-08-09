from dataclasses import dataclass


@dataclass
class LogMessage:
    message_log_level: str
    message_text: str
