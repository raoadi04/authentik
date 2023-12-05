"""Base event enricher"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from authentik.events.models import Event


class EventEnricher:
    """Base event enricher"""

    def enrich_event(self, event: "Event"):
        """Modify event"""
        raise NotImplementedError
