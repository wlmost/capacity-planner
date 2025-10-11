"""
Unit Tests für TimerWidget
"""
import pytest
from unittest.mock import Mock
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import QTimer
import time

from src.views.timer_widget import TimerWidget


@pytest.fixture(scope="module")
def qapp():
    """Qt Application für GUI-Tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def timer_widget(qapp):
    """TimerWidget Instanz"""
    widget = TimerWidget(entry_id=1, initial_minutes=0)
    yield widget
    # Cleanup
    if widget.is_running:
        widget._stop_timer()


class TestTimerWidgetInitialization:
    """Tests für Timer-Widget Initialisierung"""
    
    def test_initialization_with_zero_minutes(self, qapp):
        """Timer startet mit 0 Minuten"""
        widget = TimerWidget(entry_id=1, initial_minutes=0)
        
        assert widget.entry_id == 1
        assert widget.initial_minutes == 0
        assert widget.accumulated_seconds == 0
        assert not widget.is_running
        assert widget.get_total_minutes() == 0
    
    def test_initialization_with_existing_minutes(self, qapp):
        """Timer startet mit vorhandenen Minuten"""
        widget = TimerWidget(entry_id=2, initial_minutes=45)
        
        assert widget.entry_id == 2
        assert widget.initial_minutes == 45
        assert widget.accumulated_seconds == 45 * 60
        assert not widget.is_running
        assert widget.get_total_minutes() == 45
    
    def test_initial_display_shows_correct_time(self, qapp):
        """Zeit-Anzeige zeigt korrekte initiale Zeit"""
        widget = TimerWidget(entry_id=1, initial_minutes=90)
        
        # 90 Minuten = 1 Stunde 30 Minuten
        assert "01:30:00" in widget.time_label.text()
    
    def test_button_starts_with_play_icon(self, timer_widget):
        """Button zeigt initial Play-Icon"""
        assert timer_widget.timer_button.text() == "▶"


class TestTimerStartStop:
    """Tests für Timer Start/Stop Funktionalität"""
    
    def test_start_timer_changes_button_to_stop(self, timer_widget):
        """Timer-Start ändert Button zu Stop"""
        timer_widget._start_timer()
        
        assert timer_widget.is_running
        assert timer_widget.timer_button.text() == "■"
        assert timer_widget.start_time is not None
        
        # Cleanup
        timer_widget._stop_timer()
    
    def test_stop_timer_changes_button_to_play(self, timer_widget):
        """Timer-Stop ändert Button zu Play"""
        timer_widget._start_timer()
        QTest.qWait(100)  # Warte kurz
        timer_widget._stop_timer()
        
        assert not timer_widget.is_running
        assert timer_widget.timer_button.text() == "▶"
        assert timer_widget.start_time is None
    
    def test_toggle_timer_starts_when_stopped(self, timer_widget):
        """Toggle startet Timer wenn gestoppt"""
        assert not timer_widget.is_running
        
        timer_widget._toggle_timer()
        
        assert timer_widget.is_running
        
        # Cleanup
        timer_widget._stop_timer()
    
    def test_toggle_timer_stops_when_running(self, timer_widget):
        """Toggle stoppt Timer wenn läuft"""
        timer_widget._start_timer()
        assert timer_widget.is_running
        
        timer_widget._toggle_timer()
        
        assert not timer_widget.is_running
    
    def test_timer_stopped_signal_emitted(self, timer_widget):
        """timer_stopped Signal wird emittiert"""
        signal_received = []
        timer_widget.timer_stopped.connect(lambda m: signal_received.append(m))
        
        timer_widget._start_timer()
        QTest.qWait(1100)  # Warte 1+ Sekunde
        timer_widget._stop_timer()
        
        assert len(signal_received) == 1
        assert signal_received[0] >= 0  # Mindestens 0 Minuten


class TestTimerTimeCalculation:
    """Tests für Zeit-Berechnung"""
    
    def test_format_time_zero_seconds(self, timer_widget):
        """Formatiert 0 Sekunden korrekt"""
        result = timer_widget._format_time(0)
        assert result == "00:00:00"
    
    def test_format_time_one_minute(self, timer_widget):
        """Formatiert 1 Minute korrekt"""
        result = timer_widget._format_time(60)
        assert result == "00:01:00"
    
    def test_format_time_one_hour(self, timer_widget):
        """Formatiert 1 Stunde korrekt"""
        result = timer_widget._format_time(3600)
        assert result == "01:00:00"
    
    def test_format_time_complex(self, timer_widget):
        """Formatiert komplexe Zeit korrekt"""
        # 2 Stunden, 34 Minuten, 56 Sekunden
        result = timer_widget._format_time(2 * 3600 + 34 * 60 + 56)
        assert result == "02:34:56"
    
    def test_get_total_minutes_when_stopped(self, qapp):
        """get_total_minutes gibt korrekte Minuten wenn gestoppt"""
        widget = TimerWidget(entry_id=1, initial_minutes=30)
        
        assert widget.get_total_minutes() == 30
    
    def test_accumulated_time_persists_after_stop(self, timer_widget):
        """Zeit akkumuliert über mehrere Start/Stop-Zyklen"""
        # Erster Zyklus
        timer_widget._start_timer()
        QTest.qWait(1100)
        timer_widget._stop_timer()
        
        first_time = timer_widget.get_total_minutes()
        
        # Zweiter Zyklus
        timer_widget._start_timer()
        QTest.qWait(1100)
        timer_widget._stop_timer()
        
        second_time = timer_widget.get_total_minutes()
        
        # Zweite Zeit sollte größer sein
        assert second_time >= first_time


class TestTimerDisplay:
    """Tests für Timer-Anzeige Updates"""
    
    def test_display_updates_when_timer_runs(self, timer_widget):
        """Display wird aktualisiert während Timer läuft"""
        initial_text = timer_widget.time_label.text()
        
        timer_widget._start_timer()
        QTest.qWait(1100)  # Warte 1+ Sekunde
        
        updated_text = timer_widget.time_label.text()
        timer_widget._stop_timer()
        
        # Text sollte sich geändert haben
        assert updated_text != initial_text
    
    def test_update_display_method(self, timer_widget):
        """_update_display() aktualisiert Label"""
        timer_widget.accumulated_seconds = 125  # 2:05
        timer_widget._update_display()
        
        assert "00:02:05" in timer_widget.time_label.text()


class TestTimerHelpers:
    """Tests für Hilfsmethoden"""
    
    def test_is_timer_running_false_initially(self, timer_widget):
        """is_timer_running() gibt False initial"""
        assert not timer_widget.is_timer_running()
    
    def test_is_timer_running_true_when_started(self, timer_widget):
        """is_timer_running() gibt True wenn gestartet"""
        timer_widget._start_timer()
        
        assert timer_widget.is_timer_running()
        
        timer_widget._stop_timer()
    
    def test_stop_timer_if_running_stops_timer(self, timer_widget):
        """stop_timer_if_running() stoppt laufenden Timer"""
        timer_widget._start_timer()
        assert timer_widget.is_running
        
        timer_widget.stop_timer_if_running()
        
        assert not timer_widget.is_running
    
    def test_stop_timer_if_running_does_nothing_when_stopped(self, timer_widget):
        """stop_timer_if_running() tut nichts wenn bereits gestoppt"""
        assert not timer_widget.is_running
        
        # Sollte keine Exception werfen
        timer_widget.stop_timer_if_running()
        
        assert not timer_widget.is_running


class TestTimerSignals:
    """Tests für Timer-Signals"""
    
    def test_duration_changed_signal_emitted_periodically(self, timer_widget):
        """duration_changed Signal wird periodisch emittiert"""
        signals_received = []
        timer_widget.duration_changed.connect(lambda m: signals_received.append(m))
        
        timer_widget._start_timer()
        QTest.qWait(2100)  # Warte 2+ Sekunden
        timer_widget._stop_timer()
        
        # Sollte mindestens 2 Signale empfangen haben
        assert len(signals_received) >= 2
