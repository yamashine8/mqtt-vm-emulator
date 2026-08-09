from collections.abc import Awaitable, Callable

MessageHandler = Callable[["MessageService", str, bytes], Awaitable[None]]
MessageHandlers = dict[str, MessageHandler]

def collect_handler(registry: MessageHandlers) -> Callable[[MessageHandler], MessageHandler]:
    def decorator(func: MessageHandler) -> MessageHandler:
        handler_name = func.__name__.removeprefix("handle_").replace("_", "").lower()
        registry[handler_name] = func
        return func

    return decorator
