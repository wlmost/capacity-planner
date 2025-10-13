"""
Unit Tests für CapacityWidget
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.views.capacity_widget import CapacityWidget
from src.viewmodels.capacity_viewmodel import CapacityViewModel
from src.models.capacity import Capacity
from src.models.worker import Worker


@pytest.fixture
def mock_viewmodel():
    """Mock CapacityViewModel"""
    viewmodel = Mock(spec=CapacityViewModel)
    viewmodel.get_active_workers = Mock(return_value=[])
    viewmodel.load_all_capacities = Mock()
    viewmodel.calculate_utilization = Mock(return_value=None)
    
    # Mock _analytics_service für direkten Zugriff
    mock_analytics = Mock()
    mock_analytics.calculate_worker_utilization = Mock(return_value=None)
    # Mock _db_service für Repository-Zugriff
    mock_db_service = Mock()
    mock_analytics._db_service = mock_db_service
    viewmodel._analytics_service = mock_analytics
    
    return viewmodel


@pytest.fixture
def sample_workers():
    """Sample Workers für Tests"""
    return [
        Worker(id=1, name="Alice", email="alice@test.com", team="Team A", active=True),
        Worker(id=2, name="Bob", email="bob@test.com", team="Team B", active=True),
    ]


@pytest.fixture
def sample_capacities():
    """Sample Capacities für Tests"""
    return [
        Capacity(
            id=1,
            worker_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=160.0,
            notes="Januar Kapazität"
        ),
        Capacity(
            id=2,
            worker_id=2,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=160.0,
            notes="Januar Kapazität"
        ),
    ]


@pytest.fixture
def capacity_widget(qtbot, mock_viewmodel):
    """CapacityWidget Fixture"""
    widget = CapacityWidget(mock_viewmodel)
    qtbot.addWidget(widget)
    return widget


class TestCapacityWidgetTablePopulation:
    """Tests für Tabellen-Befüllung"""
    
    def test_populate_table_makes_cells_readonly(self, capacity_widget, sample_workers, sample_capacities, monkeypatch):
        """Test: Tabellenzellen sind nicht editierbar"""
        # Setup
        from src.models.time_entry import TimeEntry
        
        # Mock TimeEntryRepository
        mock_repo = Mock()
        mock_repo.find_by_worker = Mock(return_value=[
            TimeEntry(
                id=1,
                worker_id=1,
                date=datetime(2024, 1, 15),
                duration_minutes=480,  # 8 hours
                description="Test"
            )
        ])
        
        mock_repo_class = Mock(return_value=mock_repo)
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        capacity_widget._workers = sample_workers
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify - alle Zellen sollten nicht editierbar sein
        for row in range(capacity_widget._capacity_table.rowCount()):
            for col in range(capacity_widget._capacity_table.columnCount()):
                item = capacity_widget._capacity_table.item(row, col)
                assert item is not None, f"Item at row {row}, col {col} should exist"
                # Check that ItemIsEditable flag is NOT set
                assert not (item.flags() & Qt.ItemIsEditable), \
                    f"Item at row {row}, col {col} should not be editable"
    
    def test_populate_table_displays_utilization(self, capacity_widget, sample_workers, sample_capacities, monkeypatch):
        """Test: Auslastung wird in der Tabelle angezeigt"""
        # Setup
        from src.models.time_entry import TimeEntry
        
        # Mock TimeEntryRepository - 150 Stunden gearbeitet bei 160 geplanten
        mock_repo = Mock()
        mock_time_entries = []
        # 20 Tage à 7.5 Stunden = 150 Stunden
        for day in range(1, 21):
            mock_time_entries.append(
                TimeEntry(
                    id=day,
                    worker_id=1,
                    date=datetime(2024, 1, day),
                    duration_minutes=450,  # 7.5 Stunden
                    description="Test"
                )
            )
        mock_repo.find_by_worker = Mock(return_value=mock_time_entries)
        
        mock_repo_class = Mock(return_value=mock_repo)
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        capacity_widget._workers = sample_workers
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify - Auslastungsspalte (Index 5) sollte Werte enthalten
        for row in range(capacity_widget._capacity_table.rowCount()):
            util_item = capacity_widget._capacity_table.item(row, 5)
            assert util_item is not None, f"Utilization item at row {row} should exist"
            util_text = util_item.text()
            # Sollte einen Prozentwert oder "-" anzeigen
            # 150h / 160h = 93.75%
            assert "%" in util_text or util_text == "-", \
                f"Utilization should show percentage or '-', got: {util_text}"
    
    def test_calculate_capacity_utilization_with_data(self, capacity_widget, monkeypatch):
        """Test: Auslastungsberechnung mit Daten"""
        # Setup
        from src.models.time_entry import TimeEntry
        
        capacity = Capacity(
            id=1,
            worker_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=160.0
        )
        
        # Mock TimeEntryRepository - 150 Stunden gearbeitet
        mock_repo = Mock()
        mock_time_entries = []
        for day in range(1, 21):
            mock_time_entries.append(
                TimeEntry(
                    id=day,
                    worker_id=1,
                    date=datetime(2024, 1, day),
                    duration_minutes=450,  # 7.5 Stunden
                    description="Test"
                )
            )
        mock_repo.find_by_worker = Mock(return_value=mock_time_entries)
        
        mock_repo_class = Mock(return_value=mock_repo)
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        # Execute
        result = capacity_widget._calculate_capacity_utilization(capacity)
        
        # Verify - 150h / 160h = 93.75%
        assert result['percent'] == 93.75
        assert result['display'] == "93.8%"
    
    def test_calculate_capacity_utilization_no_data(self, capacity_widget, monkeypatch):
        """Test: Auslastungsberechnung ohne Daten"""
        # Setup
        capacity = Capacity(
            id=1,
            worker_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=0.0  # Keine geplanten Stunden
        )
        
        # Mock TimeEntryRepository - keine Einträge
        mock_repo = Mock()
        mock_repo.find_by_worker = Mock(return_value=[])
        
        mock_repo_class = Mock(return_value=mock_repo)
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        # Execute
        result = capacity_widget._calculate_capacity_utilization(capacity)
        
        # Verify
        assert result['percent'] is None
        assert result['display'] == "-"
    
    def test_calculate_capacity_utilization_with_error(self, capacity_widget, monkeypatch):
        """Test: Auslastungsberechnung bei Fehler"""
        # Setup
        capacity = Capacity(
            id=1,
            worker_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=160.0
        )
        
        # Mock TimeEntryRepository um Exception zu werfen
        mock_repo_class = Mock(side_effect=Exception("Test Error"))
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        # Execute
        result = capacity_widget._calculate_capacity_utilization(capacity)
        
        # Verify - sollte "-" zurückgeben bei Fehler
        assert result['percent'] is None
        assert result['display'] == "-"


class TestCapacityWidgetUtilizationColors:
    """Tests für Auslastungs-Farben"""
    
    def test_utilization_color_low(self, capacity_widget, sample_workers, sample_capacities, monkeypatch):
        """Test: Niedrige Auslastung (<80%) wird orange dargestellt"""
        # Setup
        from src.models.time_entry import TimeEntry
        
        # Mock TimeEntryRepository - 120 Stunden gearbeitet bei 160 geplanten = 75%
        mock_repo = Mock()
        mock_time_entries = []
        for day in range(1, 17):  # 16 Tage à 7.5 Stunden = 120 Stunden
            mock_time_entries.append(
                TimeEntry(
                    id=day,
                    worker_id=1,
                    date=datetime(2024, 1, day),
                    duration_minutes=450,  # 7.5 Stunden
                    description="Test"
                )
            )
        mock_repo.find_by_worker = Mock(return_value=mock_time_entries)
        
        mock_repo_class = Mock(return_value=mock_repo)
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        capacity_widget._workers = sample_workers
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify
        util_item = capacity_widget._capacity_table.item(0, 5)
        assert util_item.foreground().color().name() == "#ffa500"  # orange
    
    def test_utilization_color_normal(self, capacity_widget, sample_workers, sample_capacities, monkeypatch):
        """Test: Normale Auslastung (80-110%) wird grün dargestellt"""
        # Setup
        from src.models.time_entry import TimeEntry
        
        # Mock TimeEntryRepository - 150 Stunden gearbeitet bei 160 geplanten = 93.75%
        mock_repo = Mock()
        mock_time_entries = []
        for day in range(1, 21):  # 20 Tage à 7.5 Stunden = 150 Stunden
            mock_time_entries.append(
                TimeEntry(
                    id=day,
                    worker_id=1,
                    date=datetime(2024, 1, day),
                    duration_minutes=450,  # 7.5 Stunden
                    description="Test"
                )
            )
        mock_repo.find_by_worker = Mock(return_value=mock_time_entries)
        
        mock_repo_class = Mock(return_value=mock_repo)
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        capacity_widget._workers = sample_workers
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify
        util_item = capacity_widget._capacity_table.item(0, 5)
        assert util_item.foreground().color().name() == "#008000"  # green
    
    def test_utilization_color_high(self, capacity_widget, sample_workers, sample_capacities, monkeypatch):
        """Test: Hohe Auslastung (>110%) wird rot dargestellt"""
        # Setup
        from src.models.time_entry import TimeEntry
        
        # Mock TimeEntryRepository - 180 Stunden gearbeitet bei 160 geplanten = 112.5%
        mock_repo = Mock()
        mock_time_entries = []
        for day in range(1, 25):  # 24 Tage à 7.5 Stunden = 180 Stunden
            mock_time_entries.append(
                TimeEntry(
                    id=day,
                    worker_id=1,
                    date=datetime(2024, 1, day),
                    duration_minutes=450,  # 7.5 Stunden
                    description="Test"
                )
            )
        mock_repo.find_by_worker = Mock(return_value=mock_time_entries)
        
        mock_repo_class = Mock(return_value=mock_repo)
        monkeypatch.setattr('src.repositories.time_entry_repository.TimeEntryRepository', mock_repo_class)
        
        capacity_widget._workers = sample_workers
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify
        util_item = capacity_widget._capacity_table.item(0, 5)
        assert util_item.foreground().color().name() == "#ff0000"  # red
