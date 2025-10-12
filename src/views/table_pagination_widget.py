"""
TablePaginationWidget - Wiederverwendbare Pagination-Komponente für QTableWidget
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox
from PySide6.QtCore import Signal, Qt


class TablePaginationWidget(QWidget):
    """
    Wiederverwendbare Pagination-Komponente für Tabellen-Widgets
    
    Features:
    - Vorherige/Nächste Seite Navigation
    - Seitenanzeige (z.B. "Seite 2 von 10")
    - Einstellbare Einträge pro Seite
    - Signal-Emission bei Änderungen
    
    Signals:
        page_changed(int): Wird emittiert wenn Seite sich ändert (neue Seitennummer)
        page_size_changed(int): Wird emittiert wenn Einträge pro Seite sich ändern
        
    Example:
        pagination = TablePaginationWidget()
        pagination.page_changed.connect(self._on_page_changed)
        pagination.page_size_changed.connect(self._on_page_size_changed)
        pagination.set_total_items(150)
    """
    
    page_changed = Signal(int)
    page_size_changed = Signal(int)
    
    def __init__(self, default_page_size: int = 25):
        """
        Initialisiert TablePaginationWidget
        
        Args:
            default_page_size: Standardanzahl Einträge pro Seite
        """
        super().__init__()
        self._current_page = 1
        self._total_items = 0
        self._page_size = default_page_size
        self._setup_ui()
        self._update_controls()
    
    def _setup_ui(self):
        """Erstellt das UI Layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        
        # Einträge pro Seite Label
        entries_label = QLabel("Einträge pro Seite:")
        layout.addWidget(entries_label)
        
        # Einträge pro Seite Dropdown
        self._page_size_combo = QComboBox()
        self._page_size_combo.addItems(["10", "25", "50", "100"])
        self._page_size_combo.setCurrentText(str(self._page_size))
        self._page_size_combo.currentTextChanged.connect(self._on_page_size_changed)
        self._page_size_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 60px;
            }
        """)
        layout.addWidget(self._page_size_combo)
        
        layout.addStretch()
        
        # Info-Label (z.B. "Zeige 1-25 von 150 Einträgen")
        self._info_label = QLabel()
        self._info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 10pt;
                padding: 5px;
            }
        """)
        layout.addWidget(self._info_label)
        
        layout.addStretch()
        
        # Navigation Buttons
        self._prev_button = QPushButton("◀ Zurück")
        self._prev_button.clicked.connect(self._on_prev_clicked)
        self._prev_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:disabled {
                color: #999;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self._prev_button)
        
        # Seiten-Info Label (z.B. "Seite 2 von 10")
        self._page_label = QLabel()
        self._page_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                padding: 5px 15px;
            }
        """)
        self._page_label.setAlignment(Qt.AlignCenter)
        self._page_label.setMinimumWidth(120)
        layout.addWidget(self._page_label)
        
        self._next_button = QPushButton("Weiter ▶")
        self._next_button.clicked.connect(self._on_next_clicked)
        self._next_button.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:disabled {
                color: #999;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(self._next_button)
    
    def _on_page_size_changed(self, text: str):
        """
        Wird aufgerufen wenn Einträge pro Seite sich ändern
        
        Args:
            text: Neue Seitengröße als String
        """
        try:
            new_size = int(text)
            if new_size != self._page_size:
                self._page_size = new_size
                # Zurück zu Seite 1 bei Änderung der Seitengröße
                self._current_page = 1
                self._update_controls()
                self.page_size_changed.emit(new_size)
                self.page_changed.emit(1)
        except ValueError:
            pass
    
    def _on_prev_clicked(self):
        """Vorherige Seite"""
        if self._current_page > 1:
            self._current_page -= 1
            self._update_controls()
            self.page_changed.emit(self._current_page)
    
    def _on_next_clicked(self):
        """Nächste Seite"""
        if self._current_page < self._get_total_pages():
            self._current_page += 1
            self._update_controls()
            self.page_changed.emit(self._current_page)
    
    def _get_total_pages(self) -> int:
        """
        Berechnet Gesamtanzahl Seiten
        
        Returns:
            int: Anzahl Seiten
        """
        if self._total_items == 0:
            return 1
        return (self._total_items + self._page_size - 1) // self._page_size
    
    def _update_controls(self):
        """Aktualisiert Button-States und Labels"""
        total_pages = self._get_total_pages()
        
        # Buttons aktivieren/deaktivieren
        self._prev_button.setEnabled(self._current_page > 1)
        self._next_button.setEnabled(self._current_page < total_pages)
        
        # Seiten-Label aktualisieren
        if self._total_items == 0:
            self._page_label.setText("Keine Einträge")
        else:
            self._page_label.setText(f"Seite {self._current_page} von {total_pages}")
        
        # Info-Label aktualisieren
        if self._total_items == 0:
            self._info_label.setText("")
        else:
            start = (self._current_page - 1) * self._page_size + 1
            end = min(self._current_page * self._page_size, self._total_items)
            self._info_label.setText(f"Zeige {start}-{end} von {self._total_items} Einträgen")
    
    def set_total_items(self, total: int):
        """
        Setzt Gesamtanzahl der Einträge
        
        Args:
            total: Gesamtanzahl Einträge
        """
        self._total_items = total
        
        # Wenn aktuelle Seite außerhalb des Bereichs, zurück zu Seite 1
        if self._current_page > self._get_total_pages():
            self._current_page = 1
        
        self._update_controls()
    
    def get_current_page(self) -> int:
        """
        Gibt aktuelle Seitennummer zurück
        
        Returns:
            int: Aktuelle Seite (1-basiert)
        """
        return self._current_page
    
    def get_page_size(self) -> int:
        """
        Gibt aktuelle Seitengröße zurück
        
        Returns:
            int: Anzahl Einträge pro Seite
        """
        return self._page_size
    
    def set_page_size(self, size: int):
        """
        Setzt Seitengröße programmatisch
        
        Args:
            size: Neue Seitengröße
        """
        self._page_size_combo.setCurrentText(str(size))
    
    def reset_to_first_page(self):
        """Setzt zurück auf erste Seite"""
        if self._current_page != 1:
            self._current_page = 1
            self._update_controls()
            self.page_changed.emit(1)
    
    def get_offset(self) -> int:
        """
        Berechnet Offset für Datenbankabfragen
        
        Returns:
            int: Start-Index für aktuelle Seite (0-basiert)
        """
        return (self._current_page - 1) * self._page_size
    
    def get_limit(self) -> int:
        """
        Gibt Limit für Datenbankabfragen zurück
        
        Returns:
            int: Anzahl zu ladender Einträge
        """
        return self._page_size
