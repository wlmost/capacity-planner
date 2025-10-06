"""
TimeEntry Model
Repräsentiert eine einzelne Arbeitszeiterfassung
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TimeEntry:
    """
    Arbeitszeit-Eintrag für einen Knowledge Worker
    
    Attributes:
        id: Eindeutige ID (aus Datenbank)
        worker_id: Referenz zum Worker
        date: Datum der Erfassung
        duration_minutes: Dauer in Minuten
        description: Beschreibung der Tätigkeit
        project: Optional: Projektzuordnung
        created_at: Zeitstempel der Erstellung
        updated_at: Zeitstempel der letzten Änderung
    """
    worker_id: int
    date: datetime
    duration_minutes: int
    description: str
    id: Optional[int] = None
    project: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def duration_hours(self) -> float:
        """Gibt die Dauer in Stunden zurück"""
        return self.duration_minutes / 60.0
    
    def __str__(self) -> str:
        return f"TimeEntry({self.date.date()}, {self.duration_hours():.2f}h, {self.description})"
