"""
Analytics Service
Berechnung von Auslastungen und Reports
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from ..models.time_entry import TimeEntry
from ..models.capacity import Capacity
from .database_service import DatabaseService


class AnalyticsService:
    """
    Service für Auslastungsberechnungen und Analytics
    
    Funktionen:
    - Auslastungsberechnung (Ist vs. Plan)
    - Trendanalysen
    - Report-Generierung
    
    Beispiel:
        >>> analytics = AnalyticsService(db_service)
        >>> utilization = analytics.calculate_worker_utilization(1, start, end)
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialisiert AnalyticsService
        
        Args:
            db_service: DatabaseService-Instanz
        """
        self._db_service = db_service
    
    def calculate_worker_utilization(
        self,
        worker_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Berechnet Auslastung für einen Worker im Zeitraum
        
        Args:
            worker_id: ID des Workers
            start_date: Startdatum
            end_date: Enddatum
            
        Returns:
            Dict mit hours_worked, hours_planned, utilization_percent
        """
        from ..repositories.time_entry_repository import TimeEntryRepository
        from ..repositories.capacity_repository import CapacityRepository
        
        entry_repo = TimeEntryRepository(self._db_service)
        capacity_repo = CapacityRepository(self._db_service)
        
        # Lade TimeEntries für Worker
        time_entries = entry_repo.find_by_worker(worker_id, start_date, end_date)
        
        # Lade Capacities für Worker
        capacities = capacity_repo.find_by_worker(worker_id, start_date, end_date)
        
        # Summiere gearbeitete Stunden
        hours_worked = sum(entry.duration_hours() for entry in time_entries)
        
        # Summiere geplante Stunden
        hours_planned = sum(cap.planned_hours for cap in capacities)
        
        # Berechne Auslastung
        utilization_percent = (hours_worked / hours_planned * 100) if hours_planned > 0 else 0.0
        
        return {
            "hours_worked": hours_worked,
            "hours_planned": hours_planned,
            "utilization_percent": utilization_percent
        }
    
    def calculate_utilization(
        self,
        time_entries: List[TimeEntry],
        capacities: List[Capacity],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, float]:
        """
        Berechnet Auslastung für einen Zeitraum
        
        Args:
            time_entries: Erfasste Arbeitszeiten
            capacities: Geplante Kapazitäten
            start_date: Start des Zeitraums
            end_date: Ende des Zeitraums
            
        Returns:
            Dict mit Keys: actual_hours, planned_hours, utilization_percent
        """
        # Ist-Stunden summieren
        actual_hours = sum(
            entry.duration_hours()
            for entry in time_entries
            if start_date <= entry.date <= end_date
        )
        
        # Plan-Stunden summieren (nur überlappende Zeiträume)
        planned_hours = sum(
            self._get_overlapping_hours(cap, start_date, end_date)
            for cap in capacities
        )
        
        # Auslastung berechnen
        utilization_percent = (actual_hours / planned_hours * 100) if planned_hours > 0 else 0.0
        
        return {
            "actual_hours": actual_hours,
            "planned_hours": planned_hours,
            "utilization_percent": utilization_percent,
            "difference_hours": actual_hours - planned_hours
        }
    
    def _get_overlapping_hours(
        self,
        capacity: Capacity,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Berechnet überlappende Stunden zwischen Capacity und Zeitraum"""
        # Überlappende Tage finden
        overlap_start = max(capacity.start_date, start_date)
        overlap_end = min(capacity.end_date, end_date)
        
        if overlap_start > overlap_end:
            return 0.0
        
        # Anteil der Capacity berechnen
        capacity_days = capacity.days_count()
        overlap_days = (overlap_end - overlap_start).days + 1
        
        return capacity.planned_hours * (overlap_days / capacity_days)
    
    def calculate_daily_breakdown(
        self,
        time_entries: List[TimeEntry],
        start_date: datetime,
        end_date: datetime
    ) -> List[Tuple[datetime, float]]:
        """
        Erstellt tägliche Breakdown von Arbeitszeiten
        
        Returns:
            Liste von (Datum, Stunden) Tuples
        """
        daily_hours: Dict[datetime, float] = {}
        
        # Alle Tage im Zeitraum mit 0 initialisieren
        current_date = start_date
        while current_date <= end_date:
            daily_hours[current_date.date()] = 0.0
            current_date += timedelta(days=1)
        
        # Stunden summieren
        for entry in time_entries:
            entry_date = entry.date.date()
            if start_date.date() <= entry_date <= end_date.date():
                daily_hours[entry_date] = daily_hours.get(entry_date, 0.0) + entry.duration_hours()
        
        # Als sortierte Liste zurückgeben
        return sorted(daily_hours.items())
    
    def get_statistics_summary(self, time_entries: List[TimeEntry]) -> Dict[str, float]:
        """
        Erstellt Statistik-Zusammenfassung
        
        Returns:
            Dict mit total_hours, avg_hours_per_day, min_hours, max_hours
        """
        if not time_entries:
            return {
                "total_hours": 0.0,
                "avg_hours_per_day": 0.0,
                "min_hours": 0.0,
                "max_hours": 0.0,
                "entry_count": 0
            }
        
        hours = [entry.duration_hours() for entry in time_entries]
        
        return {
            "total_hours": sum(hours),
            "avg_hours_per_day": sum(hours) / len(hours),
            "min_hours": min(hours),
            "max_hours": max(hours),
            "entry_count": len(time_entries)
        }
