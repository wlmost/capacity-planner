"""
Time Entry Repository
Datenzugriff für Zeiterfassungen
"""
from typing import List, Optional
from datetime import datetime
from ..models.time_entry import TimeEntry
from .base_repository import BaseRepository


class TimeEntryRepository(BaseRepository[TimeEntry]):
    """
    Repository für TimeEntry-Operationen
    
    CRUD-Operationen für Zeiterfassungen
    """
    
    def create(self, entry: TimeEntry) -> int:
        """
        Erstellt neue Zeiterfassung
        
        Args:
            entry: TimeEntry-Objekt
            
        Returns:
            ID der erstellten Zeiterfassung
        """
        query_text = """
            INSERT INTO time_entries 
            (worker_id, date, duration_minutes, description, project, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = [
            entry.worker_id,
            entry.date.isoformat(),
            entry.duration_minutes,
            entry.description,
            entry.project,
            entry.created_at.isoformat(),
            entry.updated_at.isoformat()
        ]
        
        query = self._execute_query(query_text, params)
        entry_id = query.lastInsertId()
        
        # Explizites Commit für sofortige Verfügbarkeit
        if self.db_service.db:
            self.db_service.db.commit()
        
        return entry_id
    
    def find_by_id(self, entry_id: int) -> Optional[TimeEntry]:
        """
        Findet Zeiterfassung per ID
        
        Args:
            entry_id: ID der Zeiterfassung
            
        Returns:
            TimeEntry oder None
        """
        query_text = "SELECT * FROM time_entries WHERE id = ?"
        query = self._execute_query(query_text, [entry_id])
        
        if query.next():
            return self._map_to_entity(query)
        return None
    
    def find_by_worker(
        self,
        worker_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TimeEntry]:
        """
        Findet alle Zeiterfassungen eines Workers
        
        Args:
            worker_id: Worker-ID
            start_date: Optionaler Start-Filter
            end_date: Optionaler End-Filter
            
        Returns:
            Liste von TimeEntry-Objekten
        """
        query_text = "SELECT * FROM time_entries WHERE worker_id = ?"
        params = [worker_id]
        
        if start_date:
            query_text += " AND date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query_text += " AND date <= ?"
            params.append(end_date.isoformat())
        
        query_text += " ORDER BY date DESC"
        
        query = self._execute_query(query_text, params)
        
        entries = []
        while query.next():
            entries.append(self._map_to_entity(query))
        
        return entries
    
    def find_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[TimeEntry]:
        """
        Findet alle Zeiterfassungen in einem Datumsbereich
        
        Args:
            start_date: Start-Datum (YYYY-MM-DD)
            end_date: End-Datum (YYYY-MM-DD)
            
        Returns:
            Liste von TimeEntry-Objekten
        """
        query_text = """
            SELECT * FROM time_entries 
            WHERE DATE(date) >= ? AND DATE(date) <= ?
            ORDER BY date DESC
        """
        params = [start_date, end_date]
        
        query = self._execute_query(query_text, params)
        
        entries = []
        while query.next():
            entry = self._map_to_entity(query)
            entries.append(entry)
        
        return entries
    
    def update(self, entry: TimeEntry) -> bool:
        """
        Aktualisiert Zeiterfassung
        
        Args:
            entry: TimeEntry mit aktualisiertem Daten und ID
            
        Returns:
            True bei Erfolg
        """
        query_text = """
            UPDATE time_entries
            SET worker_id = ?, date = ?, duration_minutes = ?, 
                description = ?, project = ?, updated_at = ?
            WHERE id = ?
        """
        params = [
            entry.worker_id,
            entry.date.isoformat(),
            entry.duration_minutes,
            entry.description,
            entry.project,
            datetime.now().isoformat(),
            entry.id
        ]
        
        query = self._execute_query(query_text, params)
        return query.numRowsAffected() > 0
    
    def delete(self, entry_id: int) -> bool:
        """
        Löscht Zeiterfassung
        
        Args:
            entry_id: ID der zu löschenden Zeiterfassung
            
        Returns:
            True bei Erfolg
        """
        query_text = "DELETE FROM time_entries WHERE id = ?"
        query = self._execute_query(query_text, [entry_id])
        return query.numRowsAffected() > 0
    
    def _map_to_entity(self, query) -> TimeEntry:
        """Mappt QSqlQuery-Result zu TimeEntry"""
        return TimeEntry(
            id=query.value("id"),
            worker_id=query.value("worker_id"),
            date=datetime.fromisoformat(query.value("date")),
            duration_minutes=query.value("duration_minutes"),
            description=query.value("description"),
            project=query.value("project"),
            created_at=datetime.fromisoformat(query.value("created_at")),
            updated_at=datetime.fromisoformat(query.value("updated_at"))
        )
