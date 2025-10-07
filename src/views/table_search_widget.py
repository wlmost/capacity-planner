"""
TableSearchWidget - Wiederverwendbare Such-Komponente für QTableWidget
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Signal


class TableSearchWidget(QWidget):
    """
    Wiederverwendbare Such-Komponente für Tabellen-Widgets
    
    Features:
    - Live-Suche während Tippen
    - Built-in Clear-Button (X)
    - Treffer-Anzeige
    - Signal-Emission bei Textänderung
    
    Signals:
        search_changed(str): Wird emittiert wenn Suchtext sich ändert
        
    Example:
        search_widget = TableSearchWidget("🔍 Worker oder Team suchen...")
        search_widget.search_changed.connect(self._on_search)
        
        def _on_search(self, text):
            # Filter table based on text
            pass
    """
    
    search_changed = Signal(str)
    
    def __init__(self, placeholder: str = "🔍 Suchen..."):
        """
        Initialisiert das Such-Widget
        
        Args:
            placeholder: Platzhalter-Text für Sucheingabe
        """
        super().__init__()
        self._placeholder = placeholder
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt das UI Layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Such-Eingabefeld mit Clear-Button
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._placeholder)
        self._search_input.setClearButtonEnabled(True)  # Built-in X-Button
        self._search_input.textChanged.connect(self._on_text_changed)
        self._search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 11pt;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        layout.addWidget(self._search_input)
        
        # Treffer-Anzeige Label
        self._result_label = QLabel("")
        self._result_label.setStyleSheet("""
            QLabel {
                color: grey;
                font-size: 10pt;
                padding: 5px;
            }
        """)
        layout.addWidget(self._result_label)
        
        layout.addStretch()
    
    def _on_text_changed(self, text: str):
        """
        Handler für Textänderungen im Suchfeld
        
        Emittiert search_changed Signal mit aktuellem Text.
        
        Args:
            text: Aktueller Suchtext
        """
        self.search_changed.emit(text)
    
    def set_result_count(self, count: int, total: int):
        """
        Aktualisiert die Treffer-Anzeige
        
        Args:
            count: Anzahl sichtbarer/gefundener Einträge
            total: Gesamtanzahl Einträge
        """
        search_text = self._search_input.text()
        
        if not search_text:
            # Keine aktive Suche
            if total == 0:
                self._result_label.setText("")
            else:
                self._result_label.setText(f"{total} Einträge")
                self._result_label.setStyleSheet("""
                    QLabel {
                        color: grey;
                        font-size: 10pt;
                        padding: 5px;
                    }
                """)
        elif count == 0:
            # Keine Treffer
            self._result_label.setText("Keine Treffer")
            self._result_label.setStyleSheet("""
                QLabel {
                    color: #f44336;
                    font-size: 10pt;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
        elif count == total:
            # Alle Einträge passen
            self._result_label.setText(f"{total} Einträge")
            self._result_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 10pt;
                    padding: 5px;
                }
            """)
        else:
            # Gefilterte Treffer
            self._result_label.setText(f"{count} von {total} Treffern")
            self._result_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 10pt;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
    
    def clear(self):
        """Löscht den Suchtext"""
        self._search_input.clear()
    
    def get_search_text(self) -> str:
        """
        Gibt den aktuellen Suchtext zurück
        
        Returns:
            str: Aktueller Suchtext
        """
        return self._search_input.text()
    
    def set_focus(self):
        """Setzt den Fokus auf das Suchfeld"""
        self._search_input.setFocus()
