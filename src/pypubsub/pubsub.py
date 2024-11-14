from enum import Enum
import random
import logging
from typing import Any, Dict, List
from weakref import WeakSet
class_logger = None
from pypubsub.event_listener import EventListener


class Events(Dict[Enum, WeakSet[EventListener]]):
    pass


class PubSub:
    ADD_LISTENER_GC_PROBABILITY = 0.005

    @property
    def logger(cls) -> logging.Logger:
        global class_logger
        if class_logger is None:
            class_logger = logging.getLogger(__name__)
        return class_logger

    def __init__(self):
        self._events = Events()

    def add_listener(self, event_tag: Enum, listener: EventListener):
        listeners = self._events.get(event_tag)
        if listeners == None:
            listeners = WeakSet()
            self._events[event_tag] = listeners
        listeners.add(listener)
        if random.random() < PubSub.ADD_LISTENER_GC_PROBABILITY:
            self._remove_dead_listeners()

    def remove_listener(self, event_tag: Enum, listener: EventListener):
        listeners = self._events.get(event_tag)
        if listeners is None:
            return
        exists = next((True for ltn in listeners if ltn == listener), False)
        if exists:
            listeners.remove(listener)
        self._remove_dead_listeners()

    def get_listeners(self, event_tag: Enum) -> List[EventListener]:
        self._remove_dead_listeners()
        listeners = list(self._events.get(event_tag, []))
        return listeners

    def trigger_event(self, event_tag: Enum, message: Any):
        self._remove_dead_listeners()
        listeners = self._events.get(event_tag)
        if listeners is None:
            return

        # It is extremely important that this set of listeners is a copy - because listeners are allowed to call
        # remove_listener(), which breaks the iterator if we're using the underlying set.
        listeners = list(listeners)
        for listener in listeners:
            try:
                listener.set_event_info(self)
                listener.call(message)
            except Exception:
                self.log_exception(event_tag, message)
            finally:
                listener.set_event_info(None)

    def log_exception(self, event_tag: Enum, arg: Any):
        self.logger.error(f"Unexpected error while processing event {event_tag}.", exc_info=True)
    
    def _remove_dead_listeners(self):
        to_remove = []
        for tag, listeners in self._events.items():
            if len(listeners) == 0:
                to_remove.append(tag)
        for tag in to_remove:
            del self._events[tag]
