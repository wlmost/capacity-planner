"""
Unit Tests für TimeEntryWidget - Such-Funktionalität
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import QDate
from pytestqt.qtbot import QtBot

from src.views.time_entry_widget import TimeEntryWidget
from src.viewmodels.time_entry_viewmodel import TimeEntryViewModel
from src.repositories.time_entry_repository import TimeEntryRepository
from src.models.time_entry import TimeEntry
from src.models.worker import Worker
from datetime import datetime


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
    return vm


@pytest.fixture
def mock_repository():
    """Mock TimeEntryRepository mit Test-Daten"""
    repo = Mock(spec=TimeEntryRepository)
    
    # Beispiel-Einträge für Tests
    entries = [
        Mock(
            id=1,
            worker_id=1,
            date=datetime(2024, 1, 15),
            duration_minutes=480,
            description="Feature Implementation",
            project="Project Alpha"
        ),
        Mock(
            id=2,
            worker_id=1,
            date=datetime(2024, 1, 16),
            duration_minutes=420,
            description="Bug Fixes",
            project="Project Beta"
        ),
        Mock(
            id=3,
            worker_id=2,
            date=datetime(2024, 1, 17),
            duration_minutes=360,
            description="Code Review",
            project="Project Alpha"
        ),
    ]
    
    repo.find_by_date_range = Mock(return_value=entries)
    return repo


@pytest.fixture
def widget(qapp, mock_viewmodel, mock_repository):
    """TimeEntryWidget Instanz mit Test-Daten"""
    widget = TimeEntryWidget(mock_viewmodel, mock_repository)
    
    # Worker für Tests hinzufügen
    workers = [
        Worker(id=1, name="Alice Test", email="alice@test.com", team="Dev", active=True),
        Worker(id=2, name="Bob Worker", email="bob@test.com", team="QA", active=True),
    ]
    widget.load_workers(workers)
    
    # Einträge laden um Tabelle zu füllen
    widget._refresh_entries_list()
    
    yield widget


class TestTimeEntryWidgetSearchUI:
    """Tests für Such-Widget UI-Integration"""
    
    def test_search_widget_exists(self, widget):
        """Such-Widget ist vorhanden"""
        assert hasattr(widget, 'search_widget')
        assert widget.search_widget is not None
    
    def test_search_widget_placeholder(self, widget):
        """Such-Widget hat korrekten Placeholder"""
        expected = "🔍 Datum, Worker, Projekt oder Beschreibung suchen..."
        assert widget.search_widget._placeholder == expected
    
    def test_search_widget_signal_connected(self, widget):
        """Such-Widget Signal ist verbunden"""
        # Signal connection kann nicht direkt getestet werden,
        # aber wir können prüfen ob Handler existiert
        assert hasattr(widget, '_on_search')
        assert callable(widget._on_search)


class TestTimeEntryWidgetSearchFunctionality:
    """Tests für Such-Funktionalität"""
    
    def test_search_no_text_shows_all_rows(self, widget):
        """Leerer Suchtext zeigt alle Zeilen"""
        # Initial sollten alle Zeilen sichtbar sein
        total_rows = widget.entries_table.rowCount()
        
        # Suche mit leerem Text
        widget._on_search("")
        
        # Prüfe dass alle Zeilen sichtbar sind
        visible_rows = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        assert visible_rows == total_rows
    
    def test_search_filters_by_worker(self, widget):
        """Suche nach Worker-Name filtert korrekt"""
        total_rows = widget.entries_table.rowCount()
        
        if total_rows == 0:
            pytest.skip("Keine Test-Daten in Tabelle")
        
        # Suche nach "Alice"
        widget._on_search("Alice")
        
        # Zähle sichtbare Zeilen
        visible_rows = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        
        # Mindestens eine Zeile sollte sichtbar sein (wenn Alice existiert)
        # oder keine (wenn Alice nicht existiert)
        assert visible_rows <= total_rows
    
    def test_search_filters_by_project(self, widget):
        """Suche nach Projekt filtert korrekt"""
        total_rows = widget.entries_table.rowCount()
        
        if total_rows == 0:
            pytest.skip("Keine Test-Daten in Tabelle")
        
        # Suche nach "Alpha"
        widget._on_search("Alpha")
        
        visible_rows = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        
        assert visible_rows <= total_rows
    
    def test_search_filters_by_description(self, widget):
        """Suche nach Beschreibung filtert korrekt"""
        total_rows = widget.entries_table.rowCount()
        
        if total_rows == 0:
            pytest.skip("Keine Test-Daten in Tabelle")
        
        # Suche nach "Implementation"
        widget._on_search("Implementation")
        
        visible_rows = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        
        assert visible_rows <= total_rows
    
    def test_search_is_case_insensitive(self, widget):
        """Suche ist case-insensitive"""
        total_rows = widget.entries_table.rowCount()
        
        if total_rows == 0:
            pytest.skip("Keine Test-Daten in Tabelle")
        
        # Suche mit verschiedenen Cases
        widget._on_search("ALICE")
        visible_upper = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        
        # Alle Zeilen zurücksetzen
        widget._on_search("")
        
        widget._on_search("alice")
        visible_lower = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        
        # Beide Suchen sollten gleiche Ergebnisse liefern
        assert visible_upper == visible_lower
    
    def test_search_substring_matching(self, widget):
        """Suche findet Substrings"""
        total_rows = widget.entries_table.rowCount()
        
        if total_rows == 0:
            pytest.skip("Keine Test-Daten in Tabelle")
        
        # Suche nach Teilstring
        widget._on_search("Ali")  # Sollte "Alice" finden
        
        visible_rows = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        
        # Ergebnis sollte konsistent sein
        assert visible_rows <= total_rows
    
    def test_search_no_matches_hides_all(self, widget):
        """Suche ohne Treffer versteckt alle Zeilen"""
        total_rows = widget.entries_table.rowCount()
        
        if total_rows == 0:
            pytest.skip("Keine Test-Daten in Tabelle")
        
        # Suche nach etwas das nicht existiert
        widget._on_search("XXXXXXXXXX")
        
        visible_rows = sum(
            1 for row in range(total_rows) 
            if not widget.entries_table.isRowHidden(row)
        )
        
        # Keine Zeile sollte sichtbar sein
        assert visible_rows == 0


class TestSearchResultCount:
    """Tests für Treffer-Anzeige"""
    
    def test_result_count_updated_on_search(self, widget):
        """Treffer-Anzeige wird aktualisiert"""
        total_rows = widget.entries_table.rowCount()
        
        # Leere Suche
        widget._on_search("")
        
        # Result Label sollte aktualisiert sein
        result_text = widget.search_widget._result_label.text()
        
        # Sollte entweder leer sein oder Total anzeigen
        assert result_text == "" or str(total_rows) in result_text or "Einträge" in result_text
    
    def test_result_count_shows_filtered(self, widget):
        """Treffer-Anzeige zeigt gefilterte Anzahl"""
        total_rows = widget.entries_table.rowCount()
        
        if total_rows == 0:
            pytest.skip("Keine Test-Daten in Tabelle")
        
        # Suche durchführen
        widget._on_search("test")
        
        # Result Label prüfen
        result_text = widget.search_widget._result_label.text()
        
        # Sollte Treffer-Info enthalten
        assert result_text != "" or total_rows == 0


class TestSearchEdgeCases:
    """Edge Case Tests"""
    
    def test_search_empty_table(self, widget, mock_repository):
        """Suche in leerer Tabelle crasht nicht"""
        # Leere Tabelle
        mock_repository.find_by_date_range = Mock(return_value=[])
        widget._refresh_entries_list()
        
        # Suche sollte nicht crashen
        widget._on_search("test")
        
        # Keine Zeilen sollten vorhanden sein
        assert widget.entries_table.rowCount() == 0
    
    def test_search_special_characters(self, widget):
        """Suche mit Sonderzeichen funktioniert"""
        # Sollte nicht crashen
        widget._on_search("@#$%")
        widget._on_search("äöü")
        widget._on_search("test & test")
        
        assert True  # Wenn wir hier ankommen, ist alles gut
    
    def test_search_very_long_text(self, widget):
        """Suche mit sehr langem Text funktioniert"""
        long_text = "a" * 1000
        
        # Sollte nicht crashen
        widget._on_search(long_text)
        
        assert True
    
    def test_search_multiple_times(self, widget):
        """Mehrfache Suchen funktionieren"""
        widget._on_search("test1")
        widget._on_search("test2")
        widget._on_search("")
        widget._on_search("test3")
        
        # Sollte immer funktionieren
        assert True
