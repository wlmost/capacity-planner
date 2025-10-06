"""
WorkerWidget - UI für Worker Management
"""
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel,
    QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..viewmodels.worker_viewmodel import WorkerViewModel
from ..models.worker import Worker


class WorkerWidget(QWidget):
    """
    Widget für Worker Management
    
    Features:
        - Worker Liste mit Suche
        - Worker erstellen/bearbeiten
        - Worker aktivieren/deaktivieren
        - Validierung & Feedback
    """
    
    def __init__(self, viewmodel: WorkerViewModel):
        super().__init__()
        self._viewmodel = viewmodel
        self._current_worker_id: Optional[int] = None
        self._workers: List[Worker] = []
        
        self._setup_ui()
        self._connect_signals()
        self._load_workers()
    
    def _setup_ui(self):
        """Erstellt das UI Layout"""
        layout = QHBoxLayout(self)
        
        # Left Side: Worker List
        left_panel = self._create_list_panel()
        layout.addWidget(left_panel, stretch=2)
        
        # Right Side: Worker Form
        right_panel = self._create_form_panel()
        layout.addWidget(right_panel, stretch=1)
    
    def _create_list_panel(self) -> QWidget:
        """Erstellt das Listen-Panel"""
        panel = QGroupBox("Workers")
        layout = QVBoxLayout(panel)
        
        # Search & Filter
        filter_layout = QHBoxLayout()
        
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Suchen...")
        self._search_input.textChanged.connect(self._filter_workers)
        filter_layout.addWidget(self._search_input)
        
        self._show_inactive_checkbox = QCheckBox("Inaktive anzeigen")
        self._show_inactive_checkbox.stateChanged.connect(self._load_workers)
        filter_layout.addWidget(self._show_inactive_checkbox)
        
        layout.addLayout(filter_layout)
        
        # Worker Table
        self._worker_table = QTableWidget()
        self._worker_table.setColumnCount(4)
        self._worker_table.setHorizontalHeaderLabels(["ID", "Name", "E-Mail", "Team"])
        self._worker_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._worker_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._worker_table.setSelectionMode(QTableWidget.SingleSelection)
        self._worker_table.itemSelectionChanged.connect(self._on_worker_selected)
        layout.addWidget(self._worker_table)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        self._new_button = QPushButton("Neuer Worker")
        self._new_button.clicked.connect(self._on_new_clicked)
        button_layout.addWidget(self._new_button)
        
        self._delete_button = QPushButton("Löschen")
        self._delete_button.clicked.connect(self._on_delete_clicked)
        self._delete_button.setEnabled(False)
        button_layout.addWidget(self._delete_button)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def _create_form_panel(self) -> QWidget:
        """Erstellt das Formular-Panel"""
        panel = QGroupBox("Worker Details")
        layout = QVBoxLayout(panel)
        
        # Form
        form_layout = QFormLayout()
        
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Max Mustermann")
        form_layout.addRow("Name:", self._name_input)
        
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("max.mustermann@example.com")
        form_layout.addRow("E-Mail:", self._email_input)
        
        self._team_input = QLineEdit()
        self._team_input.setPlaceholderText("Engineering")
        form_layout.addRow("Team:", self._team_input)
        
        self._active_checkbox = QCheckBox("Aktiv")
        self._active_checkbox.setChecked(True)
        form_layout.addRow("Status:", self._active_checkbox)
        
        layout.addLayout(form_layout)
        
        # Status Label
        self._status_label = QLabel()
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)
        
        layout.addStretch()
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        self._save_button = QPushButton("Speichern")
        self._save_button.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(self._save_button)
        
        self._cancel_button = QPushButton("Abbrechen")
        self._cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self._cancel_button)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def _connect_signals(self):
        """Verbindet ViewModel Signals"""
        self._viewmodel.worker_created.connect(self._on_worker_created)
        self._viewmodel.worker_updated.connect(self._on_worker_updated)
        self._viewmodel.worker_deleted.connect(self._on_worker_deleted)
        self._viewmodel.workers_loaded.connect(self._on_workers_loaded)
        self._viewmodel.validation_failed.connect(self._on_validation_failed)
        self._viewmodel.error_occurred.connect(self._on_error_occurred)
    
    def _load_workers(self):
        """Lädt Workers vom ViewModel"""
        include_inactive = self._show_inactive_checkbox.isChecked()
        self._viewmodel.load_workers(include_inactive)
    
    def _filter_workers(self):
        """Filtert die Worker-Tabelle basierend auf Suchtext"""
        search_text = self._search_input.text().lower()
        
        for row in range(self._worker_table.rowCount()):
            show_row = False
            
            for col in range(self._worker_table.columnCount()):
                item = self._worker_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self._worker_table.setRowHidden(row, not show_row)
    
    def _populate_table(self, workers: List[Worker]):
        """Füllt die Tabelle mit Workers"""
        self._worker_table.setRowCount(0)
        self._workers = workers
        
        for worker in workers:
            row = self._worker_table.rowCount()
            self._worker_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(worker.id))
            id_item.setData(Qt.UserRole, worker.id)
            self._worker_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(worker.name)
            if not worker.active:
                font = name_item.font()
                font.setItalic(True)
                name_item.setFont(font)
                name_item.setForeground(Qt.gray)
            self._worker_table.setItem(row, 1, name_item)
            
            # Email
            email_item = QTableWidgetItem(worker.email)
            if not worker.active:
                font = email_item.font()
                font.setItalic(True)
                email_item.setFont(font)
                email_item.setForeground(Qt.gray)
            self._worker_table.setItem(row, 2, email_item)
            
            # Team
            team_item = QTableWidgetItem(worker.team or "-")
            if not worker.active:
                font = team_item.font()
                font.setItalic(True)
                team_item.setFont(font)
                team_item.setForeground(Qt.gray)
            self._worker_table.setItem(row, 3, team_item)
    
    def _clear_form(self):
        """Leert das Formular"""
        self._current_worker_id = None
        self._name_input.clear()
        self._email_input.clear()
        self._team_input.clear()
        self._active_checkbox.setChecked(True)
        self._status_label.clear()
    
    def _populate_form(self, worker: Worker):
        """Füllt das Formular mit Worker-Daten"""
        self._current_worker_id = worker.id
        self._name_input.setText(worker.name)
        self._email_input.setText(worker.email)
        self._team_input.setText(worker.team or "")
        self._active_checkbox.setChecked(worker.active)
        self._status_label.clear()
    
    def _on_worker_selected(self):
        """Handler für Worker-Auswahl"""
        selected_rows = self._worker_table.selectedItems()
        if not selected_rows:
            self._delete_button.setEnabled(False)
            return
        
        self._delete_button.setEnabled(True)
        
        # Get worker_id from first column
        row = selected_rows[0].row()
        worker_id = self._worker_table.item(row, 0).data(Qt.UserRole)
        
        # Find worker in list
        worker = next((w for w in self._workers if w.id == worker_id), None)
        if worker:
            self._populate_form(worker)
    
    def _on_new_clicked(self):
        """Handler für Neu-Button"""
        self._clear_form()
        self._worker_table.clearSelection()
        self._name_input.setFocus()
    
    def _on_save_clicked(self):
        """Handler für Speichern-Button"""
        name = self._name_input.text()
        email = self._email_input.text()
        team = self._team_input.text()
        active = self._active_checkbox.isChecked()
        
        if self._current_worker_id is None:
            # Create new
            self._viewmodel.create_worker(name, email, team, active)
        else:
            # Update existing
            self._viewmodel.update_worker(self._current_worker_id, name, email, team, active)
    
    def _on_cancel_clicked(self):
        """Handler für Abbrechen-Button"""
        self._clear_form()
        self._worker_table.clearSelection()
    
    def _on_delete_clicked(self):
        """Handler für Löschen-Button"""
        if self._current_worker_id is None:
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Worker löschen",
            "Möchten Sie diesen Worker wirklich löschen?\n\n"
            "Hinweis: Alle zugehörigen Zeiterfassungen und Kapazitäten werden ebenfalls gelöscht.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._viewmodel.delete_worker(self._current_worker_id)
    
    def _on_worker_created(self, worker_id: int):
        """Handler für worker_created Signal"""
        self._show_success(f"Worker erfolgreich erstellt (ID: {worker_id})")
        self._clear_form()
        self._load_workers()
    
    def _on_worker_updated(self, worker_id: int):
        """Handler für worker_updated Signal"""
        self._show_success(f"Worker erfolgreich aktualisiert")
        self._load_workers()
    
    def _on_worker_deleted(self, worker_id: int):
        """Handler für worker_deleted Signal"""
        self._show_success(f"Worker erfolgreich gelöscht")
        self._clear_form()
        self._load_workers()
    
    def _on_workers_loaded(self, workers: List[Worker]):
        """Handler für workers_loaded Signal"""
        self._populate_table(workers)
    
    def _on_validation_failed(self, message: str):
        """Handler für validation_failed Signal"""
        self._show_error(message)
    
    def _on_error_occurred(self, message: str):
        """Handler für error_occurred Signal"""
        self._show_error(message)
    
    def _show_success(self, message: str):
        """Zeigt Erfolgs-Nachricht"""
        self._status_label.setText(f"✓ {message}")
        self._status_label.setStyleSheet("color: green;")
    
    def _show_error(self, message: str):
        """Zeigt Fehler-Nachricht"""
        self._status_label.setText(f"✗ {message}")
        self._status_label.setStyleSheet("color: red;")
