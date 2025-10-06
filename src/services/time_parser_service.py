"""
Time Parser Service
Flexibles Parsing von Zeiteingaben in verschiedenen Formaten
"""
import re
from typing import Optional


class TimeParserService:
    """
    Parst verschiedene Zeit-Formate und konvertiert zu Minuten
    
    Unterstützte Formate:
    - "1:30" oder "1:30:00" (Stunden:Minuten:Sekunden)
    - "90m" oder "90min" (Minuten)
    - "1.5h" oder "1,5h" (Dezimal-Stunden)
    - "5400s" (Sekunden)
    
    Beispiele:
        >>> parser = TimeParserService()
        >>> parser.parse("1:30")
        90
        >>> parser.parse("90m")
        90
        >>> parser.parse("1.5h")
        90
    """
    
    # Regex-Patterns für verschiedene Formate
    PATTERN_COLON = re.compile(r'^(\d+):(\d+)(?::(\d+))?$')  # 1:30 oder 1:30:00
    PATTERN_MINUTES = re.compile(r'^(\d+(?:\.\d+)?)\s*m(?:in)?$', re.IGNORECASE)  # 90m, 90min
    PATTERN_HOURS = re.compile(r'^(\d+(?:[.,]\d+)?)\s*h(?:ours?)?$', re.IGNORECASE)  # 1.5h
    PATTERN_SECONDS = re.compile(r'^(\d+)\s*s(?:ec)?$', re.IGNORECASE)  # 5400s
    
    def parse(self, time_input: str) -> Optional[int]:
        """
        Parst Zeiteingabe und gibt Minuten zurück
        
        Args:
            time_input: Zeiteingabe als String
            
        Returns:
            Minuten als Integer oder None bei ungültigem Format
            
        Raises:
            ValueError: Bei ungültigem Format
        """
        if not time_input or not isinstance(time_input, str):
            raise ValueError("Eingabe muss ein nicht-leerer String sein")
        
        time_input = time_input.strip()
        
        # Versuche verschiedene Formate
        if match := self.PATTERN_COLON.match(time_input):
            return self._parse_colon_format(match)
        elif match := self.PATTERN_MINUTES.match(time_input):
            return self._parse_minutes(match)
        elif match := self.PATTERN_HOURS.match(time_input):
            return self._parse_hours(match)
        elif match := self.PATTERN_SECONDS.match(time_input):
            return self._parse_seconds(match)
        else:
            raise ValueError(f"Ungültiges Zeitformat: {time_input}")
    
    def _parse_colon_format(self, match: re.Match) -> int:
        """Parst HH:MM:SS oder HH:MM Format"""
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = int(match.group(3)) if match.group(3) else 0
        
        total_minutes = hours * 60 + minutes + seconds // 60
        return total_minutes
    
    def _parse_minutes(self, match: re.Match) -> int:
        """Parst Minuten-Format (90m)"""
        minutes = float(match.group(1))
        return int(round(minutes))
    
    def _parse_hours(self, match: re.Match) -> int:
        """Parst Stunden-Format (1.5h)"""
        hours_str = match.group(1).replace(',', '.')  # Deutsche Notation
        hours = float(hours_str)
        return int(round(hours * 60))
    
    def _parse_seconds(self, match: re.Match) -> int:
        """Parst Sekunden-Format (5400s)"""
        seconds = int(match.group(1))
        return seconds // 60
    
    def format_minutes(self, minutes: int, format_type: str = "colon") -> str:
        """
        Formatiert Minuten als String
        
        Args:
            minutes: Minuten als Integer
            format_type: "colon" (1:30) oder "decimal" (1.5h)
            
        Returns:
            Formatierter String
        """
        if format_type == "colon":
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}:{mins:02d}"
        elif format_type == "decimal":
            hours = minutes / 60.0
            return f"{hours:.2f}h"
        else:
            raise ValueError(f"Ungültiger Format-Typ: {format_type}")
