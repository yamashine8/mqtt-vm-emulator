import random

from src.model.log_message import LogMessage
from src.utils.message_body import MESSAGE_BODY


class MessageGeneratorMixin:
    def _generate_message(self):
        num = random.randint(1, 10)
        message_header, message_text = self._get_message_body(num)
        return LogMessage(message_header, message_text)

    @staticmethod
    def _get_message_body(num):
        return MESSAGE_BODY.get(num)

    @staticmethod
    def _get_message_timeout() -> int:
        return random.randint(1, 10)
