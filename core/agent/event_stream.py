"""
Event Stream Module

Manages the chronological capture and storage of human interactions.
"""

import time
import uuid
from typing import List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Event:
    """
    A captured instance of human interaction.
    
    Attributes:
        event_id: Unique identifier for the event
        timestamp: When the event occurred
        source: Origin of the input (agent, handler, etc.)
        modality: Type of input (text, voice, document, etc.)
        raw_content: The actual content of the interaction
        confidence: Processing confidence score
        metadata: Additional contextual information
    """
    event_id: str
    timestamp: float
    source: str
    modality: str
    raw_content: Any
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


class EventStream:
    """
    A chronological stream of captured events.
    
    The event stream maintains temporal ordering and provides
    methods for adding, querying, and managing events.
    """
    
    def __init__(self):
        self._events: List[Event] = []
        self._index: dict = {}  # For fast lookups by ID
    
    def add_event(self, event: Event) -> None:
        """
        Add an event to the stream.
        
        Args:
            event: The event to add
        """
        self._events.append(event)
        self._index[event.event_id] = event
    
    def get_events(self, 
                   start_time: Optional[float] = None,
                   end_time: Optional[float] = None,
                   source: Optional[str] = None,
                   modality: Optional[str] = None,
                   limit: Optional[int] = None) -> List[Event]:
        """
        Query events with optional filters.
        
        Args:
            start_time: Only return events after this time
            end_time: Only return events before this time
            source: Only return events from this source
            modality: Only return events of this modality
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        results = []
        
        for event in reversed(self._events):  # Most recent first
            # Apply filters
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            if source and event.source != source:
                continue
            if modality and event.modality != modality:
                continue
            
            results.append(event)
            
            if limit and len(results) >= limit:
                break
        
        return results
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: The event identifier
            
        Returns:
            The event if found, None otherwise
        """
        return self._index.get(event_id)
    
    def count(self) -> int:
        """Return the total number of events in the stream."""
        return len(self._events)
    
    def clear(self) -> None:
        """Remove all events from the stream."""
        self._events.clear()
        self._index.clear()
    
    def export(self) -> List[dict]:
        """
        Export all events as dictionaries.
        
        Returns:
            List of event dictionaries
        """
        return [e.__dict__ for e in self._events]
    
    def import_events(self, events: List[dict]) -> None:
        """
        Import events from dictionaries.
        
        Args:
            events: List of event dictionaries
        """
        for event_dict in events:
            event = Event(**event_dict)
            self.add_event(event)
