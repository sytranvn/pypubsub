from enum import Enum
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pypubsub.pubsub import PubSub

class EventListener:
    _context: Optional["PubSub" ]

    def __init__(self):
        self._context = None

    def __call__(self, arg: Any):
        raise NotImplementedError()

    def set_event_info(self, context: "PubSub | None"):
        self._context = context

    def call(self, arg: Any):
        self(arg)

