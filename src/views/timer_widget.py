"""
Timer Widget für Zeiterfassung in der Tabelle

Bietet Start/Stop-Funktionalität mit Live-Anzeige der erfassten Zeit
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer, Signal, QTime
from PySide6.QtGui import QFont
from typing import Optional
from datetime import datetime, timedelta


class TimerWidget(QWidget):
    """
    Widget für Timer-Funktionalität in Zeiterfassungs-Tabelle
    
    Features:
    - Start/Stop Button
    - Live-Anzeige der laufenden Zeit
    - Speichert Start-Zeit und akkumulierte Zeit
    - Signal wenn Timer gestoppt wird
    
    Signals:
        timer_stopped: Emittiert wenn Timer gestoppt wird (mit Minuten)
        duration_changed: Emittiert bei jeder Sekunde (mit Minuten)
    """
    
    timer_stopped = Signal(int)  # Emittiert Minuten
    duration_changed = Signal(int)  # Emittiert Minuten
    
    def __init__(
        self, 
        entry_id: int,
        initial_minutes: int = 0,
        parent: Optional[QWidget] = None
    ):
        """
        Initialisiert TimerWidget
        
        Args:
            entry_id: ID des TimeEntry
            initial_minutes: Bereits erfasste Minuten
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.entry_id = entry_id
        self.initial_minutes = initial_minutes
        self.accumulated_seconds = initial_minutes * 60
        self.start_time: Optional[datetime] = None
        self.is_running = False
        
        # Timer für Updates (jede Sekunde)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt UI-Komponenten"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Zeit-Anzeige
        self.time_label = QLabel(self._format_time(self.accumulated_seconds))
        font = QFont()
        font.setFamily("Courier")  # Monospace für bessere Ausrichtung
        self.time_label.setFont(font)
        self.time_label.setMinimumWidth(80)
        layout.addWidget(self.time_label)
        
        # Start/Stop Button
        self.timer_button = QPushButton("▶")
        self.timer_button.setMaximumWidth(35)
        self.timer_button.setToolTip("Timer starten")
        self.timer_button.clicked.connect(self._toggle_timer)
        self._update_button_style()
        layout.addWidget(self.timer_button)
    
    def _toggle_timer(self):
        """Startet oder stoppt den Timer"""
        if self.is_running:
            self._stop_timer()
        else:
            self._start_timer()
    
    def _start_timer(self):
        """Startet den Timer"""
        self.is_running = True
        self.start_time = datetime.now()
        self.update_timer.start(1000)  # Update jede Sekunde
        
        self.timer_button.setText("■")
        self.timer_button.setToolTip("Timer stoppen")
        self._update_button_style()
    
    def _stop_timer(self):
        """Stoppt den Timer und emittiert Signal"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.update_timer.stop()
        
        # Berechne finale Zeit
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            self.accumulated_seconds += int(elapsed.total_seconds())
            self.start_time = None
        
        self.timer_button.setText("▶")
        self.timer_button.setToolTip("Timer starten")
        self._update_button_style()
        
        # Emittiere Signals
        minutes = self.get_total_minutes()
        self.timer_stopped.emit(minutes)
    
    def _update_display(self):
        """Aktualisiert die Zeit-Anzeige"""
        current_seconds = self._get_current_seconds()
        self.time_label.setText(self._format_time(current_seconds))
        
        # Emittiere duration_changed Signal
        minutes = current_seconds // 60
        self.duration_changed.emit(minutes)
    
    def _get_current_seconds(self) -> int:
        """Berechnet aktuelle Gesamt-Sekunden"""
        total = self.accumulated_seconds
        
        if self.is_running and self.start_time:
            elapsed = datetime.now() - self.start_time
            total += int(elapsed.total_seconds())
        
        return total
    
    def _format_time(self, seconds: int) -> str:
        """
        Formatiert Sekunden als HH:MM:SS
        
        Args:
            seconds: Sekunden
            
        Returns:
            Formatierter String
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _update_button_style(self):
        """Aktualisiert Button-Styling basierend auf Status"""
        if self.is_running:
            # Rot für Stop
            self.timer_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
        else:
            # Grün für Start
            self.timer_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
    
    def get_total_minutes(self) -> int:
        """
        Gibt die Gesamt-Minuten zurück
        
        Returns:
            Minuten (gerundet)
        """
        return self._get_current_seconds() // 60
    
    def is_timer_running(self) -> bool:
        """
        Prüft ob Timer läuft
        
        Returns:
            True wenn Timer läuft
        """
        return self.is_running
    
    def stop_timer_if_running(self):
        """Stoppt Timer falls er läuft"""
        if self.is_running:
            self._stop_timer()
