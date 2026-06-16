# runtime/event_bus.py

from __future__ import annotations

import asyncio
import inspect
import logging
import threading
import time
import uuid

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
)

logger = logging.getLogger(__name__)


# ============================================================
# EVENT PRIORITY
# ============================================================

class EventPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


# ============================================================
# EVENT MODEL
# ============================================================

@dataclass(slots=True)
class Event:

    name: str

    payload: Any = None

    source: str = "system"

    priority: EventPriority = EventPriority.NORMAL

    correlation_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    timestamp: float = field(
        default_factory=time.time
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EVENT RESULT
# ============================================================

@dataclass(slots=True)
class EventResult:

    event_name: str

    success: bool

    execution_time: float

    handler_count: int

    errors: List[str] = field(default_factory=list)


# ============================================================
# DEAD LETTER EVENT
# ============================================================

@dataclass(slots=True)
class DeadLetter:

    event: Event

    error: str

    handler: str

    timestamp: float = field(
        default_factory=time.time
    )


# ============================================================
# METRICS
# ============================================================

@dataclass
class EventMetrics:

    published: int = 0

    delivered: int = 0

    failed: int = 0

    total_execution_time: float = 0.0

    @property
    def average_execution_time(self) -> float:

        if self.delivered == 0:
            return 0.0

        return self.total_execution_time / self.delivered


# ============================================================
# EVENT BUS
# ============================================================

HandlerType = Callable[[Event], Any]
MiddlewareType = Callable[[Event], Event]


class EventBus:
    """
    Production-grade async event bus.

    Features:
        - sync + async handlers
        - middleware pipeline
        - wildcard subscriptions
        - dead letter queue
        - event history
        - metrics
        - replay support
        - thread-safe publishing
    """

    def __init__(
        self,
        history_limit: int = 1000
    ):

        self._handlers: Dict[str, Set[HandlerType]] = {}

        self._wildcard_handlers: Set[HandlerType] = set()

        self._middleware: List[MiddlewareType] = []

        self._history: List[Event] = []

        self._history_limit = history_limit

        self._dead_letters: List[DeadLetter] = []

        self._metrics = EventMetrics()

        self._lock = threading.RLock()

    # ========================================================
    # SUBSCRIPTIONS
    # ========================================================

    def subscribe(
        self,
        event_name: str,
        handler: HandlerType
    ) -> None:

        with self._lock:

            if event_name == "*":

                self._wildcard_handlers.add(handler)
                return

            self._handlers.setdefault(
                event_name,
                set()
            ).add(handler)

    def unsubscribe(
        self,
        event_name: str,
        handler: HandlerType
    ) -> None:

        with self._lock:

            if event_name == "*":

                self._wildcard_handlers.discard(handler)
                return

            if event_name in self._handlers:

                self._handlers[event_name].discard(
                    handler
                )

    # ========================================================
    # MIDDLEWARE
    # ========================================================

    def add_middleware(
        self,
        middleware: MiddlewareType
    ) -> None:

        self._middleware.append(middleware)

    # ========================================================
    # PUBLISH
    # ========================================================

    async def publish(
        self,
        event: Event
    ) -> EventResult:

        start_time = time.perf_counter()

        self._metrics.published += 1

        for middleware in self._middleware:
            event = middleware(event)

        self._store_history(event)

        handlers = self._get_handlers(event.name)

        errors: List[str] = []

        tasks = []

        for handler in handlers:

            tasks.append(
                self._execute_handler(
                    handler,
                    event,
                    errors
                )
            )

        if tasks:
            await asyncio.gather(*tasks)

        execution_time = (
            time.perf_counter() - start_time
        )

        self._metrics.delivered += len(handlers)

        self._metrics.total_execution_time += (
            execution_time
        )

        success = len(errors) == 0

        return EventResult(
            event_name=event.name,
            success=success,
            execution_time=execution_time,
            handler_count=len(handlers),
            errors=errors
        )

    # ========================================================
    # SYNC WRAPPER
    # ========================================================

    def publish_sync(
        self,
        event: Event
    ) -> EventResult:

        try:

            loop = asyncio.get_running_loop()

            future = asyncio.run_coroutine_threadsafe(
                self.publish(event),
                loop
            )

            return future.result()

        except RuntimeError:

            return asyncio.run(
                self.publish(event)
            )

    # ========================================================
    # EXECUTION
    # ========================================================

    async def _execute_handler(
        self,
        handler: HandlerType,
        event: Event,
        errors: List[str]
    ) -> None:

        try:

            if inspect.iscoroutinefunction(handler):

                await handler(event)

            else:

                await asyncio.to_thread(
                    handler,
                    event
                )

        except Exception as exc:

            self._metrics.failed += 1

            error = (
                f"{handler.__name__}: {exc}"
            )

            errors.append(error)

            self._dead_letters.append(
                DeadLetter(
                    event=event,
                    error=str(exc),
                    handler=handler.__name__
                )
            )

            logger.exception(
                "Event handler failed"
            )

    # ========================================================
    # HISTORY
    # ========================================================

    def _store_history(
        self,
        event: Event
    ) -> None:

        self._history.append(event)

        if len(self._history) > self._history_limit:

            self._history.pop(0)

    def get_history(self) -> List[Event]:

        return list(self._history)

    def replay(
        self,
        event_name: Optional[str] = None
    ) -> List[Event]:

        if event_name is None:
            return list(self._history)

        return [
            e
            for e in self._history
            if e.name == event_name
        ]

    # ========================================================
    # DEAD LETTERS
    # ========================================================

    def get_dead_letters(
        self
    ) -> List[DeadLetter]:

        return list(self._dead_letters)

    # ========================================================
    # METRICS
    # ========================================================

    def metrics(self) -> EventMetrics:

        return self._metrics

    # ========================================================
    # INTERNAL
    # ========================================================

    def _get_handlers(
        self,
        event_name: str
    ) -> List[HandlerType]:

        handlers = []

        handlers.extend(
            self._handlers.get(
                event_name,
                set()
            )
        )

        handlers.extend(
            self._wildcard_handlers
        )

        return handlers