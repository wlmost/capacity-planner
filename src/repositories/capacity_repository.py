"""
Capacity Repository
Datenzugriff für Kapazitätsplanung
"""
from typing import List, Optional
from datetime import datetime
from ..models.capacity import Capacity
from .base_repository import BaseRepository


class CapacityRepository(BaseRepository[Capacity]):
    """
    Repository für Capacity-Operationen
    
    CRUD-Operationen für Kapazitätsplanung
    """
    
    def create(self, capacity: Capacity) -> int:
        """
        Erstellt neue Kapazitätsplanung
        
        Args:
            capacity: Capacity-Objekt
            
        Returns:
            ID der erstellten Capacity
        """
        query_text = """
            INSERT INTO capacities 
            (worker_id, start_date, end_date, planned_hours, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = [
            capacity.worker_id,
            capacity.start_date.isoformat(),
            capacity.end_date.isoformat(),
            capacity.planned_hours,
            capacity.notes,
            capacity.created_at.isoformat()
        ]
        
        query = self._execute_query(query_text, params)
        return query.lastInsertId()
    
    def find_by_id(self, capacity_id: int) -> Optional[Capacity]:
        """
        Findet Capacity per ID
        
        Args:
            capacity_id: ID der Capacity
            
        Returns:
            Capacity oder None
        """
        query_text = "SELECT * FROM capacities WHERE id = ?"
        query = self._execute_query(query_text, [capacity_id])
        
        if query.next():
            return self._map_to_entity(query)
        return None
    
    def find_by_worker(
        self,
        worker_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Capacity]:
        """
        Findet alle Capacities eines Workers
        
        Args:
            worker_id: Worker-ID
            start_date: Optionaler Start-Filter
            end_date: Optionaler End-Filter
            
        Returns:
            Liste von Capacity-Objekten
        """
        query_text = "SELECT * FROM capacities WHERE worker_id = ?"
        params = [worker_id]
        
        if start_date:
            query_text += " AND end_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query_text += " AND start_date <= ?"
            params.append(end_date.isoformat())
        
        query_text += " ORDER BY start_date DESC"
        
        query = self._execute_query(query_text, params)
        
        capacities = []
        while query.next():
            capacities.append(self._map_to_entity(query))
        
        return capacities
    
    def find_by_date_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Capacity]:
        """
        Findet alle Capacities in einem Datumsbereich
        
        Args:
            start_date: Optionaler Start-Filter
            end_date: Optionaler End-Filter
            
        Returns:
            Liste von Capacity-Objekten
        """
        query_text = "SELECT * FROM capacities WHERE 1=1"
        params = []
        
        if start_date:
            query_text += " AND end_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query_text += " AND start_date <= ?"
            params.append(end_date.isoformat())
        
        query_text += " ORDER BY start_date DESC"
        
        query = self._execute_query(query_text, params)
        
        capacities = []
        while query.next():
            capacities.append(self._map_to_entity(query))
        
        return capacities
    
    def update(self, capacity: Capacity) -> bool:
        """
        Aktualisiert Capacity
        
        Args:
            capacity: Capacity mit aktualisierten Daten und ID
            
        Returns:
            True bei Erfolg
        """
        query_text = """
            UPDATE capacities
            SET worker_id = ?, start_date = ?, end_date = ?, 
                planned_hours = ?, notes = ?
            WHERE id = ?
        """
        params = [
            capacity.worker_id,
            capacity.start_date.isoformat(),
            capacity.end_date.isoformat(),
            capacity.planned_hours,
            capacity.notes,
            capacity.id
        ]
        
        query = self._execute_query(query_text, params)
        return query.numRowsAffected() > 0
    
    def delete(self, capacity_id: int) -> bool:
        """
        Löscht Capacity
        
        Args:
            capacity_id: ID der zu löschenden Capacity
            
        Returns:
            True bei Erfolg
        """
        query_text = "DELETE FROM capacities WHERE id = ?"
        query = self._execute_query(query_text, [capacity_id])
        return query.numRowsAffected() > 0
    
    def _map_to_entity(self, query) -> Capacity:
        """Mappt QSqlQuery-Result zu Capacity"""
        return Capacity(
            id=query.value("id"),
            worker_id=query.value("worker_id"),
            start_date=datetime.fromisoformat(query.value("start_date")),
            end_date=datetime.fromisoformat(query.value("end_date")),
            planned_hours=query.value("planned_hours"),
            notes=query.value("notes"),
            created_at=datetime.fromisoformat(query.value("created_at"))
        )
