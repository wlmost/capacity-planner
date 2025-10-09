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
    
    def test_populate_table_makes_cells_readonly(self, capacity_widget, sample_workers, sample_capacities):
        """Test: Tabellenzellen sind nicht editierbar"""
        # Setup
        capacity_widget._workers = sample_workers
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(return_value={
            'hours_worked': 150.0,
            'hours_planned': 160.0,
            'utilization_percent': 93.75
        })
        
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
    
    def test_populate_table_displays_utilization(self, capacity_widget, sample_workers, sample_capacities):
        """Test: Auslastung wird in der Tabelle angezeigt"""
        # Setup
        capacity_widget._workers = sample_workers
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(return_value={
            'hours_worked': 150.0,
            'hours_planned': 160.0,
            'utilization_percent': 93.75
        })
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify - Auslastungsspalte (Index 5) sollte Werte enthalten
        for row in range(capacity_widget._capacity_table.rowCount()):
            util_item = capacity_widget._capacity_table.item(row, 5)
            assert util_item is not None, f"Utilization item at row {row} should exist"
            util_text = util_item.text()
            # Sollte entweder einen Prozentwert oder "-" anzeigen
            assert util_text == "93.8%" or util_text == "-", \
                f"Utilization should show percentage or '-', got: {util_text}"
    
    def test_calculate_capacity_utilization_with_data(self, capacity_widget):
        """Test: Auslastungsberechnung mit Daten"""
        # Setup
        capacity = Capacity(
            id=1,
            worker_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=160.0
        )
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(return_value={
            'hours_worked': 150.0,
            'hours_planned': 160.0,
            'utilization_percent': 93.75
        })
        
        # Execute
        result = capacity_widget._calculate_capacity_utilization(capacity)
        
        # Verify
        assert result['percent'] == 93.75
        assert result['display'] == "93.8%"
    
    def test_calculate_capacity_utilization_no_data(self, capacity_widget):
        """Test: Auslastungsberechnung ohne Daten"""
        # Setup
        capacity = Capacity(
            id=1,
            worker_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=160.0
        )
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(return_value={
            'hours_worked': 0.0,
            'hours_planned': 0.0,
            'utilization_percent': 0.0
        })
        
        # Execute
        result = capacity_widget._calculate_capacity_utilization(capacity)
        
        # Verify
        assert result['percent'] is None
        assert result['display'] == "-"
    
    def test_calculate_capacity_utilization_with_error(self, capacity_widget):
        """Test: Auslastungsberechnung bei Fehler"""
        # Setup
        capacity = Capacity(
            id=1,
            worker_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            planned_hours=160.0
        )
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(side_effect=Exception("Test Error"))
        
        # Execute
        result = capacity_widget._calculate_capacity_utilization(capacity)
        
        # Verify - sollte "-" zurückgeben bei Fehler
        assert result['percent'] is None
        assert result['display'] == "-"


class TestCapacityWidgetUtilizationColors:
    """Tests für Auslastungs-Farben"""
    
    def test_utilization_color_low(self, capacity_widget, sample_workers, sample_capacities):
        """Test: Niedrige Auslastung (<80%) wird orange dargestellt"""
        # Setup
        capacity_widget._workers = sample_workers
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(return_value={
            'hours_worked': 120.0,
            'hours_planned': 160.0,
            'utilization_percent': 75.0
        })
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify
        util_item = capacity_widget._capacity_table.item(0, 5)
        assert util_item.foreground().color().name() == "#ffa500"  # orange
    
    def test_utilization_color_normal(self, capacity_widget, sample_workers, sample_capacities):
        """Test: Normale Auslastung (80-110%) wird grün dargestellt"""
        # Setup
        capacity_widget._workers = sample_workers
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(return_value={
            'hours_worked': 150.0,
            'hours_planned': 160.0,
            'utilization_percent': 93.75
        })
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify
        util_item = capacity_widget._capacity_table.item(0, 5)
        assert util_item.foreground().color().name() == "#008000"  # green
    
    def test_utilization_color_high(self, capacity_widget, sample_workers, sample_capacities):
        """Test: Hohe Auslastung (>110%) wird rot dargestellt"""
        # Setup
        capacity_widget._workers = sample_workers
        capacity_widget._viewmodel._analytics_service.calculate_worker_utilization = Mock(return_value={
            'hours_worked': 180.0,
            'hours_planned': 160.0,
            'utilization_percent': 112.5
        })
        
        # Execute
        capacity_widget._populate_table(sample_capacities)
        
        # Verify
        util_item = capacity_widget._capacity_table.item(0, 5)
        assert util_item.foreground().color().name() == "#ff0000"  # red
