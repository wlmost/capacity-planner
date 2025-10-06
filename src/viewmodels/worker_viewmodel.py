"""
WorkerViewModel - MVVM Layer für Worker Management
"""
from typing import Optional, List
from PySide6.QtCore import QObject, Signal

from ..models.worker import Worker
from ..repositories.worker_repository import WorkerRepository


class WorkerViewModel(QObject):
    """
    ViewModel für Worker Management
    
    Signals:
        worker_created: Worker wurde erfolgreich erstellt (worker_id: int)
        worker_updated: Worker wurde erfolgreich aktualisiert (worker_id: int)
        worker_deleted: Worker wurde erfolgreich gelöscht (worker_id: int)
        workers_loaded: Workers wurden geladen (workers: List[Worker])
        validation_failed: Validierung fehlgeschlagen (message: str)
        error_occurred: Fehler aufgetreten (message: str)
    """
    
    worker_created = Signal(int)
    worker_updated = Signal(int)
    worker_deleted = Signal(int)
    workers_loaded = Signal(list)
    validation_failed = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, repository: WorkerRepository):
        super().__init__()
        self._repository = repository
    
    def create_worker(
        self,
        name: str,
        email: str,
        team: str = "",
        active: bool = True
    ) -> bool:
        """
        Erstellt einen neuen Worker
        
        Args:
            name: Name des Workers
            email: E-Mail-Adresse
            team: Team-Zugehörigkeit (optional)
            active: Aktiv-Status
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        # Validation
        validation_error = self._validate_worker(name, email)
        if validation_error:
            self.validation_failed.emit(validation_error)
            return False
        
        try:
            worker = Worker(
                name=name.strip(),
                email=email.strip().lower(),
                team=team.strip(),
                active=active
            )
            
            worker_id = self._repository.create(worker)
            self.worker_created.emit(worker_id)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Erstellen: {str(e)}")
            return False
    
    def update_worker(
        self,
        worker_id: int,
        name: str,
        email: str,
        team: str = "",
        active: bool = True
    ) -> bool:
        """
        Aktualisiert einen existierenden Worker
        
        Args:
            worker_id: ID des Workers
            name: Neuer Name
            email: Neue E-Mail
            team: Neues Team
            active: Neuer Aktiv-Status
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        # Validation
        validation_error = self._validate_worker(name, email)
        if validation_error:
            self.validation_failed.emit(validation_error)
            return False
        
        try:
            worker = Worker(
                id=worker_id,
                name=name.strip(),
                email=email.strip().lower(),
                team=team.strip(),
                active=active
            )
            
            success = self._repository.update(worker)
            if success:
                self.worker_updated.emit(worker_id)
                return True
            else:
                self.error_occurred.emit("Worker konnte nicht aktualisiert werden")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Aktualisieren: {str(e)}")
            return False
    
    def delete_worker(self, worker_id: int) -> bool:
        """
        Löscht einen Worker
        
        Args:
            worker_id: ID des Workers
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            success = self._repository.delete(worker_id)
            if success:
                self.worker_deleted.emit(worker_id)
                return True
            else:
                self.error_occurred.emit("Worker konnte nicht gelöscht werden")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Löschen: {str(e)}")
            return False
    
    def load_workers(self, include_inactive: bool = False) -> List[Worker]:
        """
        Lädt alle Workers
        
        Args:
            include_inactive: Ob inaktive Workers inkludiert werden sollen
            
        Returns:
            Liste aller Workers
        """
        try:
            workers = self._repository.find_all()
            
            if not include_inactive:
                workers = [w for w in workers if w.active]
            
            self.workers_loaded.emit(workers)
            return workers
            
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Laden: {str(e)}")
            return []
    
    def find_worker(self, worker_id: int) -> Optional[Worker]:
        """
        Sucht einen spezifischen Worker
        
        Args:
            worker_id: ID des Workers
            
        Returns:
            Worker oder None
        """
        try:
            return self._repository.find_by_id(worker_id)
        except Exception as e:
            self.error_occurred.emit(f"Fehler beim Suchen: {str(e)}")
            return None
    
    def _validate_worker(self, name: str, email: str) -> Optional[str]:
        """
        Validiert Worker-Daten
        
        Args:
            name: Name des Workers
            email: E-Mail-Adresse
            
        Returns:
            Fehlermeldung oder None wenn valide
        """
        name = name.strip()
        email = email.strip()
        
        if not name:
            return "Name darf nicht leer sein"
        
        if len(name) < 2:
            return "Name muss mindestens 2 Zeichen haben"
        
        if not email:
            return "E-Mail darf nicht leer sein"
        
        # Simple email validation
        if "@" not in email or "." not in email.split("@")[-1]:
            return "Ungültige E-Mail-Adresse"
        
        return None
