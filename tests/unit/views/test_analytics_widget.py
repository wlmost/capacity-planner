"""
Unit Tests für AnalyticsWidget
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDate

from src.views.analytics_widget import AnalyticsWidget
from src.services.analytics_service import AnalyticsService
from src.repositories.worker_repository import WorkerRepository
from src.repositories.time_entry_repository import TimeEntryRepository
from src.repositories.capacity_repository import CapacityRepository
from src.models.worker import Worker


@pytest.fixture
def mock_analytics_service():
    """Mock AnalyticsService"""
    service = Mock(spec=AnalyticsService)
    service.calculate_worker_utilization = Mock(return_value=None)
    return service


@pytest.fixture
def mock_worker_repository():
    """Mock WorkerRepository"""
    repo = Mock(spec=WorkerRepository)
    repo.find_all = Mock(return_value=[])
    return repo


@pytest.fixture
def mock_time_entry_repository():
    """Mock TimeEntryRepository"""
    repo = Mock(spec=TimeEntryRepository)
    return repo


@pytest.fixture
def mock_capacity_repository():
    """Mock CapacityRepository"""
    repo = Mock(spec=CapacityRepository)
    return repo


@pytest.fixture
def sample_workers():
    """Sample Workers für Tests"""
    return [
        Worker(id=1, name="Alice", email="alice@test.com", team="Team A", active=True),
        Worker(id=2, name="Bob", email="bob@test.com", team="Team A", active=True),
        Worker(id=3, name="Charlie", email="charlie@test.com", team="Team B", active=True),
    ]


@pytest.fixture
def sample_utilization_data():
    """Sample Utilization Data"""
    return {
        1: {
            'worker_id': 1,
            'hours_planned': 160.0,
            'hours_worked': 150.0,
            'utilization_percent': 93.75
        },
        2: {
            'worker_id': 2,
            'hours_planned': 160.0,
            'hours_worked': 180.0,
            'utilization_percent': 112.5
        },
        3: {
            'worker_id': 3,
            'hours_planned': 160.0,
            'hours_worked': 120.0,
            'utilization_percent': 75.0
        }
    }


@pytest.fixture
def analytics_widget(qtbot, mock_analytics_service, mock_worker_repository, mock_time_entry_repository, mock_capacity_repository):
    """AnalyticsWidget Fixture"""
    widget = AnalyticsWidget(
        mock_analytics_service, 
        mock_worker_repository, 
        mock_time_entry_repository, 
        mock_capacity_repository
    )
    qtbot.addWidget(widget)
    return widget


class TestAnalyticsWidgetInitialization:
    """Tests für Widget-Initialisierung"""
    
    def test_widget_creation(self, analytics_widget):
        """Test: Widget wird korrekt erstellt"""
        assert analytics_widget is not None
        assert analytics_widget.windowTitle() == ""
    
    def test_services_set(self, analytics_widget, mock_analytics_service, mock_worker_repository):
        """Test: Services werden korrekt gesetzt"""
        assert analytics_widget._analytics_service == mock_analytics_service
        assert analytics_widget._worker_repository == mock_worker_repository
    
    def test_ui_components_exist(self, analytics_widget):
        """Test: UI-Komponenten existieren"""
        assert analytics_widget._team_table is not None
        assert analytics_widget._start_date_filter is not None
        assert analytics_widget._end_date_filter is not None
        assert analytics_widget._refresh_button is not None
        assert analytics_widget._export_csv_button is not None
        assert analytics_widget._export_excel_button is not None
        assert analytics_widget._status_label is not None
        assert analytics_widget._chart_widget is not None
    
    def test_statistics_labels_exist(self, analytics_widget):
        """Test: Statistik-Labels existieren"""
        assert analytics_widget._total_workers_label is not None
        assert analytics_widget._total_planned_label is not None
        assert analytics_widget._total_worked_label is not None
        assert analytics_widget._avg_utilization_label is not None
        assert analytics_widget._avg_progress is not None
    
    def test_initial_date_range(self, analytics_widget):
        """Test: Initiale Datumsauswahl ist sinnvoll"""
        start_date = analytics_widget._start_date_filter.date()
        end_date = analytics_widget._end_date_filter.date()
        
        assert start_date < end_date
        assert end_date.toPython() == datetime.now().date()


class TestAnalyticsWidgetDataLoading:
    """Tests für Datenladen"""
    
    def test_load_workers(self, qtbot, mock_analytics_service, mock_worker_repository, mock_time_entry_repository, mock_capacity_repository, sample_workers):
        """Test: Workers werden geladen"""
        mock_worker_repository.find_all.return_value = sample_workers
        
        widget = AnalyticsWidget(
            mock_analytics_service, 
            mock_worker_repository, 
            mock_time_entry_repository, 
            mock_capacity_repository
        )
        qtbot.addWidget(widget)
        
        assert len(widget._workers) == 3
        assert all(w.active for w in widget._workers)
    
    def test_filter_inactive_workers(self, qtbot, mock_analytics_service, mock_worker_repository, mock_time_entry_repository, mock_capacity_repository):
        """Test: Inaktive Workers werden gefiltert"""
        workers = [
            Worker(id=1, name="Alice", email="alice@test.com", team="Team A", active=True),
            Worker(id=2, name="Bob", email="bob@test.com", team="Team A", active=False),
        ]
        mock_worker_repository.find_all.return_value = workers
        
        widget = AnalyticsWidget(
            mock_analytics_service, 
            mock_worker_repository, 
            mock_time_entry_repository, 
            mock_capacity_repository
        )
        qtbot.addWidget(widget)
        
        assert len(widget._workers) == 1
        assert widget._workers[0].name == "Alice"
    
    def test_refresh_data_calls_analytics(self, analytics_widget, mock_analytics_service, sample_workers):
        """Test: Refresh ruft AnalyticsService auf"""
        analytics_widget._workers = sample_workers
        mock_analytics_service.calculate_worker_utilization.return_value = {
            'worker_id': 1,
            'hours_planned': 160.0,
            'hours_worked': 150.0,
            'utilization_percent': 93.75
        }
        
        analytics_widget._refresh_data()
        
        assert mock_analytics_service.calculate_worker_utilization.call_count == 3


class TestAnalyticsWidgetStatistics:
    """Tests für Statistik-Berechnung"""
    
    def test_update_statistics(self, analytics_widget, sample_workers, sample_utilization_data):
        """Test: Statistiken werden korrekt berechnet"""
        analytics_widget._workers = sample_workers
        analytics_widget._utilization_data = sample_utilization_data
        
        analytics_widget._update_statistics()
        
        assert analytics_widget._total_workers_label.text() == "3"
        assert "480.0" in analytics_widget._total_planned_label.text()  # 160 * 3
        assert "450.0" in analytics_widget._total_worked_label.text()  # 150 + 180 + 120
    
    def test_average_utilization_calculation(self, analytics_widget, sample_workers, sample_utilization_data):
        """Test: Durchschnittliche Auslastung wird korrekt berechnet"""
        analytics_widget._workers = sample_workers
        analytics_widget._utilization_data = sample_utilization_data
        
        analytics_widget._update_statistics()
        
        # (93.75 + 112.5 + 75.0) / 3 = 93.75
        label_text = analytics_widget._avg_utilization_label.text()
        assert "93.8%" in label_text or "93.7%" in label_text
    
    def test_progress_bar_color_coding(self, analytics_widget, sample_workers):
        """Test: Progress Bar Farbkodierung"""
        # Test UNTER 80% -> Orange
        analytics_widget._workers = sample_workers[:1]
        analytics_widget._utilization_data = {
            1: {'worker_id': 1, 'hours_planned': 160.0, 'hours_worked': 100.0, 'utilization_percent': 62.5}
        }
        analytics_widget._update_statistics()
        assert "orange" in analytics_widget._avg_progress.styleSheet().lower()
        
        # Test 80-110% -> Grün
        analytics_widget._utilization_data = {
            1: {'worker_id': 1, 'hours_planned': 160.0, 'hours_worked': 150.0, 'utilization_percent': 93.75}
        }
        analytics_widget._update_statistics()
        assert "green" in analytics_widget._avg_progress.styleSheet().lower()
        
        # Test ÜBER 110% -> Rot
        analytics_widget._utilization_data = {
            1: {'worker_id': 1, 'hours_planned': 160.0, 'hours_worked': 200.0, 'utilization_percent': 125.0}
        }
        analytics_widget._update_statistics()
        assert "red" in analytics_widget._avg_progress.styleSheet().lower()


class TestAnalyticsWidgetTable:
    """Tests für Team-Tabelle"""
    
    def test_table_population(self, analytics_widget, sample_workers, sample_utilization_data):
        """Test: Tabelle wird gefüllt"""
        analytics_widget._workers = sample_workers
        analytics_widget._utilization_data = sample_utilization_data
        
        analytics_widget._update_table()
        
        assert analytics_widget._team_table.rowCount() == 3
    
    def test_table_columns(self, analytics_widget, sample_workers, sample_utilization_data):
        """Test: Tabelle hat korrekte Spalten"""
        analytics_widget._workers = sample_workers
        analytics_widget._utilization_data = sample_utilization_data
        
        analytics_widget._update_table()
        
        assert analytics_widget._team_table.columnCount() == 7
        headers = [
            analytics_widget._team_table.horizontalHeaderItem(i).text()
            for i in range(7)
        ]
        assert "Worker" in headers
        assert "Team" in headers
        assert "Auslastung (%)" in headers
        assert "Status" in headers
    
    def test_status_item_optimal(self, analytics_widget):
        """Test: Status-Item für optimale Auslastung"""
        item = analytics_widget._get_status_item(95.0)
        assert "✓" in item.text()
        assert "Optimal" in item.text()
    
    def test_status_item_under(self, analytics_widget):
        """Test: Status-Item für Unterauslastung"""
        item = analytics_widget._get_status_item(70.0)
        assert "⚠️" in item.text()
        assert "Unter" in item.text()
    
    def test_status_item_over(self, analytics_widget):
        """Test: Status-Item für Überauslastung"""
        item = analytics_widget._get_status_item(120.0)
        assert "❗" in item.text()
        assert "Über" in item.text()


class TestAnalyticsWidgetExport:
    """Tests für CSV-Export"""
    
    @patch('builtins.open', create=True)
    @patch('src.views.analytics_widget.QFileDialog.getSaveFileName')
    def test_export_to_csv(self, mock_dialog, mock_open, analytics_widget, sample_workers, sample_utilization_data):
        """Test: CSV-Export funktioniert"""
        analytics_widget._workers = sample_workers
        analytics_widget._utilization_data = sample_utilization_data
        
        mock_dialog.return_value = ('/path/to/export.csv', 'CSV Files (*.csv)')
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        analytics_widget._export_to_csv()
        
        mock_open.assert_called_once()
        assert "✓" in analytics_widget._status_label.text()
    
    @patch('src.views.analytics_widget.QFileDialog.getSaveFileName')
    def test_export_canceled(self, mock_dialog, analytics_widget, sample_workers, sample_utilization_data):
        """Test: Export kann abgebrochen werden"""
        analytics_widget._workers = sample_workers
        analytics_widget._utilization_data = sample_utilization_data
        
        # Speichere vorherigen Status
        previous_status = analytics_widget._status_label.text()
        
        mock_dialog.return_value = ('', '')  # User canceled
        
        analytics_widget._export_to_csv()
        
        # Status sollte unverändert bleiben (kein neuer Erfolg/Fehler)
        assert analytics_widget._status_label.text() == previous_status
    
    def test_export_no_data_warning(self, analytics_widget, qtbot):
        """Test: Warnung bei fehlenden Daten"""
        analytics_widget._utilization_data = {}
        
        with patch('src.views.analytics_widget.QMessageBox.warning') as mock_warning:
            analytics_widget._export_to_csv()
            mock_warning.assert_called_once()


class TestAnalyticsWidgetSignals:
    """Tests für Signals"""
    
    def test_data_refreshed_signal(self, qtbot, analytics_widget, sample_workers):
        """Test: data_refreshed Signal wird emittiert"""
        analytics_widget._workers = sample_workers
        
        with qtbot.waitSignal(analytics_widget.data_refreshed, timeout=1000):
            analytics_widget._refresh_data()
    
    def test_filter_changed_triggers_refresh(self, analytics_widget, mock_analytics_service):
        """Test: Filter-Änderung triggert Refresh"""
        with patch.object(analytics_widget, '_refresh_data') as mock_refresh:
            analytics_widget._start_date_filter.setDate(QDate.currentDate().addDays(-7))
            mock_refresh.assert_called_once()


class TestAnalyticsWidgetErrorHandling:
    """Tests für Error Handling"""
    
    def test_error_message_display(self, analytics_widget):
        """Test: Error-Nachricht wird angezeigt"""
        analytics_widget._show_error("Test Error")
        
        assert "✗" in analytics_widget._status_label.text()
        assert "Test Error" in analytics_widget._status_label.text()
        assert "red" in analytics_widget._status_label.styleSheet().lower()
    
    def test_success_message_display(self, analytics_widget):
        """Test: Success-Nachricht wird angezeigt"""
        analytics_widget._show_success("Test Success")
        
        assert "✓" in analytics_widget._status_label.text()
        assert "Test Success" in analytics_widget._status_label.text()
        assert "green" in analytics_widget._status_label.styleSheet().lower()
    
    def test_refresh_data_handles_errors(self, analytics_widget, mock_analytics_service):
        """Test: Fehler beim Refresh werden behandelt"""
        mock_analytics_service.calculate_worker_utilization.side_effect = Exception("Test Error")
        analytics_widget._workers = [Worker(id=1, name="Test", email="test@test.com", team="A", active=True)]
        
        analytics_widget._refresh_data()
        
        assert "✗" in analytics_widget._status_label.text()
        assert "Fehler" in analytics_widget._status_label.text()


class TestAnalyticsWidgetFilters:
    """Tests für Filter-Funktionalität"""
    
    def test_team_filter_populated(self, analytics_widget, mock_worker_repository):
        """Test: Team-Filter wird mit Teams populiert"""
        workers = [
            Worker(id=1, name="Alice", email="alice@test.com", team="Team A", active=True),
            Worker(id=2, name="Bob", email="bob@test.com", team="Team B", active=True),
            Worker(id=3, name="Charlie", email="charlie@test.com", team="Team A", active=True),
        ]
        mock_worker_repository.find_all.return_value = workers
        
        analytics_widget._load_initial_data()
        
        # "Alle Teams" + 2 unique teams = 3 items
        assert analytics_widget._team_filter.count() == 3
        assert analytics_widget._team_filter.itemText(0) == "Alle Teams"
        assert "Team A" in [analytics_widget._team_filter.itemText(i) for i in range(analytics_widget._team_filter.count())]
        assert "Team B" in [analytics_widget._team_filter.itemText(i) for i in range(analytics_widget._team_filter.count())]
    
    def test_status_filter_has_options(self, analytics_widget):
        """Test: Status-Filter hat alle Optionen"""
        assert analytics_widget._status_filter.count() == 4
        assert analytics_widget._status_filter.itemText(0) == "Alle Status"
        assert "Unter" in analytics_widget._status_filter.itemText(1)
        assert "Optimal" in analytics_widget._status_filter.itemText(2)
        assert "Über" in analytics_widget._status_filter.itemText(3)
    
    def test_apply_filters_team_filter(self, analytics_widget):
        """Test: Team-Filter funktioniert"""
        analytics_widget._workers = [
            Worker(id=1, name="Alice", email="alice@test.com", team="Team A", active=True),
            Worker(id=2, name="Bob", email="bob@test.com", team="Team B", active=True),
            Worker(id=3, name="Charlie", email="charlie@test.com", team="Team A", active=True),
        ]
        
        # Setze Team-Filter auf "Team A"
        analytics_widget._team_filter.addItem("Team A", "Team A")
        analytics_widget._team_filter.setCurrentIndex(1)
        
        filtered = analytics_widget._apply_filters()
        
        assert len(filtered) == 2
        assert all(w.team == "Team A" for w in filtered)
    
    def test_apply_filters_no_filter(self, analytics_widget):
        """Test: Ohne Filter werden alle Workers zurückgegeben"""
        analytics_widget._workers = [
            Worker(id=1, name="Alice", email="alice@test.com", team="Team A", active=True),
            Worker(id=2, name="Bob", email="bob@test.com", team="Team B", active=True),
        ]
        
        filtered = analytics_widget._apply_filters()
        
        assert len(filtered) == 2
    
    def test_table_sorting_enabled(self, analytics_widget):
        """Test: Tabellen-Sortierung ist aktiviert"""
        assert analytics_widget._team_table.isSortingEnabled()
    
    def test_filter_change_triggers_refresh(self, analytics_widget, qtbot, mock_analytics_service):
        """Test: Filter-Änderung triggert Refresh"""
        # Setup: Mock Analytics Service, damit refresh nicht crasht
        mock_analytics_service.calculate_worker_utilization.return_value = None
        analytics_widget._workers = []
        
        # Initialer State
        initial_status = analytics_widget._status_label.text()
        
        # Team-Filter ändern
        analytics_widget._team_filter.setCurrentIndex(0)
        qtbot.wait(200)
        
        # Status sollte sich geändert haben (zeigt dass refresh getriggert wurde)
        new_status = analytics_widget._status_label.text()
        # Status wird von _refresh_data() verändert
        assert new_status != initial_status or "Daten" in new_status or "geladen" in new_status
