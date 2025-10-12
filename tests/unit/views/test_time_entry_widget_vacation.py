"""
Unit Tests für TimeEntryWidget - Urlaubs-Datumsbereich Feature
"""
import pytest
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDate, QSettings
from pytestqt.qtbot import QtBot

from src.views.time_entry_widget import TimeEntryWidget
from src.viewmodels.time_entry_viewmodel import TimeEntryViewModel
from src.repositories.time_entry_repository import TimeEntryRepository


@pytest.fixture(scope="module")
def qapp():
    """Qt Application für GUI-Tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_viewmodel():
    """Mock TimeEntryViewModel"""
    vm = Mock(spec=TimeEntryViewModel)
    vm.entry_created = Mock()
    vm.entry_created.connect = Mock()
    vm.validation_failed = Mock()
    vm.validation_failed.connect = Mock()
    vm.error_occurred = Mock()
    vm.error_occurred.connect = Mock()
    vm.parse_time_input = Mock(return_value=480)  # 8 Stunden
    vm.format_duration = Mock(return_value="08:00")
    return vm


@pytest.fixture
def mock_repository():
    """Mock TimeEntryRepository"""
    repo = Mock(spec=TimeEntryRepository)
    repo.find_by_date_range = Mock(return_value=[])
    return repo


@pytest.fixture
def widget(qapp, mock_viewmodel, mock_repository):
    """TimeEntryWidget Instanz"""
    widget = TimeEntryWidget(mock_viewmodel, mock_repository)
    
    # Worker für Tests hinzufügen
    mock_worker = Mock()
    mock_worker.id = 1
    mock_worker.name = "Test Worker"
    mock_worker.active = True
    widget.load_workers([mock_worker])
    
    # Worker auswählen (Index 1, da Index 0 ist "Wähle Worker...")
    widget.worker_combo.setCurrentIndex(1)
    
    # Settings für Tests setzen
    settings = QSettings("CapacityPlanner", "Settings")
    settings.setValue("worker_1_daily_hours", 8.0)
    
    yield widget
    
    # Cleanup
    settings.remove("worker_1_daily_hours")


class TestVacationUIVisibility:
    """Tests für UI-Sichtbarkeits-Logik bei Urlaub"""
    
    def test_end_date_hidden_by_default(self, widget):
        """End-Datum ist initial versteckt"""
        assert not widget.end_date_edit.isVisible()
        assert not widget.end_date_label.isVisible()
    
    def test_end_date_visible_when_vacation_selected(self, widget):
        """End-Datum wird bei Urlaub angezeigt"""
        widget.type_combo.setCurrentText("Urlaub")
        
        assert widget.end_date_edit.isVisible()
        assert widget.end_date_label.isVisible()
    
    def test_end_date_hidden_when_work_selected(self, widget):
        """End-Datum wird bei Arbeit versteckt"""
        # Erst Urlaub auswählen
        widget.type_combo.setCurrentText("Urlaub")
        assert widget.end_date_edit.isVisible()
        
        # Dann zurück zu Arbeit
        widget.type_combo.setCurrentText("Arbeit")
        assert not widget.end_date_edit.isVisible()
        assert not widget.end_date_label.isVisible()
    
    def test_end_date_hidden_when_absence_selected(self, widget):
        """End-Datum wird bei Abwesenheit versteckt"""
        widget.type_combo.setCurrentText("Abwesenheit")
        
        assert not widget.end_date_edit.isVisible()
        assert not widget.end_date_label.isVisible()
    
    def test_date_label_changes_when_vacation(self, widget):
        """Datum-Label ändert sich zu 'Datum (Von):' bei Urlaub"""
        widget.type_combo.setCurrentText("Urlaub")
        assert widget.date_label.text() == "Datum (Von):"
    
    def test_date_label_resets_when_work(self, widget):
        """Datum-Label wird zurückgesetzt bei Arbeit"""
        widget.type_combo.setCurrentText("Urlaub")
        widget.type_combo.setCurrentText("Arbeit")
        
        assert widget.date_label.text() == "Datum:"
    
    def test_time_input_readonly_when_vacation(self, widget):
        """Dauer-Feld ist readonly bei Urlaub"""
        widget.type_combo.setCurrentText("Urlaub")
        
        assert widget.time_input.isReadOnly()
    
    def test_time_input_editable_when_work(self, widget):
        """Dauer-Feld ist editierbar bei Arbeit"""
        widget.type_combo.setCurrentText("Arbeit")
        
        assert not widget.time_input.isReadOnly()


class TestVacationDurationCalculation:
    """Tests für automatische Dauer-Berechnung bei Urlaub"""
    
    def test_vacation_duration_single_weekday(self, widget):
        """Einzelner Werktag wird korrekt berechnet"""
        widget.type_combo.setCurrentText("Urlaub")
        
        # Montag, 6. Januar 2025
        widget.date_edit.setDate(QDate(2025, 1, 6))
        widget.end_date_edit.setDate(QDate(2025, 1, 6))
        
        # Sollte 8h sein
        assert widget.time_input.text() == "8.0h"
        assert "1 Werktage × 8.0h/Tag" in widget.time_preview.text()
    
    def test_vacation_duration_full_week(self, widget):
        """Ganze Woche (Mo-Fr) wird korrekt berechnet"""
        widget.type_combo.setCurrentText("Urlaub")
        
        # Montag - Freitag
        widget.date_edit.setDate(QDate(2025, 1, 6))   # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 10))  # Freitag
        
        # Sollte 5 Werktage × 8h = 40h sein
        assert widget.time_input.text() == "40.0h"
        assert "5 Werktage × 8.0h/Tag" in widget.time_preview.text()
    
    def test_vacation_duration_two_weeks(self, widget):
        """Zwei Wochen werden korrekt berechnet"""
        widget.type_combo.setCurrentText("Urlaub")
        
        # 2 Wochen = 10 Werktage
        widget.date_edit.setDate(QDate(2025, 1, 6))   # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 17))  # Freitag (2 Wochen später)
        
        # Sollte 10 Werktage × 8h = 80h sein
        assert widget.time_input.text() == "80.0h"
        assert "10 Werktage × 8.0h/Tag" in widget.time_preview.text()
    
    def test_vacation_duration_with_weekend(self, widget):
        """Wochenende wird nicht mitgezählt"""
        widget.type_combo.setCurrentText("Urlaub")
        
        # Montag - Sonntag (7 Tage, aber nur 5 Werktage)
        widget.date_edit.setDate(QDate(2025, 1, 6))   # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 12))  # Sonntag
        
        # Sollte nur 5 Werktage × 8h = 40h sein
        assert widget.time_input.text() == "40.0h"
        assert "5 Werktage × 8.0h/Tag" in widget.time_preview.text()
    
    def test_vacation_duration_weekend_only(self, widget):
        """Nur Wochenende = 0 Werktage"""
        widget.type_combo.setCurrentText("Urlaub")
        
        # Samstag - Sonntag
        widget.date_edit.setDate(QDate(2025, 1, 11))  # Samstag
        widget.end_date_edit.setDate(QDate(2025, 1, 12))  # Sonntag
        
        # Sollte 0 Werktage × 8h = 0h sein
        assert widget.time_input.text() == "0.0h"
        assert "0 Werktage × 8.0h/Tag" in widget.time_preview.text()
    
    def test_vacation_duration_custom_daily_hours(self, widget):
        """Individuelle Regelarbeitszeit wird verwendet"""
        # Regelarbeitszeit auf 7.5h setzen
        settings = QSettings("CapacityPlanner", "Settings")
        settings.setValue("worker_1_daily_hours", 7.5)
        
        widget.type_combo.setCurrentText("Urlaub")
        
        # 5 Werktage
        widget.date_edit.setDate(QDate(2025, 1, 6))   # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 10))  # Freitag
        
        # Sollte 5 Werktage × 7.5h = 37.5h sein
        assert widget.time_input.text() == "37.5h"
        assert "5 Werktage × 7.5h/Tag" in widget.time_preview.text()
        
        # Cleanup
        settings.setValue("worker_1_daily_hours", 8.0)


class TestVacationValidation:
    """Tests für Validierung bei Urlaub"""
    
    def test_validation_end_before_start(self, widget):
        """Validierung: End-Datum < Start-Datum"""
        widget.type_combo.setCurrentText("Urlaub")
        
        # End-Datum vor Start-Datum
        widget.date_edit.setDate(QDate(2025, 1, 10))
        widget.end_date_edit.setDate(QDate(2025, 1, 6))
        
        # Sollte Fehlermeldung anzeigen
        assert "End-Datum muss >= Start-Datum sein" in widget.time_preview.text()
        assert widget.time_input.text() == ""
    
    def test_validation_end_equals_start(self, widget):
        """End-Datum = Start-Datum ist gültig"""
        widget.type_combo.setCurrentText("Urlaub")
        
        # Beide Daten gleich
        widget.date_edit.setDate(QDate(2025, 1, 6))
        widget.end_date_edit.setDate(QDate(2025, 1, 6))
        
        # Sollte gültig sein (1 Tag)
        assert "8.0h" in widget.time_input.text()
    
    def test_validation_no_worker_selected(self, widget):
        """Keine Berechnung wenn kein Worker ausgewählt"""
        widget.worker_combo.setCurrentIndex(0)  # "Wähle Worker..."
        widget.type_combo.setCurrentText("Urlaub")
        
        widget.date_edit.setDate(QDate(2025, 1, 6))
        widget.end_date_edit.setDate(QDate(2025, 1, 10))
        
        # Sollte leer bleiben
        assert widget.time_input.text() == ""
        assert widget.time_preview.text() == ""


class TestVacationFormReset:
    """Tests für Formular-Reset bei Urlaub"""
    
    def test_clear_form_hides_end_date(self, widget):
        """Formular-Reset versteckt End-Datum"""
        widget.type_combo.setCurrentText("Urlaub")
        assert widget.end_date_edit.isVisible()
        
        widget._clear_form()
        
        assert not widget.end_date_edit.isVisible()
        assert not widget.end_date_label.isVisible()
    
    def test_clear_form_resets_date_label(self, widget):
        """Formular-Reset setzt Datum-Label zurück"""
        widget.type_combo.setCurrentText("Urlaub")
        assert widget.date_label.text() == "Datum (Von):"
        
        widget._clear_form()
        
        assert widget.date_label.text() == "Datum:"
    
    def test_clear_form_makes_time_input_editable(self, widget):
        """Formular-Reset macht Dauer-Feld wieder editierbar"""
        widget.type_combo.setCurrentText("Urlaub")
        assert widget.time_input.isReadOnly()
        
        widget._clear_form()
        
        assert not widget.time_input.isReadOnly()
    
    def test_clear_form_resets_type_to_work(self, widget):
        """Formular-Reset setzt Typ auf Arbeit"""
        widget.type_combo.setCurrentText("Urlaub")
        
        widget._clear_form()
        
        assert widget.type_combo.currentText() == "Arbeit"


class TestWorkdaysCalculation:
    """Tests für Werktage-Berechnung (interne Hilfsmethode)"""
    
    def test_count_workdays_single_monday(self, widget):
        """Einzelner Montag = 1 Werktag"""
        workdays = widget._count_workdays(
            QDate(2025, 1, 6),   # Montag
            QDate(2025, 1, 6)    # Montag
        )
        assert workdays == 1
    
    def test_count_workdays_single_friday(self, widget):
        """Einzelner Freitag = 1 Werktag"""
        workdays = widget._count_workdays(
            QDate(2025, 1, 10),  # Freitag
            QDate(2025, 1, 10)   # Freitag
        )
        assert workdays == 1
    
    def test_count_workdays_single_saturday(self, widget):
        """Einzelner Samstag = 0 Werktage"""
        workdays = widget._count_workdays(
            QDate(2025, 1, 11),  # Samstag
            QDate(2025, 1, 11)   # Samstag
        )
        assert workdays == 0
    
    def test_count_workdays_single_sunday(self, widget):
        """Einzelner Sonntag = 0 Werktage"""
        workdays = widget._count_workdays(
            QDate(2025, 1, 12),  # Sonntag
            QDate(2025, 1, 12)   # Sonntag
        )
        assert workdays == 0
    
    def test_count_workdays_monday_to_friday(self, widget):
        """Montag bis Freitag = 5 Werktage"""
        workdays = widget._count_workdays(
            QDate(2025, 1, 6),   # Montag
            QDate(2025, 1, 10)   # Freitag
        )
        assert workdays == 5
    
    def test_count_workdays_friday_to_monday(self, widget):
        """Freitag bis Montag = 2 Werktage (Fr + Mo)"""
        workdays = widget._count_workdays(
            QDate(2025, 1, 10),  # Freitag
            QDate(2025, 1, 13)   # Montag
        )
        assert workdays == 2
    
    def test_count_workdays_full_month(self, widget):
        """Ganzer Monat Januar 2025 = 23 Werktage"""
        workdays = widget._count_workdays(
            QDate(2025, 1, 1),   # Mittwoch
            QDate(2025, 1, 31)   # Freitag
        )
        # Januar 2025: 31 Tage, davon 23 Werktage
        assert workdays == 23


class TestDateChangeCallbacks:
    """Tests für Datum-Änderungs-Callbacks"""
    
    def test_start_date_change_recalculates(self, widget):
        """Start-Datum-Änderung löst Neuberechnung aus"""
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))   # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 10))  # Freitag
        
        initial_text = widget.time_input.text()
        assert initial_text == "40.0h"
        
        # Start-Datum ändern
        widget.date_edit.setDate(QDate(2025, 1, 7))  # Dienstag
        
        # Sollte neu berechnet werden (4 Werktage)
        assert widget.time_input.text() == "32.0h"
    
    def test_end_date_change_recalculates(self, widget):
        """End-Datum-Änderung löst Neuberechnung aus"""
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))   # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 10))  # Freitag
        
        initial_text = widget.time_input.text()
        assert initial_text == "40.0h"
        
        # End-Datum ändern
        widget.end_date_edit.setDate(QDate(2025, 1, 17))  # Freitag (1 Woche später)
        
        # Sollte neu berechnet werden (10 Werktage)
        assert widget.time_input.text() == "80.0h"
    
    def test_worker_change_recalculates(self, widget):
        """Worker-Änderung löst Neuberechnung aus (wegen Regelarbeitszeit)"""
        # Zweiten Worker hinzufügen
        mock_worker2 = Mock()
        mock_worker2.id = 2
        mock_worker2.name = "Test Worker 2"
        mock_worker2.active = True
        
        # Settings für Worker 2
        settings = QSettings("CapacityPlanner", "Settings")
        settings.setValue("worker_2_daily_hours", 6.0)
        
        # Workers neu laden
        widget.load_workers([
            Mock(id=1, name="Test Worker", active=True),
            mock_worker2
        ])
        
        widget.type_combo.setCurrentText("Urlaub")
        widget.worker_combo.setCurrentIndex(1)  # Worker 1
        widget.date_edit.setDate(QDate(2025, 1, 6))
        widget.end_date_edit.setDate(QDate(2025, 1, 10))
        
        assert widget.time_input.text() == "40.0h"
        
        # Worker wechseln
        widget.worker_combo.setCurrentIndex(2)  # Worker 2
        
        # Sollte mit 6h/Tag neu berechnet werden
        assert widget.time_input.text() == "30.0h"
        assert "6.0h/Tag" in widget.time_preview.text()
        
        # Cleanup
        settings.remove("worker_2_daily_hours")


class TestTimeInputPreventEdit:
    """Tests dass Dauer-Eingabe bei Urlaub nicht funktioniert"""
    
    def test_time_input_change_ignored_during_vacation(self, widget):
        """Manuelle Dauer-Eingabe wird bei Urlaub ignoriert"""
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))
        widget.end_date_edit.setDate(QDate(2025, 1, 10))
        
        calculated_value = widget.time_input.text()
        
        # Versuche manuell zu ändern (sollte readonly sein)
        # Da readonly, sollte setText funktionieren aber _on_time_input_changed ignoriert
        widget.time_input.setText("100h")
        widget._on_time_input_changed("100h")
        
        # Preview sollte sich nicht ändern (bleibt bei Werktage-Info)
        assert "Werktage" in widget.time_preview.text()
