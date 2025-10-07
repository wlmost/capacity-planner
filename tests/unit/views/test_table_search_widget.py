"""
Unit Tests für TableSearchWidget
"""
import pytest
from PySide6.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from src.views.table_search_widget import TableSearchWidget


@pytest.fixture(scope="module")
def qapp():
    """Qt Application für GUI-Tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestTableSearchWidget:
    """Tests für TableSearchWidget Komponente"""
    
    def test_widget_creation(self, qapp):
        """Widget kann erstellt werden"""
        widget = TableSearchWidget()
        assert widget is not None
    
    def test_default_placeholder(self, qapp):
        """Standard-Placeholder wird gesetzt"""
        widget = TableSearchWidget()
        assert widget._search_input.placeholderText() == "🔍 Suchen..."
    
    def test_custom_placeholder(self, qapp):
        """Custom Placeholder kann gesetzt werden"""
        widget = TableSearchWidget("Custom Search...")
        assert widget._search_input.placeholderText() == "Custom Search..."
    
    def test_clear_button_enabled(self, qapp):
        """Built-in Clear-Button ist aktiviert"""
        widget = TableSearchWidget()
        assert widget._search_input.isClearButtonEnabled()
    
    def test_search_signal_emission(self, qapp, qtbot: QtBot):
        """Signal wird bei Texteingabe emittiert"""
        widget = TableSearchWidget()
        
        with qtbot.waitSignal(widget.search_changed, timeout=1000) as blocker:
            widget._search_input.setText("test")
        
        assert blocker.args[0] == "test"
    
    def test_get_search_text(self, qapp):
        """get_search_text gibt aktuellen Text zurück"""
        widget = TableSearchWidget()
        widget._search_input.setText("hello world")
        
        assert widget.get_search_text() == "hello world"
    
    def test_clear_method(self, qapp):
        """clear() löscht Suchtext"""
        widget = TableSearchWidget()
        widget._search_input.setText("test")
        assert widget.get_search_text() == "test"
        
        widget.clear()
        assert widget.get_search_text() == ""


class TestTableSearchWidgetResultDisplay:
    """Tests für Treffer-Anzeige"""
    
    def test_result_count_no_search(self, qapp):
        """Anzeige bei leerer Suche"""
        widget = TableSearchWidget()
        
        # Keine Suche, 10 Einträge
        widget.set_result_count(10, 10)
        assert widget._result_label.text() == "10 Einträge"
    
    def test_result_count_empty_table(self, qapp):
        """Anzeige bei leerer Tabelle"""
        widget = TableSearchWidget()
        
        # Keine Einträge
        widget.set_result_count(0, 0)
        assert widget._result_label.text() == ""
    
    def test_result_count_with_results(self, qapp):
        """Anzeige bei gefilterten Ergebnissen"""
        widget = TableSearchWidget()
        widget._search_input.setText("test")  # Aktive Suche
        
        # 5 von 10 Treffern
        widget.set_result_count(5, 10)
        assert widget._result_label.text() == "5 von 10 Treffern"
    
    def test_result_count_no_matches(self, qapp):
        """Anzeige bei keinen Treffern"""
        widget = TableSearchWidget()
        widget._search_input.setText("xyz")  # Aktive Suche
        
        # Keine Treffer
        widget.set_result_count(0, 10)
        assert widget._result_label.text() == "Keine Treffer"
    
    def test_result_count_all_match(self, qapp):
        """Anzeige wenn alle Einträge passen"""
        widget = TableSearchWidget()
        widget._search_input.setText("test")  # Aktive Suche
        
        # Alle 10 passen
        widget.set_result_count(10, 10)
        assert widget._result_label.text() == "10 Einträge"


class TestTableSearchWidgetStyling:
    """Tests für Styling-Verhalten"""
    
    def test_input_has_styling(self, qapp):
        """Eingabefeld hat CSS-Styling"""
        widget = TableSearchWidget()
        assert widget._search_input.styleSheet() != ""
    
    def test_result_label_has_styling(self, qapp):
        """Result-Label hat CSS-Styling"""
        widget = TableSearchWidget()
        assert widget._result_label.styleSheet() != ""
    
    def test_no_margin_on_widget(self, qapp):
        """Widget hat keine Margins (für Layout-Integration)"""
        widget = TableSearchWidget()
        margins = widget.layout().contentsMargins()
        
        assert margins.left() == 0
        assert margins.top() == 0
        assert margins.right() == 0
        assert margins.bottom() == 0


class TestTableSearchWidgetEdgeCases:
    """Edge Case Tests"""
    
    def test_empty_search_text(self, qapp, qtbot: QtBot):
        """Leerer Text triggert Signal"""
        widget = TableSearchWidget()
        widget._search_input.setText("test")
        
        with qtbot.waitSignal(widget.search_changed, timeout=1000) as blocker:
            widget._search_input.clear()
        
        assert blocker.args[0] == ""
    
    def test_whitespace_search(self, qapp):
        """Whitespace wird als gültiger Suchtext behandelt"""
        widget = TableSearchWidget()
        widget._search_input.setText("   ")
        
        assert widget.get_search_text() == "   "
    
    def test_special_characters_search(self, qapp):
        """Sonderzeichen werden korrekt behandelt"""
        widget = TableSearchWidget()
        special = "äöü@#$%&*"
        widget._search_input.setText(special)
        
        assert widget.get_search_text() == special
    
    def test_long_search_text(self, qapp):
        """Langer Suchtext wird unterstützt"""
        widget = TableSearchWidget()
        long_text = "a" * 1000
        widget._search_input.setText(long_text)
        
        assert widget.get_search_text() == long_text
    
    def test_multiple_clears(self, qapp):
        """Mehrfaches Clear ist safe"""
        widget = TableSearchWidget()
        
        widget.clear()
        widget.clear()
        widget.clear()
        
        assert widget.get_search_text() == ""
    
    def test_result_count_negative(self, qapp):
        """Negative Werte werden behandelt (defensive)"""
        widget = TableSearchWidget()
        
        # Sollte nicht crashen
        try:
            widget.set_result_count(-1, 10)
            assert True
        except:
            assert False, "set_result_count sollte negative Werte nicht crashen"
