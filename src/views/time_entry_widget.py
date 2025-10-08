"""
Time Entry Widget
UI-Komponente für Zeiterfassung mit Formular und Liste
"""
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QDateEdit, 
    QTextEdit, QPushButton, QLabel, QComboBox,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QCompleter
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from typing import Optional, List

from ..viewmodels.time_entry_viewmodel import TimeEntryViewModel
from ..repositories.time_entry_repository import TimeEntryRepository


class TimeEntryWidget(QWidget):
    """
    Widget für Zeiterfassung
    
    Features:
    - Zweigeteilt: Formular (oben) + Liste (unten)
    - Formular: Worker, Datum, Typ, Projekt, Kategorie, Beschreibung, Dauer
    - Liste: Alle Zeitbuchungen mit Löschen-Button
    - Automatisches Refresh der Liste
    - Live-Validierung der Zeit-Eingabe
    - Autovervollständigung für Projekte
    
    Signals:
        entry_saved: Emittiert nach erfolgreicher Speicherung
        entry_deleted: Emittiert nach erfolgreichem Löschen
    """
    
    entry_saved = Signal(int)  # Emittiert Entry-ID
    entry_deleted = Signal(int)  # Emittiert Entry-ID
    
    def __init__(
        self, 
        viewmodel: TimeEntryViewModel,
        time_entry_repository: TimeEntryRepository,
        parent: Optional[QWidget] = None
    ):
        """
        Initialisiert TimeEntryWidget
        
        Args:
            viewmodel: TimeEntryViewModel-Instanz
            time_entry_repository: Repository für TimeEntry-Zugriff
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.time_entry_repository = time_entry_repository
        self._workers = []
        self._project_completer = None
        
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
        
        # Splitter für Formular (oben) und Liste (unten)
        splitter = QSplitter(Qt.Vertical)
        
        # === OBERER TEIL: FORMULAR ===
        form_widget = self._create_form_widget()
        splitter.addWidget(form_widget)
        
        # === UNTERER TEIL: LISTE ===
        list_widget = self._create_list_widget()
        splitter.addWidget(list_widget)
        
        # Splitter-Verhältnis: 40% Formular, 60% Liste
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        
        layout.addWidget(splitter)
    
    def _create_form_widget(self) -> QWidget:
        """Erstellt Formular-Widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Formular-Layout
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
        
        # Typ (Combobox: Arbeit, Urlaub, Abwesenheit)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Arbeit", "Urlaub", "Abwesenheit"])
        form_layout.addRow("Typ:", self.type_combo)
        
        # Projekt (Editable Combobox mit Autovervollständigung)
        self.project_input = QComboBox()
        self.project_input.setEditable(True)
        self.project_input.setInsertPolicy(QComboBox.NoInsert)
        self.project_input.lineEdit().setPlaceholderText("Optional - z.B. Projektname")
        form_layout.addRow("Projekt:", self.project_input)
        
        # Kategorie (LineEdit)
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Optional - z.B. Development, Meeting")
        form_layout.addRow("Kategorie:", self.category_input)
        
        # Beschreibung (mehrzeilig)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Was hast du gemacht?")
        self.description_input.setMaximumHeight(60)
        form_layout.addRow("Beschreibung:", self.description_input)
        
        # Dauer mit Live-Vorschau
        time_layout = QHBoxLayout()
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("z.B. 1:30, 3h, 90m, 15m")
        self.time_input.textChanged.connect(self._on_time_input_changed)
        time_layout.addWidget(self.time_input)
        
        self.time_preview = QLabel("")
        self.time_preview.setStyleSheet("color: #666; font-style: italic;")
        time_layout.addWidget(self.time_preview)
        
        time_widget = QWidget()
        time_widget.setLayout(time_layout)
        form_layout.addRow("Dauer:", time_widget)
        
        layout.addLayout(form_layout)
        
        # Status-Label (für Fehler/Erfolg)
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Speichern")
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("🔄 Zurücksetzen")
        self.clear_button.clicked.connect(self._clear_form)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_list_widget(self) -> QWidget:
        """Erstellt Listen-Widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Titel
        list_title = QLabel("📋 Alle Zeitbuchungen")
        list_title_font = QFont()
        list_title_font.setPointSize(12)
        list_title_font.setBold(True)
        list_title.setFont(list_title_font)
        layout.addWidget(list_title)
        
        # Tabelle
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(8)
        self.entries_table.setHorizontalHeaderLabels([
            "Datum", "Worker", "Typ", "Projekt", "Kategorie", 
            "Beschreibung", "Dauer", "Aktion"
        ])
        self.entries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.entries_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.entries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setSortingEnabled(True)
        
        layout.addWidget(self.entries_table)
        
        return widget
    
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
        
        # Neues Format: Typ wird der Beschreibung vorangestellt (für Kompatibilität)
        entry_type = self.type_combo.currentText()
        if entry_type != "Arbeit":
            description = f"[{entry_type}] {description}"
        
        # Projekt und Kategorie kombinieren
        project = self.project_input.currentText().strip() or None
        category = self.category_input.text().strip()
        if category and project:
            project = f"{project} - {category}"
        elif category:
            project = category
        
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
        self._refresh_entries_list()
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
        self.type_combo.setCurrentIndex(0)
        self.project_input.clearEditText()
        self.category_input.clear()
        self.time_input.clear()
        self.description_input.clear()
        self.status_label.setVisible(False)
        self.time_input.setFocus()
    
    def _refresh_entries_list(self):
        """Aktualisiert die Liste der Zeitbuchungen"""
        try:
            # Alle Einträge laden (letzte 30 Tage)
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            entries = self.time_entry_repository.find_by_date_range(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            # Sortiere nach Datum absteigend
            entries.sort(key=lambda e: e.date, reverse=True)
            
            # Tabelle leeren
            self.entries_table.setRowCount(0)
            self.entries_table.setSortingEnabled(False)
            
            # Worker-Namen als Dict für schnellen Zugriff
            worker_names = {w.id: w.name for w in self._workers}
            
            # Einträge in Tabelle einfügen
            for entry in entries:
                row = self.entries_table.rowCount()
                self.entries_table.insertRow(row)
                
                # Datum
                date_item = QTableWidgetItem(entry.date.strftime("%d.%m.%Y"))
                self.entries_table.setItem(row, 0, date_item)
                
                # Worker
                worker_name = worker_names.get(entry.worker_id, f"ID:{entry.worker_id}")
                worker_item = QTableWidgetItem(worker_name)
                self.entries_table.setItem(row, 1, worker_item)
                
                # Typ (aus Beschreibung extrahieren)
                entry_type = "Arbeit"
                description = entry.description
                if description.startswith("["):
                    end_bracket = description.find("]")
                    if end_bracket > 0:
                        entry_type = description[1:end_bracket]
                        description = description[end_bracket+1:].strip()
                
                type_item = QTableWidgetItem(entry_type)
                self.entries_table.setItem(row, 2, type_item)
                
                # Projekt und Kategorie
                project = entry.project or ""
                category = ""
                if " - " in project:
                    project, category = project.split(" - ", 1)
                
                project_item = QTableWidgetItem(project)
                self.entries_table.setItem(row, 3, project_item)
                
                category_item = QTableWidgetItem(category)
                self.entries_table.setItem(row, 4, category_item)
                
                # Beschreibung
                desc_item = QTableWidgetItem(description[:50] + "..." if len(description) > 50 else description)
                self.entries_table.setItem(row, 5, desc_item)
                
                # Dauer
                hours = entry.duration_minutes / 60.0
                duration_str = f"{entry.duration_minutes}m ({hours:.2f}h)"
                duration_item = QTableWidgetItem(duration_str)
                self.entries_table.setItem(row, 6, duration_item)
                
                # Löschen-Button
                delete_button = QPushButton("🗑️ Löschen")
                delete_button.clicked.connect(lambda checked, e_id=entry.id: self._on_delete_entry(e_id))
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                self.entries_table.setCellWidget(row, 7, delete_button)
            
            self.entries_table.setSortingEnabled(True)
            
        except Exception as e:
            self._show_status(f"Fehler beim Laden der Einträge: {str(e)}", "error")
    
    def _on_delete_entry(self, entry_id: int):
        """
        Löscht einen Eintrag
        
        Args:
            entry_id: ID des zu löschenden Eintrags
        """
        reply = QMessageBox.question(
            self,
            "Eintrag löschen",
            f"Möchtest du den Eintrag (ID: {entry_id}) wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.time_entry_repository.delete(entry_id)
                if success:
                    self._show_status(f"✓ Eintrag {entry_id} erfolgreich gelöscht", "success")
                    self._refresh_entries_list()
                    self.entry_deleted.emit(entry_id)
                else:
                    self._show_status(f"✗ Eintrag {entry_id} konnte nicht gelöscht werden", "error")
            except Exception as e:
                self._show_status(f"✗ Fehler beim Löschen: {str(e)}", "error")
    
    def _update_project_completer(self):
        """Aktualisiert Autovervollständigung für Projekte"""
        try:
            # Alle Einträge laden
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # Letzte 12 Monate
            
            entries = self.time_entry_repository.find_by_date_range(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            # Einzigartige Projekte extrahieren
            projects = set()
            for entry in entries:
                if entry.project:
                    # Nur Projekt-Teil (vor " - ")
                    project = entry.project.split(" - ")[0] if " - " in entry.project else entry.project
                    projects.add(project)
            
            # Completer erstellen
            completer = QCompleter(sorted(projects))
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.project_input.setCompleter(completer)
            
            # Auch Items zum ComboBox hinzufügen
            self.project_input.clear()
            for project in sorted(projects):
                self.project_input.addItem(project)
            self.project_input.setCurrentIndex(-1)  # Kein Item ausgewählt
            
        except Exception as e:
            pass  # Fehler bei Autovervollständigung ignorieren
    
    def load_workers(self, workers: List):
        """Lädt Workers in Dropdown
        
        Args:
            workers: Liste von Worker-Objekten
        """
        self._workers = workers
        
        # Bestehende Einträge löschen (außer "Wähle Worker...")
        while self.worker_combo.count() > 1:
            self.worker_combo.removeItem(1)
        
        # Neue Workers hinzufügen (nur aktive)
        for worker in workers:
            if worker.active:
                self.worker_combo.addItem(worker.name, worker.id)
        
        # Single-Worker-Mode: Worker automatisch vorauswählen
        if len(workers) == 1 and workers[0].active:
            # Setze auf Index 1 (Index 0 ist "Wähle Worker...")
            self.worker_combo.setCurrentIndex(1)
            # Optional: Dropdown verstecken, da nur ein Worker
            # self.worker_combo.setEnabled(False)
        
        # Einträge-Liste aktualisieren
        self._refresh_entries_list()
        
        # Projekt-Autovervollständigung aktualisieren
        self._update_project_completer()
