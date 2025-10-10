"""
DateRangeWidget - Quick-Select Buttons + Custom Date Range Picker
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
    QButtonGroup, QDateEdit
)
from PySide6.QtCore import Signal, QDate


class DateRangeWidget(QWidget):
    """
    Widget für schnelle Datums-Bereichsauswahl mit vordefinierten Presets + Custom Range
    
    Features:
    - 8 vordefinierte Zeiträume (Heute, Diese Woche, Dieser Monat, etc.)
    - Custom Date Range Picker (Von - Bis)
    - Signal-Emission bei Auswahl
    - Visual Feedback für aktiven Preset (Checkable Buttons)
    
    Signals:
        date_range_changed(QDate, QDate): Wird emittiert wenn ein Preset/Custom Range gewählt wird
    """
    
    date_range_changed = Signal(QDate, QDate)
    
    def __init__(self):
        super().__init__()
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt das UI Layout mit Quick-Select Buttons + Custom Picker"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # === ROW 1: QUICK-SELECT BUTTONS ===
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(5)
        
        # Label
        label = QLabel("Schnellauswahl:")
        label.setStyleSheet("font-weight: bold;")
        preset_layout.addWidget(label)
        
        # Row 1: Standard Zeiträume
        self._today_btn = self._create_preset_button("Heute", self._select_today)
        preset_layout.addWidget(self._today_btn)
        
        self._week_btn = self._create_preset_button("Diese Woche", self._select_this_week)
        preset_layout.addWidget(self._week_btn)
        
        self._month_btn = self._create_preset_button("Dieser Monat", self._select_this_month)
        preset_layout.addWidget(self._month_btn)
        
        self._quarter_btn = self._create_preset_button("Dieses Quartal", self._select_this_quarter)
        preset_layout.addWidget(self._quarter_btn)
        
        self._year_btn = self._create_preset_button("Dieses Jahr", self._select_this_year)
        preset_layout.addWidget(self._year_btn)
        
        # Separator
        preset_layout.addSpacing(15)
        
        # Row 2: Letzte X Tage
        self._last_7_btn = self._create_preset_button("Letzte 7 Tage", self._select_last_7_days)
        preset_layout.addWidget(self._last_7_btn)
        
        self._last_30_btn = self._create_preset_button("Letzte 30 Tage", self._select_last_30_days)
        preset_layout.addWidget(self._last_30_btn)
        
        self._last_90_btn = self._create_preset_button("Letzte 90 Tage", self._select_last_90_days)
        preset_layout.addWidget(self._last_90_btn)
        
        preset_layout.addStretch()
        
        main_layout.addLayout(preset_layout)
        
        # === ROW 2: CUSTOM DATE RANGE PICKER ===
        custom_layout = QHBoxLayout()
        custom_layout.setSpacing(10)
        
        # Label
        custom_label = QLabel("Benutzerdefiniert:")
        custom_label.setStyleSheet("font-weight: bold;")
        custom_layout.addWidget(custom_label)
        
        # Von-Datum
        custom_layout.addWidget(QLabel("Von:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.start_date_edit.setMinimumWidth(120)
        custom_layout.addWidget(self.start_date_edit)
        
        # Bis-Datum
        custom_layout.addWidget(QLabel("Bis:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.end_date_edit.setMinimumWidth(120)
        custom_layout.addWidget(self.end_date_edit)
        
        # Anwenden-Button
        self.apply_custom_btn = QPushButton("Anwenden")
        self.apply_custom_btn.clicked.connect(self._apply_custom_range)
        self.apply_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        custom_layout.addWidget(self.apply_custom_btn)
        
        custom_layout.addStretch()
        
        main_layout.addLayout(custom_layout)
    
    def _create_preset_button(self, text: str, callback) -> QPushButton:
        """
        Erstellt einen Preset-Button
        
        Args:
            text: Button-Text
            callback: Funktion die beim Klick aufgerufen wird
            
        Returns:
            QPushButton: Konfigurierter Button
        """
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.clicked.connect(callback)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #000000;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                color: #000000;
                border: 1px solid #b0b0b0;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                font-weight: bold;
            }
            QPushButton:pressed {
                background-color: #45a049;
                color: white;
            }
        """)
        self._button_group.addButton(btn)
        return btn
    
    def _select_today(self):
        """Setzt Datumsbereich auf Heute"""
        today = QDate.currentDate()
        self.date_range_changed.emit(today, today)
    
    def _select_this_week(self):
        """Setzt Datumsbereich auf Diese Woche (Montag bis Heute)"""
        today = QDate.currentDate()
        # Qt dayOfWeek: 1=Montag, 7=Sonntag
        days_since_monday = today.dayOfWeek() - 1
        monday = today.addDays(-days_since_monday)
        self.date_range_changed.emit(monday, today)
    
    def _select_this_month(self):
        """Setzt Datumsbereich auf Diesen Monat"""
        today = QDate.currentDate()
        first_day = QDate(today.year(), today.month(), 1)
        last_day = QDate(today.year(), today.month(), today.daysInMonth())
        self.date_range_changed.emit(first_day, last_day)
    
    def _select_this_quarter(self):
        """Setzt Datumsbereich auf Dieses Quartal (Q1-Q4)"""
        today = QDate.currentDate()
        month = today.month()
        
        # Q1: Jan-März (1-3), Q2: Apr-Jun (4-6), Q3: Jul-Sep (7-9), Q4: Okt-Dez (10-12)
        quarter_start_month = ((month - 1) // 3) * 3 + 1
        quarter_end_month = quarter_start_month + 2
        
        start = QDate(today.year(), quarter_start_month, 1)
        end = QDate(today.year(), quarter_end_month, 
                   QDate(today.year(), quarter_end_month, 1).daysInMonth())
        
        self.date_range_changed.emit(start, end)
    
    def _select_this_year(self):
        """Setzt Datumsbereich auf Dieses Jahr"""
        today = QDate.currentDate()
        start = QDate(today.year(), 1, 1)
        end = QDate(today.year(), 12, 31)
        self.date_range_changed.emit(start, end)
    
    def _select_last_7_days(self):
        """Setzt Datumsbereich auf Letzte 7 Tage"""
        today = QDate.currentDate()
        start = today.addDays(-7)
        self.date_range_changed.emit(start, today)
    
    def _select_last_30_days(self):
        """Setzt Datumsbereich auf Letzte 30 Tage"""
        today = QDate.currentDate()
        start = today.addDays(-30)
        self.date_range_changed.emit(start, today)
    
    def _select_last_90_days(self):
        """Setzt Datumsbereich auf Letzte 90 Tage"""
        today = QDate.currentDate()
        start = today.addDays(-90)
        self.date_range_changed.emit(start, today)
    
    def _apply_custom_range(self):
        """Wendet benutzerdefinierten Datumsbereich an"""
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        
        # Validierung: Start-Datum muss vor oder gleich End-Datum sein
        if start_date > end_date:
            # Automatisches Tauschen der Daten
            start_date, end_date = end_date, start_date
            self.start_date_edit.setDate(start_date)
            self.end_date_edit.setDate(end_date)
        
        # Preset-Buttons deaktivieren
        self.reset()
        
        # Signal mit benutzerdefiniertem Bereich aussenden
        self.date_range_changed.emit(start_date, end_date)
    
    def reset(self):
        """Entfernt Auswahl aller Preset-Buttons"""
        checked_button = self._button_group.checkedButton()
        if checked_button:
            self._button_group.setExclusive(False)
            checked_button.setChecked(False)
            self._button_group.setExclusive(True)
