"""
Unit Tests für TablePaginationWidget
"""
import pytest
from unittest.mock import MagicMock
from src.views.table_pagination_widget import TablePaginationWidget


class TestTablePaginationWidget:
    """Tests für TablePaginationWidget"""
    
    def test_initialization_defaults(self):
        """Test: Standardwerte werden korrekt gesetzt"""
        widget = TablePaginationWidget()
        
        assert widget.get_current_page() == 1
        assert widget.get_page_size() == 25
        assert widget.get_offset() == 0
        assert widget.get_limit() == 25
    
    def test_initialization_custom_page_size(self):
        """Test: Custom Seitengröße wird verwendet"""
        widget = TablePaginationWidget(default_page_size=50)
        
        assert widget.get_page_size() == 50
        assert widget.get_limit() == 50
    
    def test_set_total_items(self):
        """Test: Gesamtanzahl Items wird korrekt gesetzt"""
        widget = TablePaginationWidget()
        widget.set_total_items(150)
        
        # Mit 25 Items pro Seite sollten 6 Seiten entstehen (150/25=6)
        assert widget.get_current_page() == 1
    
    def test_page_navigation(self):
        """Test: Navigation zwischen Seiten funktioniert"""
        widget = TablePaginationWidget(default_page_size=10)
        widget.set_total_items(50)  # 5 Seiten
        
        # Mock signal handler
        page_changed_handler = MagicMock()
        widget.page_changed.connect(page_changed_handler)
        
        # Gehe zu Seite 2
        widget._next_button.click()
        assert widget.get_current_page() == 2
        assert widget.get_offset() == 10
        page_changed_handler.assert_called_once_with(2)
        
        # Gehe zu Seite 3
        widget._next_button.click()
        assert widget.get_current_page() == 3
        assert widget.get_offset() == 20
        
        # Gehe zurück zu Seite 2
        widget._prev_button.click()
        assert widget.get_current_page() == 2
        assert widget.get_offset() == 10
    
    def test_page_size_change(self):
        """Test: Änderung der Seitengröße funktioniert"""
        widget = TablePaginationWidget(default_page_size=10)
        widget.set_total_items(100)
        
        # Mock signal handlers
        page_size_changed_handler = MagicMock()
        page_changed_handler = MagicMock()
        widget.page_size_changed.connect(page_size_changed_handler)
        widget.page_changed.connect(page_changed_handler)
        
        # Gehe zu Seite 3
        widget._next_button.click()
        widget._next_button.click()
        assert widget.get_current_page() == 3
        
        # Ändere Seitengröße
        page_size_changed_handler.reset_mock()
        page_changed_handler.reset_mock()
        widget._page_size_combo.setCurrentText("25")
        
        # Sollte zurück zu Seite 1 gehen
        assert widget.get_current_page() == 1
        assert widget.get_page_size() == 25
        page_size_changed_handler.assert_called_once_with(25)
        page_changed_handler.assert_called_once_with(1)
    
    def test_button_states(self):
        """Test: Buttons werden korrekt aktiviert/deaktiviert"""
        widget = TablePaginationWidget(default_page_size=10)
        widget.set_total_items(30)  # 3 Seiten
        
        # Seite 1: Zurück deaktiviert, Weiter aktiviert
        assert not widget._prev_button.isEnabled()
        assert widget._next_button.isEnabled()
        
        # Gehe zu Seite 2
        widget._next_button.click()
        assert widget._prev_button.isEnabled()
        assert widget._next_button.isEnabled()
        
        # Gehe zu Seite 3 (letzte Seite)
        widget._next_button.click()
        assert widget._prev_button.isEnabled()
        assert not widget._next_button.isEnabled()
    
    def test_reset_to_first_page(self):
        """Test: Reset auf erste Seite funktioniert"""
        widget = TablePaginationWidget(default_page_size=10)
        widget.set_total_items(50)
        
        # Gehe zu Seite 3
        widget._next_button.click()
        widget._next_button.click()
        assert widget.get_current_page() == 3
        
        # Reset
        widget.reset_to_first_page()
        assert widget.get_current_page() == 1
    
    def test_offset_calculation(self):
        """Test: Offset wird korrekt berechnet"""
        widget = TablePaginationWidget(default_page_size=10)
        widget.set_total_items(100)
        
        # Seite 1: Offset = 0
        assert widget.get_offset() == 0
        
        # Seite 2: Offset = 10
        widget._next_button.click()
        assert widget.get_offset() == 10
        
        # Seite 3: Offset = 20
        widget._next_button.click()
        assert widget.get_offset() == 20
    
    def test_empty_list(self):
        """Test: Leere Liste wird korrekt behandelt"""
        widget = TablePaginationWidget()
        widget.set_total_items(0)
        
        assert widget.get_current_page() == 1
        assert not widget._prev_button.isEnabled()
        assert not widget._next_button.isEnabled()
    
    def test_page_out_of_range_resets(self):
        """Test: Seite außerhalb des Bereichs wird zurückgesetzt"""
        widget = TablePaginationWidget(default_page_size=10)
        widget.set_total_items(50)  # 5 Seiten
        
        # Gehe zu Seite 5
        for _ in range(4):
            widget._next_button.click()
        assert widget.get_current_page() == 5
        
        # Reduziere Items auf 20 (nur 2 Seiten)
        widget.set_total_items(20)
        
        # Sollte automatisch auf Seite 1 zurückgehen
        assert widget.get_current_page() == 1
