"""
Time Entry Widget
UI-Komponente für Zeiterfassung mit Formular und Liste
"""
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QDateEdit, 
    QTextEdit, QPushButton, QLabel, QComboBox,
    QVBoxLayout, QHBoxLayout, QMessageBox, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QCompleter,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QDate, Signal, QSettings
from PySide6.QtGui import QFont
from typing import Optional, List, Dict
from datetime import datetime

from ..viewmodels.time_entry_viewmodel import TimeEntryViewModel
from ..repositories.time_entry_repository import TimeEntryRepository
from .date_range_widget import DateRangeWidget
from .timer_widget import TimerWidget


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
        
        # Datumsfilter-State (Standard: Heute)
        self._filter_start_date = QDate.currentDate()
        self._filter_end_date = QDate.currentDate()
        
        # Timer-Widgets Tracking (entry_id -> TimerWidget)
        self._timer_widgets: Dict[int, TimerWidget] = {}
        
        # Entry-ID zu Row-Mapping (für Updates)
        self._entry_row_map: Dict[int, int] = {}
        
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
        self.date_label = QLabel("Datum:")
        form_layout.addRow(self.date_label, self.date_edit)
        
        # End-Datum (DateEdit) - nur für Urlaub sichtbar
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.end_date_label = QLabel("Datum (Bis):")
        form_layout.addRow(self.end_date_label, self.end_date_edit)
        
        # Initial verstecken (nur bei Urlaub sichtbar)
        self.end_date_edit.setVisible(False)
        self.end_date_label.setVisible(False)
        
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
        
        # DateRangeWidget für Filterung
        self.date_range_widget = DateRangeWidget()
        layout.addWidget(self.date_range_widget)
        
        # Tabelle
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(9)  # Eine Spalte mehr für Timer
        self.entries_table.setHorizontalHeaderLabels([
            "Datum", "Worker", "Typ", "Projekt", "Kategorie", 
            "Beschreibung", "Dauer", "Timer", "Aktion"
        ])
        self.entries_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.entries_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.entries_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setSortingEnabled(True)
        
        # Editierbar machen (Doppelklick oder F2)
        self.entries_table.setEditTriggers(
            QAbstractItemView.DoubleClicked | 
            QAbstractItemView.EditKeyPressed
        )
        
        # Signal für Zell-Änderungen
        self.entries_table.itemChanged.connect(self._on_table_item_changed)
        
        layout.addWidget(self.entries_table)
        
        return widget
    
    def _connect_signals(self):
        """Verbindet Signals mit Slots"""
        # ViewModel Signals
        self.viewmodel.entry_created.connect(self._on_entry_created)
        self.viewmodel.validation_failed.connect(self._on_validation_failed)
        self.viewmodel.error_occurred.connect(self._on_error_occurred)
        
        # DateRangeWidget Signal
        self.date_range_widget.date_range_changed.connect(self._on_date_range_changed)
        
        # Typ-Änderung für Urlaubs-Logik
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        
        # Datumsänderungen für automatische Dauer-Berechnung
        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.end_date_edit.dateChanged.connect(self._on_date_changed)
        
        # Worker-Änderung für Regelarbeitszeit
        self.worker_combo.currentIndexChanged.connect(self._on_worker_changed)
    
    def _on_time_input_changed(self, text: str):
        """
        Live-Vorschau der Zeit-Eingabe
        
        Args:
            text: Eingegebener Text
        """
        # Bei Urlaub wird Dauer automatisch berechnet
        if self.type_combo.currentText() == "Urlaub":
            return
        
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
    
    def _on_type_changed(self, index: int):
        """
        Wird aufgerufen wenn Typ geändert wird
        
        Args:
            index: Index des ausgewählten Typs
        """
        entry_type = self.type_combo.currentText()
        
        if entry_type == "Urlaub":
            # End-Datum-Feld anzeigen
            self.end_date_edit.setVisible(True)
            self.end_date_label.setVisible(True)
            
            # Datum-Label ändern
            self.date_label.setText("Datum (Von):")
            
            # Dauer-Feld readonly machen (wird automatisch berechnet)
            self.time_input.setReadOnly(True)
            self.time_input.setStyleSheet("background-color: #f0f0f0;")
            
            # Dauer automatisch berechnen
            self._calculate_vacation_duration()
            
        else:
            # End-Datum-Feld verstecken
            self.end_date_edit.setVisible(False)
            self.end_date_label.setVisible(False)
            
            # Datum-Label zurücksetzen
            self.date_label.setText("Datum:")
            
            # Dauer-Feld wieder editierbar
            self.time_input.setReadOnly(False)
            self.time_input.setStyleSheet("")
            self.time_input.clear()
            self.time_preview.setText("")
    
    def _on_date_changed(self):
        """Wird aufgerufen wenn ein Datum geändert wird"""
        if self.type_combo.currentText() == "Urlaub":
            self._calculate_vacation_duration()
    
    def _on_worker_changed(self, index: int):
        """Wird aufgerufen wenn Worker geändert wird"""
        if self.type_combo.currentText() == "Urlaub":
            self._calculate_vacation_duration()
    
    def _on_date_range_changed(self, start_date: QDate, end_date: QDate):
        """
        Wird aufgerufen wenn Datumsbereich geändert wird
        
        Args:
            start_date: Start-Datum
            end_date: End-Datum
        """
        self._filter_start_date = start_date
        self._filter_end_date = end_date
        self._refresh_entries_list()
    
    def _calculate_vacation_duration(self):
        """Berechnet und setzt Urlaubsdauer automatisch"""
        if self.type_combo.currentText() != "Urlaub":
            return
        
        # Worker-ID holen
        worker_id = self.worker_combo.currentData()
        if not worker_id:
            self.time_input.clear()
            self.time_preview.setText("")
            return
        
        # Datumsbereich
        start_date = self.date_edit.date()
        end_date = self.end_date_edit.date()
        
        # Validierung
        if end_date < start_date:
            self.time_preview.setText("⚠️ End-Datum muss >= Start-Datum sein")
            self.time_preview.setStyleSheet("color: red; font-style: italic;")
            self.time_input.clear()
            return
        
        # Regelarbeitszeit laden
        daily_hours = self._get_daily_hours_for_worker(worker_id)
        
        # Dauer berechnen
        duration_minutes = self._count_workdays(start_date, end_date) * daily_hours * 60
        
        # Werktage für Anzeige
        workdays = int(duration_minutes / (daily_hours * 60))
        
        # Dauer-Feld setzen
        hours = duration_minutes / 60.0
        self.time_input.setText(f"{hours}h")
        
        # Preview aktualisieren
        self.time_preview.setText(f"ℹ️ {workdays} Werktage × {daily_hours}h/Tag")
        self.time_preview.setStyleSheet("color: #666; font-style: italic;")
    
    def _count_workdays(self, start_date: QDate, end_date: QDate) -> int:
        """
        Zählt Werktage (Mo-Fr) zwischen zwei Daten
        
        Args:
            start_date: Start-Datum (inklusiv)
            end_date: End-Datum (inklusiv)
            
        Returns:
            Anzahl der Werktage
        """
        workdays = 0
        current = start_date
        
        while current <= end_date:
            # Qt dayOfWeek: 1=Montag, 7=Sonntag
            if current.dayOfWeek() <= 5:  # Mo-Fr
                workdays += 1
            current = current.addDays(1)
        
        return workdays
    
    def _get_daily_hours_for_worker(self, worker_id: int) -> float:
        """
        Lädt Regelarbeitszeit für Worker aus QSettings
        
        Args:
            worker_id: ID des Workers
            
        Returns:
            Regelarbeitszeit in Stunden (Standard: 8.0)
        """
        settings = QSettings("CapacityPlanner", "Settings")
        return settings.value(f"worker_{worker_id}_daily_hours", 8.0, type=float)
    
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
        # Worker-Auswahl NUR zurücksetzen wenn mehr als 1 Worker
        # Im Single-Worker-Mode bleibt die Auswahl erhalten
        if self.worker_combo.count() > 2:  # "Wähle Worker..." + mindestens 2 Worker
            self.worker_combo.setCurrentIndex(0)
        
        self.date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate())
        self.type_combo.setCurrentIndex(0)
        self.project_input.clearEditText()
        self.category_input.clear()
        self.time_input.clear()
        self.description_input.clear()
        self.status_label.setVisible(False)
        
        # End-Datum verstecken (wird bei Urlaub wieder angezeigt)
        self.end_date_edit.setVisible(False)
        self.end_date_label.setVisible(False)
        self.date_label.setText("Datum:")
        
        # Dauer-Feld wieder editierbar
        self.time_input.setReadOnly(False)
        self.time_input.setStyleSheet("")
        
        self.time_input.setFocus()
    
    def _refresh_entries_list(self):
        """Aktualisiert die Liste der Zeitbuchungen"""
        try:
            # Stopppe alle laufenden Timer vor dem Refresh
            self._stop_all_timers()
            
            # Verwende Filter-Datumsbereich
            start_date_str = self._filter_start_date.toString("yyyy-MM-dd")
            end_date_str = self._filter_end_date.toString("yyyy-MM-dd")
            
            entries = self.time_entry_repository.find_by_date_range(
                start_date_str,
                end_date_str
            )
            
            # Sortiere nach Datum absteigend
            entries.sort(key=lambda e: e.date, reverse=True)
            
            # Tabelle leeren
            self.entries_table.setRowCount(0)
            self.entries_table.setSortingEnabled(False)
            
            # Clear tracking dicts
            self._timer_widgets.clear()
            self._entry_row_map.clear()
            
            # Worker-Namen als Dict für schnellen Zugriff
            worker_names = {w.id: w.name for w in self._workers}
            
            # Signal temporär trennen für Bulk-Update
            self.entries_table.itemChanged.disconnect(self._on_table_item_changed)
            
            # Einträge in Tabelle einfügen
            for entry in entries:
                row = self.entries_table.rowCount()
                self.entries_table.insertRow(row)
                
                # Speichere Mapping
                self._entry_row_map[entry.id] = row
                
                # Datum (nicht editierbar)
                date_item = QTableWidgetItem(entry.date.strftime("%d.%m.%Y"))
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.entries_table.setItem(row, 0, date_item)
                
                # Worker (nicht editierbar)
                worker_name = worker_names.get(entry.worker_id, f"ID:{entry.worker_id}")
                worker_item = QTableWidgetItem(worker_name)
                worker_item.setFlags(worker_item.flags() & ~Qt.ItemIsEditable)
                self.entries_table.setItem(row, 1, worker_item)
                
                # Typ (aus Beschreibung extrahieren, nicht editierbar)
                entry_type = "Arbeit"
                description = entry.description
                if description.startswith("["):
                    end_bracket = description.find("]")
                    if end_bracket > 0:
                        entry_type = description[1:end_bracket]
                        description = description[end_bracket+1:].strip()
                
                type_item = QTableWidgetItem(entry_type)
                type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
                self.entries_table.setItem(row, 2, type_item)
                
                # Projekt und Kategorie (editierbar)
                project = entry.project or ""
                category = ""
                if " - " in project:
                    project, category = project.split(" - ", 1)
                
                project_item = QTableWidgetItem(project)
                project_item.setData(Qt.UserRole, entry.id)  # Speichere Entry-ID
                self.entries_table.setItem(row, 3, project_item)
                
                category_item = QTableWidgetItem(category)
                category_item.setData(Qt.UserRole, entry.id)
                self.entries_table.setItem(row, 4, category_item)
                
                # Beschreibung (editierbar)
                desc_item = QTableWidgetItem(description)
                desc_item.setData(Qt.UserRole, entry.id)
                self.entries_table.setItem(row, 5, desc_item)
                
                # Dauer (editierbar)
                hours = entry.duration_minutes / 60.0
                duration_str = f"{entry.duration_minutes}m ({hours:.2f}h)"
                duration_item = QTableWidgetItem(duration_str)
                duration_item.setData(Qt.UserRole, entry.id)
                duration_item.setData(Qt.UserRole + 1, entry.duration_minutes)  # Original-Minuten
                self.entries_table.setItem(row, 6, duration_item)
                
                # Timer Widget
                timer_widget = TimerWidget(entry.id, entry.duration_minutes)
                timer_widget.timer_stopped.connect(
                    lambda minutes, e_id=entry.id: self._on_timer_stopped(e_id, minutes)
                )
                self._timer_widgets[entry.id] = timer_widget
                self.entries_table.setCellWidget(row, 7, timer_widget)
                
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
                self.entries_table.setCellWidget(row, 8, delete_button)
            
            # Signal wieder verbinden
            self.entries_table.itemChanged.connect(self._on_table_item_changed)
            
            self.entries_table.setSortingEnabled(True)
            
        except Exception as e:
            self._show_status(f"Fehler beim Laden der Einträge: {str(e)}", "error")
    
    def _on_timer_stopped(self, entry_id: int, minutes: int):
        """
        Behandelt Timer-Stopp Event
        
        Args:
            entry_id: ID des TimeEntry
            minutes: Erfasste Minuten
        """
        try:
            # Lade Entry aus DB
            entry = self.time_entry_repository.find_by_id(entry_id)
            if not entry:
                self._show_status(f"Fehler: Entry {entry_id} nicht gefunden", "error")
                return
            
            # Update Dauer
            entry.duration_minutes = minutes
            entry.updated_at = datetime.now()
            
            # Speichere in DB
            success = self.time_entry_repository.update(entry)
            if success:
                # Update Tabellen-Zelle
                row = self._entry_row_map.get(entry_id)
                if row is not None:
                    hours = minutes / 60.0
                    duration_str = f"{minutes}m ({hours:.2f}h)"
                    
                    # Temporär Signal trennen für Update
                    self.entries_table.itemChanged.disconnect(self._on_table_item_changed)
                    
                    duration_item = self.entries_table.item(row, 6)
                    if duration_item:
                        duration_item.setText(duration_str)
                        duration_item.setData(Qt.UserRole + 1, minutes)
                    
                    # Signal wieder verbinden
                    self.entries_table.itemChanged.connect(self._on_table_item_changed)
                
                self._show_status(f"✓ Timer gestoppt: {minutes} Minuten erfasst", "success")
            else:
                self._show_status("Fehler beim Speichern der Dauer", "error")
                
        except Exception as e:
            self._show_status(f"Fehler beim Timer-Stopp: {str(e)}", "error")
    
    def _on_table_item_changed(self, item: QTableWidgetItem):
        """
        Behandelt Änderungen in der Tabelle
        
        Args:
            item: Geändertes Table Item
        """
        # Hole Entry-ID aus Item
        entry_id = item.data(Qt.UserRole)
        if not entry_id:
            return
        
        col = item.column()
        
        # Nur editierbare Spalten: Projekt (3), Kategorie (4), Beschreibung (5), Dauer (6)
        if col not in [3, 4, 5, 6]:
            return
        
        try:
            # Lade Entry aus DB
            entry = self.time_entry_repository.find_by_id(entry_id)
            if not entry:
                return
            
            new_value = item.text().strip()
            
            # Update entsprechende Eigenschaft
            if col == 3:  # Projekt
                # Kombiniere mit Kategorie
                row = item.row()
                category_item = self.entries_table.item(row, 4)
                category = category_item.text().strip() if category_item else ""
                
                if new_value and category:
                    entry.project = f"{new_value} - {category}"
                elif new_value:
                    entry.project = new_value
                elif category:
                    entry.project = f" - {category}"
                else:
                    entry.project = None
                    
            elif col == 4:  # Kategorie
                # Kombiniere mit Projekt
                row = item.row()
                project_item = self.entries_table.item(row, 3)
                project = project_item.text().strip() if project_item else ""
                
                if project and new_value:
                    entry.project = f"{project} - {new_value}"
                elif project:
                    entry.project = project
                elif new_value:
                    entry.project = f" - {new_value}"
                else:
                    entry.project = None
                    
            elif col == 5:  # Beschreibung
                # Prüfe ob Typ-Prefix vorhanden
                row = item.row()
                type_item = self.entries_table.item(row, 2)
                entry_type = type_item.text() if type_item else "Arbeit"
                
                if entry_type != "Arbeit":
                    entry.description = f"[{entry_type}] {new_value}"
                else:
                    entry.description = new_value
                    
            elif col == 6:  # Dauer
                # Parse Dauer-Eingabe
                parsed_minutes = self.viewmodel.parse_time_input(new_value)
                if parsed_minutes is not None:
                    entry.duration_minutes = parsed_minutes
                    
                    # Update Anzeige
                    hours = parsed_minutes / 60.0
                    item.setText(f"{parsed_minutes}m ({hours:.2f}h)")
                    item.setData(Qt.UserRole + 1, parsed_minutes)
                    
                    # Update Timer Widget
                    timer_widget = self._timer_widgets.get(entry_id)
                    if timer_widget:
                        # Nur updaten wenn Timer nicht läuft
                        if not timer_widget.is_timer_running():
                            timer_widget.accumulated_seconds = parsed_minutes * 60
                            timer_widget._update_display()
                else:
                    # Ungültige Eingabe - zurücksetzen
                    orig_minutes = item.data(Qt.UserRole + 1)
                    if orig_minutes:
                        hours = orig_minutes / 60.0
                        item.setText(f"{orig_minutes}m ({hours:.2f}h)")
                    self._show_status("Ungültige Dauer-Eingabe", "error")
                    return
            
            # Speichere in DB
            entry.updated_at = datetime.now()
            success = self.time_entry_repository.update(entry)
            
            if success:
                self._show_status("✓ Änderung gespeichert", "success")
            else:
                self._show_status("Fehler beim Speichern", "error")
                
        except Exception as e:
            self._show_status(f"Fehler beim Speichern: {str(e)}", "error")
    
    def _stop_all_timers(self):
        """Stoppt alle laufenden Timer"""
        for timer_widget in self._timer_widgets.values():
            timer_widget.stop_timer_if_running()
    
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
