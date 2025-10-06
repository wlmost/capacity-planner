"""
Worker Repository
Datenzugriff für Worker-Verwaltung mit Verschlüsselung
"""
from typing import List, Optional
from datetime import datetime
from ..models.worker import Worker
from .base_repository import BaseRepository
from ..services.crypto_service import CryptoService


class WorkerRepository(BaseRepository[Worker]):
    """
    Repository für Worker-Operationen
    
    Besonderheit: Name und Email werden verschlüsselt gespeichert
    für Datenschutz-Compliance
    
    CRUD-Operationen für Worker-Verwaltung
    """
    
    def __init__(self, db_service, crypto_service: CryptoService):
        """
        Initialisiert WorkerRepository
        
        Args:
            db_service: DatabaseService-Instanz
            crypto_service: CryptoService für Verschlüsselung
        """
        super().__init__(db_service)
        self.crypto_service = crypto_service
    
    def create(self, worker: Worker) -> int:
        """
        Erstellt neuen Worker (mit Verschlüsselung)
        
        Args:
            worker: Worker-Objekt
            
        Returns:
            ID des erstellten Workers
        """
        # Sensible Daten verschlüsseln
        encrypted_name = self.crypto_service.encrypt(worker.name)
        encrypted_email = self.crypto_service.encrypt(worker.email)
        
        query_text = """
            INSERT INTO workers 
            (name, email, team, active, created_at)
            VALUES (?, ?, ?, ?, ?)
        """
        params = [
            encrypted_name,
            encrypted_email,
            worker.team,
            1 if worker.active else 0,
            worker.created_at.isoformat()
        ]
        
        query = self._execute_query(query_text, params=params)
        return query.lastInsertId()
    
    def find_by_id(self, worker_id: int) -> Optional[Worker]:
        """
        Findet Worker per ID (mit Entschlüsselung)
        
        Args:
            worker_id: ID des Workers
            
        Returns:
            Worker oder None
        """
        query_text = "SELECT * FROM workers WHERE id = ?"
        query = self._execute_query(query_text, params=[worker_id])
        
        if query.next():
            return self._map_to_entity(query)
        return None
    
    def find_all(self, active_only: bool = False) -> List[Worker]:
        """
        Findet alle Worker (mit Entschlüsselung)
        
        Args:
            active_only: Nur aktive Worker zurückgeben
            
        Returns:
            Liste von Worker-Objekten
        """
        query_text = "SELECT * FROM workers"
        params = []
        
        if active_only:
            query_text += " WHERE active = 1"
        
        query_text += " ORDER BY name ASC"
        
        query = self._execute_query(query_text, params=params if params else None)
        
        workers = []
        while query.next():
            workers.append(self._map_to_entity(query))
        
        return workers
    
    def find_by_email(self, email: str) -> Optional[Worker]:
        """
        Findet Worker per Email (mit Verschlüsselung für Suche)
        
        Args:
            email: Email-Adresse (Klartext)
            
        Returns:
            Worker oder None
        """
        # Email verschlüsseln für Suche
        encrypted_email = self.crypto_service.encrypt(email)
        
        query_text = "SELECT * FROM workers WHERE email = ?"
        query = self._execute_query(query_text, params=[encrypted_email])
        
        if query.next():
            return self._map_to_entity(query)
        return None
    
    def update(self, worker: Worker) -> bool:
        """
        Aktualisiert Worker (mit Verschlüsselung)
        
        Args:
            worker: Worker mit aktualisierten Daten und ID
            
        Returns:
            True bei Erfolg
        """
        # Sensible Daten verschlüsseln
        encrypted_name = self.crypto_service.encrypt(worker.name)
        encrypted_email = self.crypto_service.encrypt(worker.email)
        
        query_text = """
            UPDATE workers
            SET name = ?, email = ?, team = ?, active = ?
            WHERE id = ?
        """
        params = [
            encrypted_name,
            encrypted_email,
            worker.team,
            1 if worker.active else 0,
            worker.id
        ]
        
        query = self._execute_query(query_text, params=params)
        return query.numRowsAffected() > 0
    
    def delete(self, worker_id: int) -> bool:
        """
        Löscht Worker
        
        Args:
            worker_id: ID des zu löschenden Workers
            
        Returns:
            True bei Erfolg
        """
        query_text = "DELETE FROM workers WHERE id = ?"
        query = self._execute_query(query_text, params=[worker_id])
        return query.numRowsAffected() > 0
    
    def _map_to_entity(self, query) -> Worker:
        """
        Mappt QSqlQuery-Result zu Worker (mit Entschlüsselung)
        
        Args:
            query: QSqlQuery mit Daten
            
        Returns:
            Worker-Objekt mit entschlüsselten Daten
        """
        # Sensible Daten entschlüsseln
        encrypted_name = query.value("name")
        encrypted_email = query.value("email")
        
        decrypted_name = self.crypto_service.decrypt(encrypted_name)
        decrypted_email = self.crypto_service.decrypt(encrypted_email)
        
        return Worker(
            id=query.value("id"),
            name=decrypted_name,
            email=decrypted_email,
            team=query.value("team"),
            active=bool(query.value("active")),
            created_at=datetime.fromisoformat(query.value("created_at"))
        )
