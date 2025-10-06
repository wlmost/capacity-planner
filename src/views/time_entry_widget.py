"""
Time Entry Widget
UI-Komponente für Zeiterfassung
"""
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QDateEdit, 
    QTextEdit, QPushButton, QLabel, QComboBox,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from typing import Optional

from ..viewmodels.time_entry_viewmodel import TimeEntryViewModel


class TimeEntryWidget(QWidget):
    """
    Widget für Zeiterfassung
    
    Features:
    - Formular für Worker, Datum, Zeit, Beschreibung
    - Live-Validierung der Zeit-Eingabe
    - Status-Anzeige (Erfolg/Fehler)
    - Signal-basierte Kommunikation mit ViewModel
    
    Signals:
        entry_saved: Emittiert nach erfolgreicher Speicherung
    """
    
    entry_saved = Signal(int)  # Emittiert Entry-ID
    
    def __init__(self, viewmodel: TimeEntryViewModel, parent: Optional[QWidget] = None):
        """
        Initialisiert TimeEntryWidget
        
        Args:
            viewmodel: TimeEntryViewModel-Instanz
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Erstellt UI-Komponenten"""
        layout = QVBoxLayout(self)
        
        # Titel
        title = QLabel("Zeiterfassung")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Formular
        form_layout = QFormLayout()
        
        # Worker-Auswahl (Dropdown)
        self.worker_combo = QComboBox()
        self.worker_combo.addItem("Wähle Worker...", 0)
        form_layout.addRow("Worker:", self.worker_combo)
        
        # Datum (DateEdit)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        form_layout.addRow("Datum:", self.date_edit)
        
        # Zeit-Eingabe mit Live-Vorschau
        time_layout = QHBoxLayout()
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("z.B. 1:30, 90m, 1.5h")
        self.time_input.textChanged.connect(self._on_time_input_changed)
        time_layout.addWidget(self.time_input)
        
        self.time_preview = QLabel("")
        self.time_preview.setStyleSheet("color: #666; font-style: italic;")
        time_layout.addWidget(self.time_preview)
        
        form_widget = QWidget()
        form_widget.setLayout(time_layout)
        form_layout.addRow("Zeit:", form_widget)
        
        # Beschreibung (mehrzeilig)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Was hast du gemacht?")
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Beschreibung:", self.description_input)
        
        # Projekt (optional)
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("Optional")
        form_layout.addRow("Projekt:", self.project_input)
        
        layout.addLayout(form_layout)
        
        # Status-Label (für Fehler/Erfolg)
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Speichern")
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("Zurücksetzen")
        self.clear_button.clicked.connect(self._clear_form)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _connect_signals(self):
        """Verbindet Signals mit Slots"""
        # ViewModel Signals
        self.viewmodel.entry_created.connect(self._on_entry_created)
        self.viewmodel.validation_failed.connect(self._on_validation_failed)
        self.viewmodel.error_occurred.connect(self._on_error_occurred)
    
    def _on_time_input_changed(self, text: str):
        """
        Live-Vorschau der Zeit-Eingabe
        
        Args:
            text: Eingegebener Text
        """
        if not text:
            self.time_preview.setText("")
            return
        
        minutes = self.viewmodel.parse_time_input(text)
        
        if minutes:
            formatted = self.viewmodel.format_duration(minutes, "colon")
            hours = minutes / 60.0
            self.time_preview.setText(f"✓ {formatted} ({hours:.2f}h)")
            self.time_preview.setStyleSheet("color: green; font-style: italic;")
        else:
            self.time_preview.setText("✗ Ungültiges Format")
            self.time_preview.setStyleSheet("color: red; font-style: italic;")
    
    def _on_save_clicked(self):
        """Speichern-Button wurde geklickt"""
        # Daten aus Formular lesen
        worker_id = self.worker_combo.currentData()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        time_str = self.time_input.text().strip()
        description = self.description_input.toPlainText().strip()
        project = self.project_input.text().strip() or None
        
        # ViewModel aufrufen
        self.viewmodel.create_entry(worker_id, date_str, time_str, description, project)
    
    def _on_entry_created(self, entry_id: int):
        """
        Erfolgreiche Speicherung
        
        Args:
            entry_id: ID des erstellten Eintrags
        """
        self._show_status(f"✓ Zeiterfassung erfolgreich gespeichert (ID: {entry_id})", "success")
        self._clear_form()
        self.entry_saved.emit(entry_id)
    
    def _on_validation_failed(self, errors: list):
        """
        Validierung fehlgeschlagen
        
        Args:
            errors: Liste von Fehlermeldungen
        """
        error_text = "Bitte korrigiere folgende Fehler:\n" + "\n".join(f"• {err}" for err in errors)
        self._show_status(error_text, "error")
    
    def _on_error_occurred(self, error_msg: str):
        """
        Technischer Fehler aufgetreten
        
        Args:
            error_msg: Fehlermeldung
        """
        self._show_status(f"✗ Fehler: {error_msg}", "error")
        QMessageBox.critical(self, "Fehler", error_msg)
    
    def _show_status(self, message: str, status_type: str):
        """
        Zeigt Status-Nachricht an
        
        Args:
            message: Nachricht
            status_type: "success" oder "error"
        """
        self.status_label.setText(message)
        
        if status_type == "success":
            self.status_label.setStyleSheet("""
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                border-radius: 4px;
                padding: 10px;
            """)
        else:  # error
            self.status_label.setStyleSheet("""
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
                padding: 10px;
            """)
        
        self.status_label.setVisible(True)
    
    def _clear_form(self):
        """Setzt Formular zurück"""
        self.worker_combo.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())
        self.time_input.clear()
        self.description_input.clear()
        self.project_input.clear()
        self.status_label.setVisible(False)
        self.time_input.setFocus()
    
    def load_workers(self, workers: list):
        """Lädt Workers in Dropdown
        
        Args:
            workers: Liste von Worker-Objekten
        """
        # Bestehende Einträge löschen (außer "Wähle Worker...")
        while self.worker_combo.count() > 1:
            self.worker_combo.removeItem(1)
        
        # Neue Workers hinzufügen (nur aktive)
        for worker in workers:
            if worker.active:
                self.worker_combo.addItem(worker.name, worker.id)
