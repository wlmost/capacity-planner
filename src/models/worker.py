"""
Worker Model
Repräsentiert einen Knowledge Worker
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Worker:
    """
    Knowledge Worker Profil
    
    Attributes:
        id: Eindeutige ID
        name: Name des Workers (verschlüsselt gespeichert)
        email: E-Mail (verschlüsselt gespeichert)
        team: Team-Zuordnung
        active: Aktiv/Inaktiv Status
        created_at: Zeitstempel der Erstellung
    """
    name: str
    email: str
    team: str
    id: Optional[int] = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        status = "aktiv" if self.active else "inaktiv"
        return f"Worker({self.name}, {self.team}, {status})"
