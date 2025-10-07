"""
Session Service für Worker-Login und Admin-Mode

Verwaltet die aktuelle Benutzer-Session:
- Worker-ID des angemeldeten Workers
- Admin-Mode Flag
- Session-Persistenz (Speichern/Laden)
"""

import json
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class Session:
    """Repräsentiert eine Benutzer-Session"""
    worker_id: Optional[int]  # None bei Admin-Mode
    is_admin: bool
    remember: bool
    
    def is_worker_mode(self) -> bool:
        """Prüft ob Worker-Mode aktiv ist"""
        return self.worker_id is not None and not self.is_admin
    
    def is_admin_mode(self) -> bool:
        """Prüft ob Admin-Mode aktiv ist"""
        return self.is_admin


class SessionService:
    """
    Verwaltet die aktuelle Worker-Session
    
    Features:
    - Login als Worker oder Admin
    - Session-Persistenz in settings.json
    - Logout-Funktionalität
    - Abfrage des aktuellen Status
    
    Verwendung:
        session = SessionService()
        
        # Login als Worker
        session.login(worker_id=5, is_admin=False, remember=True)
        
        # Oder als Admin
        session.login(worker_id=None, is_admin=True, remember=False)
        
        # Aktuelle Session abfragen
        if session.is_worker_mode():
            worker_id = session.get_current_worker_id()
        
        # Gespeicherte Session laden
        saved = session.load_saved_session()
        if saved:
            worker_id, is_admin = saved
    """
    
    def __init__(self, settings_path: Optional[Path] = None):
        """
        Initialisiert Session-Service
        
        Args:
            settings_path: Pfad zur settings.json (optional)
        """
        self._session: Optional[Session] = None
        
        # Pfad zur Settings-Datei
        if settings_path:
            self._settings_path = settings_path
        else:
            # Standard: Neben der Datenbank
            app_dir = Path.home() / ".capacity_planner"
            app_dir.mkdir(exist_ok=True)
            self._settings_path = app_dir / "session.json"
    
    def login(self, worker_id: Optional[int], is_admin: bool, remember: bool = False) -> None:
        """
        Meldet Worker oder Admin an
        
        Args:
            worker_id: ID des Workers (None bei Admin-Mode)
            is_admin: True für Admin-Mode
            remember: True wenn Session gespeichert werden soll
        
        Raises:
            ValueError: Wenn Parameter-Kombination ungültig
        """
        # Validierung
        if is_admin and worker_id is not None:
            # Admin-Mode OHNE Worker-ID oder Worker-Mode MIT Worker-ID
            pass  # Beides ist ok: Admin kann auch Worker-Perspektive haben
        elif not is_admin and worker_id is None:
            raise ValueError("Worker-Mode benötigt eine Worker-ID")
        
        # Session erstellen
        self._session = Session(
            worker_id=worker_id,
            is_admin=is_admin,
            remember=remember
        )
        
        # Optional: Speichern
        if remember:
            self._save_session()
    
    def logout(self) -> None:
        """
        Meldet aktuellen Worker/Admin ab
        
        Löscht sowohl die In-Memory Session als auch die gespeicherte Session.
        """
        self._session = None
        
        # Gespeicherte Session löschen
        if self._settings_path.exists():
            try:
                self._settings_path.unlink()
            except Exception as e:
                # Fehler beim Löschen ignorieren (nicht kritisch)
                print(f"Warning: Could not delete session file: {e}")
    
    def is_logged_in(self) -> bool:
        """
        Prüft ob eine aktive Session existiert
        
        Returns:
            True wenn jemand angemeldet ist
        """
        return self._session is not None
    
    def is_worker_mode(self) -> bool:
        """
        Prüft ob Worker-Mode aktiv ist
        
        Returns:
            True wenn als Worker (nicht Admin) angemeldet
        """
        return self._session is not None and self._session.is_worker_mode()
    
    def is_admin_mode(self) -> bool:
        """
        Prüft ob Admin-Mode aktiv ist
        
        Returns:
            True wenn als Admin angemeldet
        """
        return self._session is not None and self._session.is_admin_mode()
    
    def get_current_worker_id(self) -> Optional[int]:
        """
        Gibt Worker-ID der aktuellen Session zurück
        
        Returns:
            Worker-ID oder None bei Admin-Mode oder nicht angemeldet
        """
        if self._session:
            return self._session.worker_id
        return None
    
    def get_current_session(self) -> Optional[Session]:
        """
        Gibt aktuelle Session zurück
        
        Returns:
            Session-Objekt oder None
        """
        return self._session
    
    def load_saved_session(self) -> Optional[Tuple[Optional[int], bool]]:
        """
        Lädt gespeicherte Session aus Datei
        
        Returns:
            Tuple (worker_id, is_admin) oder None wenn keine Session gespeichert
        """
        if not self._settings_path.exists():
            return None
        
        try:
            with open(self._settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            worker_id = data.get('worker_id')
            is_admin = data.get('is_admin', False)
            remember = data.get('remember', True)
            
            # Session wiederherstellen
            self._session = Session(
                worker_id=worker_id,
                is_admin=is_admin,
                remember=remember
            )
            
            return (worker_id, is_admin)
        
        except Exception as e:
            print(f"Warning: Could not load session: {e}")
            return None
    
    def _save_session(self) -> None:
        """Speichert aktuelle Session in Datei"""
        if not self._session:
            return
        
        data = {
            'worker_id': self._session.worker_id,
            'is_admin': self._session.is_admin,
            'remember': self._session.remember
        }
        
        try:
            # Verzeichnis erstellen falls nötig
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"Warning: Could not save session: {e}")
    
    def __repr__(self) -> str:
        """String-Repräsentation für Debugging"""
        if not self._session:
            return "SessionService(not logged in)"
        
        if self._session.is_admin_mode():
            return "SessionService(admin mode)"
        else:
            return f"SessionService(worker_id={self._session.worker_id})"
