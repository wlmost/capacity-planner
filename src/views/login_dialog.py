"""
Login-Dialog für Worker-Auswahl

Ermöglicht Auswahl eines Workers per Name oder Email beim Anwendungsstart.
Optional: Admin-Mode für Ansicht aller Worker.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QCheckBox, QPushButton, QCompleter,
    QMessageBox
)
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtGui import QFont
from typing import Optional, List

from ..repositories.worker_repository import WorkerRepository
from ..models.worker import Worker
from ..services.database_service import DatabaseService
from ..services.crypto_service import CryptoService


class LoginDialog(QDialog):
    """
    Dialog zur Worker-Auswahl beim App-Start
    
    Features:
    - Eingabefeld mit Autovervollständigung
    - Suche nach Name oder Email
    - Admin-Mode Checkbox
    - "Anmeldung merken" Option
    
    Verwendung:
        dialog = LoginDialog()
        if dialog.exec() == QDialog.Accepted:
            worker_id = dialog.selected_worker_id
            is_admin = dialog.is_admin
            remember = dialog.remember_login
    """
    
    def __init__(self, 
                 db_service: Optional[DatabaseService] = None, 
                 crypto_service: Optional[CryptoService] = None,
                 parent=None):
        super().__init__(parent)
        
        self.selected_worker_id: Optional[int] = None
        self.is_admin: bool = False
        self.remember_login: bool = False
        
        self._workers: List[Worker] = []
        
        # Services initialisieren oder übernehmen
        if db_service is None:
            db_service = DatabaseService()
            db_service.initialize()
        self._db_service = db_service
        
        if crypto_service is None:
            crypto_service = CryptoService()
            crypto_service.initialize_keys()
        self._crypto_service = crypto_service
        
        self._worker_repository = WorkerRepository(self._db_service, self._crypto_service)
        
        self._setup_ui()
        self._load_workers()
        self._setup_completer()
    
    def _setup_ui(self):
        """Erstellt UI-Elemente"""
        self.setWindowTitle("Capacity Planner - Anmeldung")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Titel
        title = QLabel("🔐 Anmeldung")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Beschreibung
        desc = QLabel(
            "Bitte gib deinen Namen oder deine Email-Adresse ein,\n"
            "um dich anzumelden."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)
        
        # Eingabefeld mit Label
        input_layout = QVBoxLayout()
        input_label = QLabel("Name oder Email:")
        input_layout.addWidget(input_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("z.B. Max Mustermann oder max@example.com")
        self.name_input.textChanged.connect(self._on_input_changed)
        self.name_input.returnPressed.connect(self._on_login_clicked)
        input_layout.addWidget(self.name_input)
        layout.addLayout(input_layout)
        
        # Optionen
        options_layout = QVBoxLayout()
        
        self.admin_checkbox = QCheckBox("Als Administrator anmelden")
        self.admin_checkbox.setToolTip(
            "Admin-Modus: Ansicht aller Worker (keine Zeiterfassung möglich)"
        )
        options_layout.addWidget(self.admin_checkbox)
        
        self.remember_checkbox = QCheckBox("Anmeldung merken")
        self.remember_checkbox.setToolTip(
            "Beim nächsten Start automatisch anmelden"
        )
        self.remember_checkbox.setChecked(True)  # Standard: aktiviert
        options_layout.addWidget(self.remember_checkbox)
        
        layout.addLayout(options_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.login_button = QPushButton("Anmelden")
        self.login_button.setDefault(True)
        self.login_button.setEnabled(False)  # Initially disabled
        self.login_button.clicked.connect(self._on_login_clicked)
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
        
        # Status-Label (für Fehlermeldungen)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
    
    def _load_workers(self):
        """Lädt alle aktiven Worker aus der Datenbank"""
        try:
            self._workers = self._worker_repository.find_all(active_only=True)
            
            # Wenn keine Worker vorhanden: Admin-Mode erzwingen
            if not self._workers:
                self._show_no_workers_message()
        except Exception as e:
            self._show_error(f"Fehler beim Laden der Worker: {e}")
    
    def _show_no_workers_message(self):
        """Zeigt Hinweis an, wenn keine Worker vorhanden sind"""
        self.status_label.setText(
            "⚠️ Keine Worker in der Datenbank!\n"
            "Du wirst im Admin-Mode angemeldet.\n"
            "Bitte erstelle zunächst Worker-Stammdaten."
        )
        self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        self.status_label.setVisible(True)
        
        # Admin-Mode automatisch aktivieren
        self.admin_checkbox.setChecked(True)
        self.admin_checkbox.setEnabled(False)
        
        # Eingabefeld deaktivieren (nicht benötigt)
        self.name_input.setEnabled(False)
        self.name_input.setPlaceholderText("(Admin-Mode: Keine Worker-Auswahl erforderlich)")
        
        # Login-Button aktivieren
        self.login_button.setEnabled(True)
        self.login_button.setText("Als Administrator fortfahren")
    
    def _setup_completer(self):
        """Konfiguriert Autovervollständigung"""
        if not self._workers:
            return
        
        # Liste mit Namen und Emails
        suggestions = []
        for worker in self._workers:
            suggestions.append(worker.name)
            if worker.email:
                suggestions.append(worker.email)
        
        # Completer erstellen
        model = QStringListModel(suggestions)
        completer = QCompleter(model, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        
        self.name_input.setCompleter(completer)
    
    def _on_input_changed(self, text: str):
        """Reagiert auf Textänderung im Eingabefeld"""
        # Login-Button nur aktivieren wenn Text eingegeben wurde oder Admin-Mode
        has_text = bool(text.strip())
        is_admin = self.admin_checkbox.isChecked()
        
        self.login_button.setEnabled(has_text or is_admin)
        self.status_label.setVisible(False)
    
    def _on_login_clicked(self):
        """Behandelt Login-Button-Click"""
        input_text = self.name_input.text().strip()
        is_admin = self.admin_checkbox.isChecked()
        
        # Admin-Mode: Kein Worker erforderlich
        if is_admin:
            if not input_text:
                # Admin ohne spezifischen Worker
                self.selected_worker_id = None
            else:
                # Admin MIT Worker-Perspektive
                worker = self._find_worker(input_text)
                if worker:
                    self.selected_worker_id = worker.id
                else:
                    self._show_error(f"Worker '{input_text}' nicht gefunden")
                    return
            
            self.is_admin = True
            self.remember_login = self.remember_checkbox.isChecked()
            self.accept()
            return
        
        # Worker-Mode: Worker muss gefunden werden
        if not input_text:
            self._show_error("Bitte Name oder Email eingeben")
            return
        
        worker = self._find_worker(input_text)
        if worker:
            self.selected_worker_id = worker.id
            self.is_admin = False
            self.remember_login = self.remember_checkbox.isChecked()
            self.accept()
        else:
            self._show_error(f"Worker '{input_text}' nicht gefunden")
    
    def _find_worker(self, search_text: str) -> Optional[Worker]:
        """
        Sucht Worker nach Name oder Email
        
        Args:
            search_text: Name oder Email (case-insensitive)
        
        Returns:
            Worker-Objekt oder None
        """
        search_lower = search_text.lower()
        
        for worker in self._workers:
            # Exakte Übereinstimmung (Name oder Email)
            if worker.name.lower() == search_lower:
                return worker
            if worker.email and worker.email.lower() == search_lower:
                return worker
        
        # Partielle Übereinstimmung (nur Name)
        for worker in self._workers:
            if search_lower in worker.name.lower():
                return worker
        
        return None
    
    def _show_error(self, message: str):
        """Zeigt Fehlermeldung an"""
        self.status_label.setText(f"❌ {message}")
        self.status_label.setVisible(True)
    
    def get_selected_worker(self) -> Optional[Worker]:
        """
        Gibt den ausgewählten Worker zurück
        
        Returns:
            Worker-Objekt oder None bei Admin-Mode ohne Worker
        """
        if self.selected_worker_id is None:
            return None
        
        try:
            return self._worker_repository.find_by_id(self.selected_worker_id)
        except Exception:
            return None
