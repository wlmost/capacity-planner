"""
CapacityViewModel - MVVM Layer für Kapazitätsplanung
"""
from typing import Optional, List
from datetime import datetime
from PySide6.QtCore import QObject, Signal

from ..models.capacity import Capacity
from ..models.worker import Worker
from ..repositories.capacity_repository import CapacityRepository
from ..repositories.worker_repository import WorkerRepository
from ..services.analytics_service import AnalyticsService


class CapacityViewModel(QObject):
    """
    ViewModel für Kapazitätsplanung
    
    Signals:
        capacity_created: Kapazität wurde erstellt (capacity_id: int)
        capacity_updated: Kapazität wurde aktualisiert (capacity_id: int)
        capacity_deleted: Kapazität wurde gelöscht (capacity_id: int)
        capacities_loaded: Kapazitäten wurden geladen (capacities: List[Capacity])
        utilization_calculated: Auslastung berechnet (worker_id: int, utilization: float, hours_worked: float, hours_planned: float)
        validation_failed: Validierung fehlgeschlagen (message: str)
        error_occurred: Fehler aufgetreten (message: str)
    """
    
    capacity_created = Signal(int)
    capacity_updated = Signal(int)
    capacity_deleted = Signal(int)
    capacities_loaded = Signal(list)
    utilization_calculated = Signal(int, float, float, float)  # worker_id, utilization%, hours_worked, hours_planned
    validation_failed = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(
        self,
        capacity_repository: CapacityRepository,
        worker_repository: WorkerRepository,
        analytics_service: AnalyticsService
    ):
        super().__init__()
        self._capacity_repository = capacity_repository
        self._worker_repository = worker_repository
        self._analytics_service = analytics_service
    
    def create_capacity(
        self,
        worker_id: int,
        start_date: datetime,
        end_date: datetime,
        planned_hours: float,
        notes: str = ""
    ) -> bool:
        """
        Erstellt eine neue Kapazität
        
        Args:
            worker_id: ID des Workers
            start_date: Startdatum des Zeitraums
            end_date: Enddatum des Zeitraums
            planned_hours: Geplante Stunden
            notes: Optionale Notizen
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        # Validation
        validation_error = self._validate_capacity(
            worker_id, start_date, end_date, planned_hours
        )
        if validation_error:
            self.validation_failed.emit(validation_error)
            return False
        
        try:
            capacity = Capacity(
                worker_id=worker_id,
                start_date=start_date,
                end_date=end_date,
                planned_hours=planned_hours,
                notes=notes.strip()
            )
            
            capacity_id = self._capacity_repository.create(capacity)
            self.capacity_created.emit(capacity_id)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Erstellen: {str(e)}")
            return False
    
    def update_capacity(
        self,
        capacity_id: int,
        worker_id: int,
        start_date: datetime,
        end_date: datetime,
        planned_hours: float,
        notes: str = ""
    ) -> bool:
        """
        Aktualisiert eine existierende Kapazität
        
        Args:
            capacity_id: ID der Kapazität
            worker_id: ID des Workers
            start_date: Neues Startdatum
            end_date: Neues Enddatum
            planned_hours: Neue geplante Stunden
            notes: Neue Notizen
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        # Validation
        validation_error = self._validate_capacity(
            worker_id, start_date, end_date, planned_hours
        )
        if validation_error:
            self.validation_failed.emit(validation_error)
            return False
        
        try:
            capacity = Capacity(
                id=capacity_id,
                worker_id=worker_id,
                start_date=start_date,
                end_date=end_date,
                planned_hours=planned_hours,
                notes=notes.strip()
            )
            
            success = self._capacity_repository.update(capacity)
            if success:
                self.capacity_updated.emit(capacity_id)
                return True
            else:
                self.error_occurred.emit("Kapazität konnte nicht aktualisiert werden")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Aktualisieren: {str(e)}")
            return False
    
    def delete_capacity(self, capacity_id: int) -> bool:
        """
        Löscht eine Kapazität
        
        Args:
            capacity_id: ID der Kapazität
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            success = self._capacity_repository.delete(capacity_id)
            if success:
                self.capacity_deleted.emit(capacity_id)
                return True
            else:
                self.error_occurred.emit("Kapazität konnte nicht gelöscht werden")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Löschen: {str(e)}")
            return False
    
    def load_capacities_for_worker(
        self,
        worker_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Capacity]:
        """
        Lädt Kapazitäten für einen Worker
        
        Args:
            worker_id: ID des Workers
            start_date: Optionales Startdatum für Filter
            end_date: Optionales Enddatum für Filter
            
        Returns:
            Liste der Kapazitäten
        """
        try:
            capacities = self._capacity_repository.find_by_worker(
                worker_id, start_date, end_date
            )
            self.capacities_loaded.emit(capacities)
            return capacities
            
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Laden: {str(e)}")
            return []
    
    def load_all_capacities(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Capacity]:
        """
        Lädt alle Kapazitäten
        
        Args:
            start_date: Optionales Startdatum für Filter
            end_date: Optionales Enddatum für Filter
            
        Returns:
            Liste aller Kapazitäten
        """
        try:
            capacities = self._capacity_repository.find_by_date_range(
                start_date, end_date
            )
            self.capacities_loaded.emit(capacities)
            return capacities
            
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Laden: {str(e)}")
            return []
    
    def calculate_utilization(
        self,
        worker_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[dict]:
        """
        Berechnet die Auslastung für einen Worker im Zeitraum
        
        Args:
            worker_id: ID des Workers
            start_date: Startdatum
            end_date: Enddatum
            
        Returns:
            Dict mit utilization_percent, hours_worked, hours_planned
            oder None bei Fehler
        """
        try:
            utilization = self._analytics_service.calculate_worker_utilization(
                worker_id, start_date, end_date
            )
            
            if utilization is not None:
                self.utilization_calculated.emit(
                    worker_id,
                    utilization['utilization_percent'],
                    utilization['hours_worked'],
                    utilization['hours_planned']
                )
            
            return utilization
            
        except Exception as e:
            self.error_occurred.emit(f"Fehler bei Auslastungsberechnung: {str(e)}")
            return None
    
    def get_active_workers(self) -> List[Worker]:
        """
        Holt aktive Workers für Dropdown
        
        Returns:
            Liste aktiver Workers
        """
        try:
            workers = self._worker_repository.find_all()
            return [w for w in workers if w.active]
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Laden der Workers: {str(e)}")
            return []
    
    def _validate_capacity(
        self,
        worker_id: int,
        start_date: datetime,
        end_date: datetime,
        planned_hours: float
    ) -> Optional[str]:
        """
        Validiert Kapazitäts-Daten
        
        Args:
            worker_id: ID des Workers
            start_date: Startdatum
            end_date: Enddatum
            planned_hours: Geplante Stunden
            
        Returns:
            Fehlermeldung oder None wenn valide
        """
        if worker_id <= 0:
            return "Ungültige Worker-ID"
        
        if start_date >= end_date:
            return "Enddatum muss nach Startdatum liegen"
        
        if planned_hours <= 0:
            return "Geplante Stunden müssen positiv sein"
        
        if planned_hours > 1000:
            return "Geplante Stunden erscheinen unrealistisch hoch (max. 1000h)"
        
        # Check if worker exists
        worker = self._worker_repository.find_by_id(worker_id)
        if worker is None:
            return f"Worker mit ID {worker_id} existiert nicht"
        
        if not worker.active:
            return f"Worker '{worker.name}' ist inaktiv"
        
        return None
