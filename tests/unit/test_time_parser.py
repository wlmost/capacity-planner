"""
Unit Tests für Time Parser Service
"""
import pytest
from src.services.time_parser_service import TimeParserService


class TestTimeParserService:
    """Tests für TimeParserService"""
    
    @pytest.fixture
    def parser(self):
        """Erstellt Parser-Instanz für Tests"""
        return TimeParserService()
    
    # Tests für Colon-Format (HH:MM)
    def test_parse_colon_format_basic(self, parser):
        """Test: 1:30 sollte 90 Minuten ergeben"""
        assert parser.parse("1:30") == 90
    
    def test_parse_colon_format_with_seconds(self, parser):
        """Test: 1:30:30 sollte 90 Minuten ergeben (Sekunden gerundet)"""
        assert parser.parse("1:30:30") == 90
    
    def test_parse_colon_format_hours_only(self, parser):
        """Test: 2:00 sollte 120 Minuten ergeben"""
        assert parser.parse("2:00") == 120
    
    # Tests für Minuten-Format
    def test_parse_minutes_format(self, parser):
        """Test: 90m sollte 90 Minuten ergeben"""
        assert parser.parse("90m") == 90
    
    def test_parse_minutes_format_long(self, parser):
        """Test: 90min sollte 90 Minuten ergeben"""
        assert parser.parse("90min") == 90
    
    def test_parse_minutes_format_decimal(self, parser):
        """Test: 90.5m sollte 90 Minuten ergeben (banker's rounding in Python)"""
        assert parser.parse("90.5m") == 90
    
    # Tests für Stunden-Format
    def test_parse_hours_format_decimal(self, parser):
        """Test: 1.5h sollte 90 Minuten ergeben"""
        assert parser.parse("1.5h") == 90
    
    def test_parse_hours_format_german_decimal(self, parser):
        """Test: 1,5h sollte 90 Minuten ergeben (deutsche Notation)"""
        assert parser.parse("1,5h") == 90
    
    def test_parse_hours_format_long(self, parser):
        """Test: 2hours sollte 120 Minuten ergeben"""
        assert parser.parse("2hours") == 120
    
    # Tests für Sekunden-Format
    def test_parse_seconds_format(self, parser):
        """Test: 5400s sollte 90 Minuten ergeben"""
        assert parser.parse("5400s") == 90
    
    # Tests für Fehlerbehandlung
    def test_parse_invalid_format_raises_error(self, parser):
        """Test: Ungültiges Format sollte ValueError werfen"""
        with pytest.raises(ValueError, match="Ungültiges Zeitformat"):
            parser.parse("invalid")
    
    def test_parse_empty_string_raises_error(self, parser):
        """Test: Leerer String sollte ValueError werfen"""
        with pytest.raises(ValueError, match="nicht-leerer String"):
            parser.parse("")
    
    def test_parse_none_raises_error(self, parser):
        """Test: None sollte ValueError werfen"""
        with pytest.raises(ValueError, match="nicht-leerer String"):
            parser.parse(None)
    
    # Tests für format_minutes
    def test_format_minutes_colon(self, parser):
        """Test: 90 Minuten sollte als 1:30 formatiert werden"""
        assert parser.format_minutes(90, "colon") == "1:30"
    
    def test_format_minutes_decimal(self, parser):
        """Test: 90 Minuten sollte als 1.50h formatiert werden"""
        assert parser.format_minutes(90, "decimal") == "1.50h"
    
    def test_format_minutes_invalid_format_raises_error(self, parser):
        """Test: Ungültiger Format-Typ sollte ValueError werfen"""
        with pytest.raises(ValueError, match="Ungültiger Format-Typ"):
            parser.format_minutes(90, "invalid")
