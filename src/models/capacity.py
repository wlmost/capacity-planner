"""
Capacity Model
Repräsentiert geplante Kapazitäten für einen Zeitraum
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Capacity:
    """
    Geplante Kapazität für einen Worker in einem Zeitraum
    
    Attributes:
        id: Eindeutige ID
        worker_id: Referenz zum Worker
        start_date: Beginn des Zeitraums
        end_date: Ende des Zeitraums
        planned_hours: Geplante verfügbare Stunden
        notes: Optionale Notizen
        created_at: Zeitstempel der Erstellung
    """
    worker_id: int
    start_date: datetime
    end_date: datetime
    planned_hours: float
    id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def days_count(self) -> int:
        """Anzahl der Tage im Zeitraum"""
        return (self.end_date - self.start_date).days + 1
    
    def hours_per_day(self) -> float:
        """Durchschnittliche Stunden pro Tag"""
        days = self.days_count()
        return self.planned_hours / days if days > 0 else 0.0
    
    def __str__(self) -> str:
        return f"Capacity({self.start_date.date()} - {self.end_date.date()}, {self.planned_hours}h)"
