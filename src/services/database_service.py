"""
Database Service
Qt SQL Connection Management und Schema-Migration
"""
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from pathlib import Path
from typing import Optional


class DatabaseService:
    """
    Verwaltet SQLite-Datenbankverbindung via Qt SQL
    
    Funktionen:
    - Connection Management
    - Schema-Migration
    - Transaction Handling
    
    Beispiel:
        >>> db = DatabaseService("capacity_planner.db")
        >>> db.initialize()
        >>> db.execute_query("SELECT * FROM workers")
    """
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialisiert Database Service
        
        Args:
            database_path: Pfad zur SQLite-Datei (default: ~/.capacity_planner/data.db)
        """
        if database_path is None:
            data_dir = Path.home() / ".capacity_planner"
            data_dir.mkdir(parents=True, exist_ok=True)
            database_path = str(data_dir / "data.db")
        
        self.database_path = database_path
        self.connection_name = "capacity_planner_main"
        self.db: Optional[QSqlDatabase] = None
    
    def initialize(self) -> bool:
        """
        Initialisiert Datenbankverbindung und Schema
        
        Returns:
            True bei Erfolg
        """
        # Verbindung erstellen
        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        self.db.setDatabaseName(self.database_path)
        
        if not self.db.open():
            raise RuntimeError(f"Konnte Datenbank nicht öffnen: {self.db.lastError().text()}")
        
        # Schema erstellen/migrieren
        self._create_schema()
        
        return True
    
    def _create_schema(self) -> None:
        """Erstellt Datenbank-Schema"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                team TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                date DATE NOT NULL,
                duration_minutes INTEGER NOT NULL,
                description TEXT NOT NULL,
                project TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS capacities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worker_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                planned_hours REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (worker_id) REFERENCES workers(id)
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_time_entries_worker 
            ON time_entries(worker_id, date)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_capacities_worker 
            ON capacities(worker_id, start_date, end_date)
            """
        ]
        
        for query_text in queries:
            query = QSqlQuery(self.db)
            if not query.exec(query_text):
                raise RuntimeError(f"Schema-Erstellung fehlgeschlagen: {query.lastError().text()}")
    
    def execute_query(self, query_text: str, params: Optional[list] = None) -> QSqlQuery:
        """
        Führt SQL-Query aus
        
        Args:
            query_text: SQL-Statement
            params: Parameter für Prepared Statement
            
        Returns:
            QSqlQuery-Objekt mit Ergebnissen
        """
        query = QSqlQuery(self.db)
        query.prepare(query_text)
        
        if params:
            for param in params:
                query.addBindValue(param)
        
        if not query.exec():
            raise RuntimeError(f"Query fehlgeschlagen: {query.lastError().text()}")
        
        return query
    
    def close(self) -> None:
        """Schließt Datenbankverbindung"""
        if self.db:
            self.db.close()
            QSqlDatabase.removeDatabase(self.connection_name)
    
    def get_db_path(self) -> str:
        """
        Gibt den Pfad zur Datenbankdatei zurück
        
        Returns:
            Absoluter Pfad zur Datenbank
        """
        return self.database_path
