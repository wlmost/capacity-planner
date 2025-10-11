"""
Unit Tests für TimeEntryWidget - Urlaubseinträge speichern
"""
import pytest
from unittest.mock import Mock, MagicMock, call
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDate, QSettings

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
    vm.create_entry = Mock(return_value=True)  # Simuliere erfolgreiche Speicherung
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


class TestVacationEntriesSave:
    """Tests für das Speichern von Urlaubseinträgen"""
    
    def test_single_workday_vacation_creates_one_entry(self, widget, mock_viewmodel):
        """Ein einzelner Urlaubstag erstellt einen Eintrag"""
        # Arrange
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))  # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 6))  # Gleicher Tag
        widget.description_input.setPlainText("Urlaubstag")
        
        # Act
        widget._on_save_clicked()
        
        # Assert
        assert mock_viewmodel.create_entry.call_count == 1
        call_args = mock_viewmodel.create_entry.call_args
        assert call_args[0][1] == "2025-01-06"  # Datum
        assert call_args[0][2] == "8.0h"  # Zeit
        assert "[Urlaub] Urlaubstag" in call_args[0][3]  # Beschreibung
    
    def test_one_week_vacation_creates_five_entries(self, widget, mock_viewmodel):
        """Eine Woche Urlaub (Mo-Fr) erstellt 5 Einträge"""
        # Arrange
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))  # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 10))  # Freitag
        widget.description_input.setPlainText("Wochenurlaub")
        
        # Act
        widget._on_save_clicked()
        
        # Assert
        assert mock_viewmodel.create_entry.call_count == 5
        
        # Prüfe, dass alle 5 Werktage erstellt wurden
        created_dates = [call[0][1] for call in mock_viewmodel.create_entry.call_args_list]
        expected_dates = ["2025-01-06", "2025-01-07", "2025-01-08", "2025-01-09", "2025-01-10"]
        assert created_dates == expected_dates
    
    def test_two_weeks_vacation_creates_ten_entries(self, widget, mock_viewmodel):
        """Zwei Wochen Urlaub erstellt 10 Einträge (ohne Wochenenden)"""
        # Arrange
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))  # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 17))  # Freitag (2 Wochen später)
        widget.description_input.setPlainText("Jahresurlaub")
        
        # Act
        widget._on_save_clicked()
        
        # Assert
        assert mock_viewmodel.create_entry.call_count == 10
        
        # Prüfe, dass alle Werktage erstellt wurden (ohne Wochenenden 11./12. Jan)
        created_dates = [call[0][1] for call in mock_viewmodel.create_entry.call_args_list]
        expected_dates = [
            "2025-01-06", "2025-01-07", "2025-01-08", "2025-01-09", "2025-01-10",  # Woche 1
            "2025-01-13", "2025-01-14", "2025-01-15", "2025-01-16", "2025-01-17"   # Woche 2
        ]
        assert created_dates == expected_dates
    
    def test_vacation_with_weekend_only_creates_no_entries(self, widget, mock_viewmodel):
        """Urlaub nur am Wochenende erstellt keine Einträge"""
        # Arrange
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 11))  # Samstag
        widget.end_date_edit.setDate(QDate(2025, 1, 12))  # Sonntag
        widget.description_input.setPlainText("Wochenende")
        
        # Act
        widget._on_save_clicked()
        
        # Assert - Keine Einträge sollten erstellt werden
        assert mock_viewmodel.create_entry.call_count == 0
    
    def test_vacation_entries_use_daily_hours_setting(self, widget, mock_viewmodel):
        """Urlaubseinträge verwenden die Regelarbeitszeit des Workers"""
        # Arrange
        settings = QSettings("CapacityPlanner", "Settings")
        settings.setValue("worker_1_daily_hours", 7.5)  # Abweichende Arbeitszeit
        
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))  # Montag
        widget.end_date_edit.setDate(QDate(2025, 1, 6))  # Gleicher Tag
        widget.description_input.setPlainText("Urlaubstag")
        
        # Act
        widget._on_save_clicked()
        
        # Assert
        call_args = mock_viewmodel.create_entry.call_args
        assert call_args[0][2] == "7.5h"  # Zeit entspricht der Regelarbeitszeit
        
        # Cleanup
        settings.setValue("worker_1_daily_hours", 8.0)
    
    def test_vacation_description_has_type_prefix(self, widget, mock_viewmodel):
        """Urlaubseinträge haben [Urlaub] Prefix in der Beschreibung"""
        # Arrange
        widget.type_combo.setCurrentText("Urlaub")
        widget.date_edit.setDate(QDate(2025, 1, 6))
        widget.end_date_edit.setDate(QDate(2025, 1, 6))
        widget.description_input.setPlainText("Erholungsurlaub")
        
        # Act
        widget._on_save_clicked()
        
        # Assert
        call_args = mock_viewmodel.create_entry.call_args
        description = call_args[0][3]
        assert description == "[Urlaub] Erholungsurlaub"
    
    def test_regular_work_entry_creates_single_entry(self, widget, mock_viewmodel):
        """Regulärer Arbeitseintrag erstellt nur einen Eintrag"""
        # Arrange
        widget.type_combo.setCurrentText("Arbeit")
        widget.date_edit.setDate(QDate(2025, 1, 6))
        widget.time_input.setText("8h")
        widget.description_input.setPlainText("Projektarbeit")
        
        # Act
        widget._on_save_clicked()
        
        # Assert
        assert mock_viewmodel.create_entry.call_count == 1
        call_args = mock_viewmodel.create_entry.call_args
        assert call_args[0][1] == "2025-01-06"
        assert call_args[0][2] == "8h"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
