"""
Unit Tests für DateRangeWidget
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDate
from pytestqt.qtbot import QtBot

from src.views.date_range_widget import DateRangeWidget


@pytest.fixture(scope="module")
def qapp():
    """Qt Application für GUI-Tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestDateRangeWidget:
    """Tests für DateRangeWidget Komponente"""
    
    def test_widget_creation(self, qapp):
        """Widget kann erstellt werden"""
        widget = DateRangeWidget()
        assert widget is not None
    
    def test_all_buttons_exist(self, qapp):
        """Alle 8 Preset-Buttons sind vorhanden"""
        widget = DateRangeWidget()
        
        assert widget._today_btn is not None
        assert widget._week_btn is not None
        assert widget._month_btn is not None
        assert widget._quarter_btn is not None
        assert widget._year_btn is not None
        assert widget._last_7_btn is not None
        assert widget._last_30_btn is not None
        assert widget._last_90_btn is not None
    
    def test_today_preset(self, qapp, qtbot: QtBot):
        """Heute-Button setzt korrektes Datum"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._today_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        assert start == today
        assert end == today
    
    def test_this_week_preset(self, qapp, qtbot: QtBot):
        """Diese-Woche-Button berechnet Montag-Heute korrekt"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._week_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        # Montag berechnen (Qt dayOfWeek: 1=Montag, 7=Sonntag)
        days_since_monday = today.dayOfWeek() - 1
        expected_start = today.addDays(-days_since_monday)
        
        assert start == expected_start
        assert end == today
    
    def test_this_month_preset(self, qapp, qtbot: QtBot):
        """Dieser-Monat-Button berechnet korrekt"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._month_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        expected_start = QDate(today.year(), today.month(), 1)
        expected_end = QDate(today.year(), today.month(), today.daysInMonth())
        
        assert start == expected_start
        assert end == expected_end
    
    def test_this_quarter_preset(self, qapp, qtbot: QtBot):
        """Dieses-Quartal-Button berechnet Q1-Q4 korrekt"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._quarter_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        month = today.month()
        
        # Q1: Jan-März (1-3), Q2: Apr-Jun (4-6), Q3: Jul-Sep (7-9), Q4: Okt-Dez (10-12)
        quarter_start_month = ((month - 1) // 3) * 3 + 1
        quarter_end_month = quarter_start_month + 2
        
        expected_start = QDate(today.year(), quarter_start_month, 1)
        expected_end = QDate(today.year(), quarter_end_month,
                           QDate(today.year(), quarter_end_month, 1).daysInMonth())
        
        assert start == expected_start
        assert end == expected_end
    
    def test_this_year_preset(self, qapp, qtbot: QtBot):
        """Dieses-Jahr-Button setzt 1.Jan bis 31.Dez"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._year_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        expected_start = QDate(today.year(), 1, 1)
        expected_end = QDate(today.year(), 12, 31)
        
        assert start == expected_start
        assert end == expected_end
    
    def test_last_7_days_preset(self, qapp, qtbot: QtBot):
        """Letzte-7-Tage berechnet korrekt"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._last_7_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        assert end == today
        assert start == today.addDays(-7)
    
    def test_last_30_days_preset(self, qapp, qtbot: QtBot):
        """Letzte-30-Tage berechnet korrekt"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._last_30_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        assert end == today
        assert start == today.addDays(-30)
    
    def test_last_90_days_preset(self, qapp, qtbot: QtBot):
        """Letzte-90-Tage berechnet korrekt"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._last_90_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        assert end == today
        assert start == today.addDays(-90)
    
    def test_button_checkable(self, qapp, qtbot: QtBot):
        """Buttons sind checkable für visual feedback"""
        widget = DateRangeWidget()
        
        assert widget._today_btn.isCheckable()
        assert widget._week_btn.isCheckable()
        assert widget._month_btn.isCheckable()
    
    def test_button_exclusive(self, qapp, qtbot: QtBot):
        """Nur ein Button kann gleichzeitig checked sein"""
        widget = DateRangeWidget()
        
        # Click Heute
        widget._today_btn.click()
        assert widget._today_btn.isChecked()
        
        # Click Woche -> Heute sollte unchecked sein
        widget._week_btn.click()
        assert widget._week_btn.isChecked()
        assert not widget._today_btn.isChecked()
    
    def test_reset_clears_selection(self, qapp):
        """reset() entfernt alle Button-Auswahlen"""
        widget = DateRangeWidget()
        
        widget._today_btn.click()
        assert widget._today_btn.isChecked()
        
        widget.reset()
        assert not widget._today_btn.isChecked()
        assert not widget._week_btn.isChecked()
        assert not widget._month_btn.isChecked()


class TestDateRangeWidgetEdgeCases:
    """Edge Case Tests für DateRangeWidget"""
    
    def test_week_on_monday(self, qapp, qtbot: QtBot):
        """Diese-Woche funktioniert korrekt wenn heute Montag ist"""
        widget = DateRangeWidget()
        
        # Simuliere Montag-Logik
        today = QDate.currentDate()
        if today.dayOfWeek() == 1:  # Wenn heute Montag
            with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
                widget._week_btn.click()
            
            start, end = blocker.args
            assert start == today  # Montag = Montag
            assert end == today
    
    def test_month_at_month_end(self, qapp, qtbot: QtBot):
        """Dieser-Monat funktioniert am Monatsende korrekt"""
        widget = DateRangeWidget()
        
        with qtbot.waitSignal(widget.date_range_changed, timeout=1000) as blocker:
            widget._month_btn.click()
        
        start, end = blocker.args
        
        # Start sollte immer 1. des Monats sein
        assert start.day() == 1
        
        # End sollte letzter Tag des Monats sein
        assert end.day() == end.daysInMonth()
