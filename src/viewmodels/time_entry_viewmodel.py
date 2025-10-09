"""
TimeEntryViewModel - MVVM Layer für Zeiterfassung
"""
from PySide6.QtCore import QObject, Signal
from datetime import datetime
from typing import List, Optional

from ..services.time_parser_service import TimeParserService
from ..repositories.time_entry_repository import TimeEntryRepository
from ..models.time_entry import TimeEntry


class TimeEntryViewModel(QObject):
    """
    ViewModel für Zeiterfassung
    
    Verantwortlichkeiten:
    - Validierung von Benutzereingaben
    - Parsing von Zeit-Strings
    - Orchestrierung von TimeEntryRepository
    - Signal-basierte Kommunikation mit View
    
    Signals:
        entry_created: Emittiert nach erfolgreicher Erstellung (mit Entry-ID)
        validation_failed: Emittiert bei Validierungsfehlern (mit Fehler-Liste)
        error_occurred: Emittiert bei technischen Fehlern (mit Fehlermeldung)
    
    Beispiel:
        >>> viewmodel = TimeEntryViewModel(parser, repository)
        >>> viewmodel.entry_created.connect(on_success)
        >>> viewmodel.create_entry(1, "2025-10-06", "1:30", "Meeting")
    """
    
    # Signals
    entry_created = Signal(int)  # Emittiert Entry-ID
    entry_updated = Signal(int)  # Emittiert Entry-ID
    validation_failed = Signal(list)  # Emittiert Fehler-Liste
    error_occurred = Signal(str)  # Emittiert Fehlermeldung
    
    def __init__(
        self,
        time_parser: TimeParserService,
        repository: TimeEntryRepository
    ):
        """
        Initialisiert TimeEntryViewModel
        
        Args:
            time_parser: Service für Zeit-Parsing
            repository: Repository für Datenzugriff
        """
        super().__init__()
        self.time_parser = time_parser
        self.repository = repository
    
    def create_entry(
        self,
        worker_id: int,
        date_str: str,
        time_str: str,
        description: str,
        project: Optional[str] = None
    ) -> bool:
        """
        Erstellt neue Zeiterfassung
        
        Args:
            worker_id: ID des Workers
            date_str: Datum im Format YYYY-MM-DD
            time_str: Zeit in beliebigem Format (1:30, 90m, etc.)
            description: Beschreibung der Tätigkeit
            project: Optional: Projekt-Zuordnung
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        # Validierung
        errors = self.validate_input(worker_id, date_str, time_str, description)
        if errors:
            self.validation_failed.emit(errors)
            return False
        
        try:
            # Zeit parsen
            duration_minutes = self.time_parser.parse(time_str)
            
            # Datum parsen
            date = datetime.fromisoformat(date_str)
            
            # TimeEntry erstellen
            entry = TimeEntry(
                worker_id=worker_id,
                date=date,
                duration_minutes=duration_minutes,
                description=description.strip(),
                project=project.strip() if project else None
            )
            
            # In Datenbank speichern
            entry_id = self.repository.create(entry)
            
            # Signal emittieren
            self.entry_created.emit(entry_id)
            
            return True
            
        except Exception as e:
            error_msg = f"Fehler beim Erstellen der Zeiterfassung: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
    
    def validate_input(
        self,
        worker_id: int,
        date_str: str,
        time_str: str,
        description: str
    ) -> List[str]:
        """
        Validiert Benutzereingaben
        
        Args:
            worker_id: ID des Workers
            date_str: Datum-String
            time_str: Zeit-String
            description: Beschreibung
            
        Returns:
            Liste von Fehlermeldungen (leer bei gültiger Eingabe)
        """
        errors = []
        
        # Worker-ID validieren
        if not worker_id or worker_id <= 0:
            errors.append("Bitte wählen Sie einen Worker aus.")
        
        # Datum validieren
        try:
            datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            errors.append("Ungültiges Datum-Format. Erwartet: YYYY-MM-DD")
        
        # Zeit validieren
        if not self.parse_time_input(time_str):
            errors.append("Ungültige Zeit-Eingabe. Erlaubt: 1:30, 90m, 1.5h, etc.")
        
        # Beschreibung validieren
        if not description or not description.strip():
            errors.append("Beschreibung darf nicht leer sein.")
        
        return errors
    
    def parse_time_input(self, time_str: str) -> Optional[int]:
        """
        Parst Zeit-Eingabe und gibt Minuten zurück
        
        Args:
            time_str: Zeit in beliebigem Format
            
        Returns:
            Minuten als Integer oder None bei Fehler
        """
        try:
            return self.time_parser.parse(time_str)
        except ValueError:
            return None
    
    def format_duration(self, minutes: int, format_type: str = "colon") -> str:
        """
        Formatiert Dauer als String
        
        Args:
            minutes: Dauer in Minuten
            format_type: "colon" (1:30) oder "decimal" (1.5h)
            
        Returns:
            Formatierter String
        """
        return self.time_parser.format_minutes(minutes, format_type)
    
    def update_entry(
        self,
        entry_id: int,
        worker_id: int,
        date_str: str,
        time_str: str,
        description: str,
        project: Optional[str] = None
    ) -> bool:
        """
        Aktualisiert bestehende Zeiterfassung
        
        Args:
            entry_id: ID des zu aktualisierenden Eintrags
            worker_id: ID des Workers
            date_str: Datum im Format YYYY-MM-DD
            time_str: Zeit in beliebigem Format (1:30, 90m, etc.)
            description: Beschreibung der Tätigkeit
            project: Optional: Projekt-Zuordnung
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        # Validierung
        errors = self.validate_input(worker_id, date_str, time_str, description)
        if errors:
            self.validation_failed.emit(errors)
            return False
        
        try:
            # Zeit parsen
            duration_minutes = self.time_parser.parse(time_str)
            
            # Datum parsen
            date = datetime.fromisoformat(date_str)
            
            # TimeEntry erstellen
            entry = TimeEntry(
                id=entry_id,
                worker_id=worker_id,
                date=date,
                duration_minutes=duration_minutes,
                description=description.strip(),
                project=project.strip() if project else None
            )
            
            # In Datenbank aktualisieren
            success = self.repository.update(entry)
            
            if success:
                # Signal emittieren
                self.entry_updated.emit(entry_id)
                return True
            else:
                error_msg = "Eintrag konnte nicht aktualisiert werden"
                self.error_occurred.emit(error_msg)
                return False
            
        except Exception as e:
            error_msg = f"Fehler beim Aktualisieren der Zeiterfassung: {str(e)}"
            self.error_occurred.emit(error_msg)
            return False
