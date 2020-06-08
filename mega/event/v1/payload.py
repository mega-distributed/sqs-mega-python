from datetime import datetime
from typing import Optional

from mega.event.v1 import PROTOCOL_NAME, PROTOCOL_VERSION


class MegaEvent:
    DEFAULT_VERSION = 1

    def __init__(
            self,
            name: str = None,
            timestamp: Optional[datetime] = None,
            version: int = DEFAULT_VERSION,
            domain: str = None,
            subject: str = None,
            publisher: str = None,
            attributes: dict = None,
            **kwargs
    ):
        if not name:
            raise AttributeError('Mega event attribute "name" has not been set, or set to an empty value')

        self.name = name
        self.timestamp = timestamp if timestamp else datetime.utcnow()
        self.version = version if version else self.DEFAULT_VERSION
        self.domain = domain
        self.subject = subject
        self.publisher = publisher

        self.attributes = {}
        self.attributes.update(attributes or {})
        self.attributes.update(kwargs or {})

    def __eq__(self, other):
        if not isinstance(other, MegaEvent):
            return NotImplemented

        return (
                self.name == other.name and
                self.timestamp == other.timestamp and
                self.version == other.version and
                self.domain == other.domain and
                self.subject == other.subject and
                self.publisher == other.publisher and
                self.attributes == other.attributes
        )


class MegaObject:
    DEFAULT_VERSION = 1

    def __init__(
            self,
            current: dict = None,
            type: str = None,
            id: str = None,
            version: int = DEFAULT_VERSION,
            previous: dict = None
    ):
        if not current:
            raise AttributeError('Mega object attribute "current" has not been set, or set to an empty value')

        self.current = dict(current)
        self.type = type
        self.id = id
        self.version = version if version else self.DEFAULT_VERSION
        self.previous = dict(previous) if previous else None

    def __eq__(self, other):
        if not isinstance(other, MegaObject):
            return NotImplemented

        return (
                self.current == other.current and
                self.type == other.type and
                self.id == other.id and
                self.version == other.version and
                self.previous == other.previous
        )


class MegaPayload:
    protocol = PROTOCOL_NAME
    version = PROTOCOL_VERSION

    def __init__(
            self,
            event: MegaEvent = None,
            object: Optional[MegaObject] = None,
            extra: dict = None,
            **kwargs
    ):
        if not event:
            raise AttributeError('Mega payload event has not been set')

        self.event = event
        self.object = object

        self.extra = {}
        self.extra.update(extra or {})
        self.extra.update(kwargs or {})

    def __eq__(self, other):
        if not isinstance(other, MegaPayload):
            return NotImplemented

        return (
                self.event == other.event and
                self.object == other.object and
                self.extra == other.extra
        )
