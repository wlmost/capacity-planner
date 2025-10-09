"""
Unit Tests für TimeEntryViewModel
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from PySide6.QtCore import QObject

from src.viewmodels.time_entry_viewmodel import TimeEntryViewModel
from src.services.time_parser_service import TimeParserService
from src.repositories.time_entry_repository import TimeEntryRepository
from src.models.time_entry import TimeEntry


class TestTimeEntryViewModel:
    """Tests für TimeEntryViewModel"""
    
    @pytest.fixture
    def time_parser(self):
        """Mock TimeParserService"""
        return TimeParserService()
    
    @pytest.fixture
    def repository(self):
        """Mock TimeEntryRepository"""
        mock_repo = Mock(spec=TimeEntryRepository)
        mock_repo.create = MagicMock(return_value=1)  # Returns ID
        return mock_repo
    
    @pytest.fixture
    def viewmodel(self, time_parser, repository):
        """Erstellt TimeEntryViewModel für Tests"""
        return TimeEntryViewModel(time_parser, repository)
    
    # Tests für create_entry mit gültigen Daten
    def test_create_entry_with_valid_data(self, viewmodel, repository):
        """Test: Gültige Eingabe sollte Entry erstellen"""
        # Arrange
        worker_id = 1
        date_str = "2025-10-06"
        time_str = "1:30"
        description = "Meeting"
        
        # Act
        result = viewmodel.create_entry(worker_id, date_str, time_str, description)
        
        # Assert
        assert result is True
        repository.create.assert_called_once()
        
        # Verify created entry
        created_entry = repository.create.call_args[0][0]
        assert created_entry.worker_id == worker_id
        assert created_entry.duration_minutes == 90
        assert created_entry.description == description
    
    def test_create_entry_with_different_time_formats(self, viewmodel, repository):
        """Test: Verschiedene Zeit-Formate sollten funktionieren"""
        test_cases = [
            ("1:30", 90),
            ("90m", 90),
            ("1.5h", 90),
            ("2:00", 120),
        ]
        
        for time_str, expected_minutes in test_cases:
            repository.reset_mock()
            result = viewmodel.create_entry(1, "2025-10-06", time_str, "Test")
            
            assert result is True
            created_entry = repository.create.call_args[0][0]
            assert created_entry.duration_minutes == expected_minutes
    
    def test_create_entry_with_optional_project(self, viewmodel, repository):
        """Test: Optional project sollte gespeichert werden"""
        result = viewmodel.create_entry(1, "2025-10-06", "1:30", "Test", project="Project X")
        
        assert result is True
        created_entry = repository.create.call_args[0][0]
        assert created_entry.project == "Project X"
    
    # Tests für Validierung
    def test_validate_input_with_empty_description(self, viewmodel):
        """Test: Leere Beschreibung sollte Fehler werfen"""
        errors = viewmodel.validate_input(1, "2025-10-06", "1:30", "")
        
        assert len(errors) > 0
        assert any("Beschreibung" in error for error in errors)
    
    def test_validate_input_with_invalid_date(self, viewmodel):
        """Test: Ungültiges Datum sollte Fehler werfen"""
        errors = viewmodel.validate_input(1, "invalid-date", "1:30", "Test")
        
        assert len(errors) > 0
        assert any("Datum" in error for error in errors)
    
    def test_validate_input_with_invalid_time(self, viewmodel):
        """Test: Ungültige Zeit sollte Fehler werfen"""
        errors = viewmodel.validate_input(1, "2025-10-06", "invalid", "Test")
        
        assert len(errors) > 0
        assert any("Zeit" in error for error in errors)
    
    def test_validate_input_with_invalid_worker_id(self, viewmodel):
        """Test: Ungültige Worker-ID sollte Fehler werfen"""
        errors = viewmodel.validate_input(0, "2025-10-06", "1:30", "Test")
        
        assert len(errors) > 0
        assert any("Worker" in error for error in errors)
    
    def test_validate_input_with_valid_data(self, viewmodel):
        """Test: Gültige Daten sollten keine Fehler ergeben"""
        errors = viewmodel.validate_input(1, "2025-10-06", "1:30", "Test")
        
        assert len(errors) == 0
    
    # Tests für parse_time_input
    def test_parse_time_input_valid_format(self, viewmodel):
        """Test: Gültige Zeit-Eingabe parsen"""
        result = viewmodel.parse_time_input("1:30")
        
        assert result == 90
    
    def test_parse_time_input_invalid_format(self, viewmodel):
        """Test: Ungültige Zeit-Eingabe sollte None zurückgeben"""
        result = viewmodel.parse_time_input("invalid")
        
        assert result is None
    
    # Tests für Signals
    def test_entry_created_signal_emitted(self, viewmodel, repository, qtbot):
        """Test: entry_created Signal wird bei Erfolg emittiert"""
        with qtbot.waitSignal(viewmodel.entry_created, timeout=1000) as blocker:
            viewmodel.create_entry(1, "2025-10-06", "1:30", "Test")
        
        assert blocker.signal_triggered
        assert blocker.args[0] == 1  # Entry ID
    
    def test_validation_failed_signal_emitted(self, viewmodel, qtbot):
        """Test: validation_failed Signal wird bei Fehler emittiert"""
        with qtbot.waitSignal(viewmodel.validation_failed, timeout=1000) as blocker:
            viewmodel.create_entry(1, "invalid-date", "1:30", "Test")
        
        assert blocker.signal_triggered
        assert len(blocker.args[0]) > 0  # Fehler-Liste
    
    # Tests für Error Handling
    def test_create_entry_handles_repository_error(self, viewmodel, repository, qtbot):
        """Test: Repository-Fehler sollten abgefangen werden"""
        repository.create.side_effect = Exception("Database error")
        
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            result = viewmodel.create_entry(1, "2025-10-06", "1:30", "Test")
        
        assert result is False
        assert blocker.signal_triggered
        assert "Database error" in blocker.args[0]
    
    # Tests für format_duration
    def test_format_duration_colon_format(self, viewmodel):
        """Test: Dauer im Colon-Format formatieren"""
        result = viewmodel.format_duration(90, "colon")
        
        assert result == "1:30"
    
    def test_format_duration_decimal_format(self, viewmodel):
        """Test: Dauer im Dezimal-Format formatieren"""
        result = viewmodel.format_duration(90, "decimal")
        
        assert result == "1.50h"
    
    # Tests für update_entry
    def test_update_entry_with_valid_data(self, viewmodel, repository):
        """Test: Update sollte Entry aktualisieren"""
        # Arrange
        entry_id = 1
        worker_id = 1
        date_str = "2025-10-06"
        time_str = "2:00"
        description = "Updated Meeting"
        
        repository.update = MagicMock(return_value=True)
        
        # Act
        result = viewmodel.update_entry(entry_id, worker_id, date_str, time_str, description)
        
        # Assert
        assert result is True
        repository.update.assert_called_once()
        
        # Verify updated entry
        updated_entry = repository.update.call_args[0][0]
        assert updated_entry.id == entry_id
        assert updated_entry.worker_id == worker_id
        assert updated_entry.duration_minutes == 120
        assert updated_entry.description == description
    
    def test_update_entry_with_optional_project(self, viewmodel, repository):
        """Test: Update sollte optional project speichern"""
        repository.update = MagicMock(return_value=True)
        
        result = viewmodel.update_entry(1, 1, "2025-10-06", "1:30", "Test", project="Project Y")
        
        assert result is True
        updated_entry = repository.update.call_args[0][0]
        assert updated_entry.project == "Project Y"
    
    def test_update_entry_with_validation_errors(self, viewmodel, repository):
        """Test: Update sollte bei Validierungsfehlern False zurückgeben"""
        repository.update = MagicMock(return_value=True)
        
        result = viewmodel.update_entry(1, 0, "2025-10-06", "1:30", "Test")
        
        assert result is False
        repository.update.assert_not_called()
    
    def test_update_entry_handles_repository_error(self, viewmodel, repository, qtbot):
        """Test: Repository-Fehler bei Update sollten abgefangen werden"""
        repository.update = MagicMock(side_effect=Exception("Database error"))
        
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            result = viewmodel.update_entry(1, 1, "2025-10-06", "1:30", "Test")
        
        assert result is False
        assert blocker.signal_triggered
        assert "Database error" in blocker.args[0]
    
    def test_update_entry_emits_signal_on_success(self, viewmodel, repository, qtbot):
        """Test: entry_updated Signal wird bei Erfolg emittiert"""
        repository.update = MagicMock(return_value=True)
        
        with qtbot.waitSignal(viewmodel.entry_updated, timeout=1000) as blocker:
            viewmodel.update_entry(1, 1, "2025-10-06", "1:30", "Test")
        
        assert blocker.signal_triggered
        assert blocker.args[0] == 1  # Entry ID
    
    def test_update_entry_returns_false_when_update_fails(self, viewmodel, repository, qtbot):
        """Test: Update sollte False zurückgeben wenn Repository False zurückgibt"""
        repository.update = MagicMock(return_value=False)
        
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            result = viewmodel.update_entry(1, 1, "2025-10-06", "1:30", "Test")
        
        assert result is False
        assert blocker.signal_triggered

