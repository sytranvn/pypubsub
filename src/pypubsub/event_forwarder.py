from typing import Callable, Any

from pypubsub.pubsub import PubSub, EventListener


class EventForwarder(EventListener):
    def __init__(self, to_function: Callable[[Any], None]):
        super().__init__()
        self._to_function: Callable[[Any], None] = to_function

    def __call__(self, arg: Any):
        self._to_function(arg)


class SourceInfoEventForwarder(EventListener):
    def __init__(self, to_function: Callable[[PubSub | None, Any], None]):
        super().__init__()
        self._to_function: Callable[[PubSub | None, Any], None] = to_function

    def __call__(self, arg: Any):
        self._to_function(self._context, arg)
