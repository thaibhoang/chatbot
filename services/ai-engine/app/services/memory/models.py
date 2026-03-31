from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatMessage:
    role: str
    content: str
    ts: datetime


@dataclass
class CustomerMemoryJob:
    id: str
    project_id: str
    customer_id: str
    transcript: list[dict[str, str]]
    source_window_id: str
