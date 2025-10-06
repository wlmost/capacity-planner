"""
Base Repository
Gemeinsame Funktionalität für alle Repositories
"""
from typing import Optional, List, TypeVar, Generic
from PySide6.QtSql import QSqlQuery
from ..services.database_service import DatabaseService

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Basis-Repository mit gemeinsamen CRUD-Operationen
    
    Implementiert Repository Pattern für Datenzugriff
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialisiert Repository
        
        Args:
            db_service: Datenbankservice-Instanz
        """
        self.db_service = db_service
    
    def _execute_query(self, query_text: str, params: Optional[list] = None) -> QSqlQuery:
        """
        Führt Query aus (Wrapper für db_service)
        
        Args:
            query_text: SQL-Statement
            params: Parameter für Prepared Statement
            
        Returns:
            QSqlQuery-Objekt
        """
        return self.db_service.execute_query(query_text, params)
    
    def begin_transaction(self) -> bool:
        """Startet Transaktion"""
        return self.db_service.db.transaction()
    
    def commit_transaction(self) -> bool:
        """Commitet Transaktion"""
        return self.db_service.db.commit()
    
    def rollback_transaction(self) -> bool:
        """Rollt Transaktion zurück"""
        return self.db_service.db.rollback()
