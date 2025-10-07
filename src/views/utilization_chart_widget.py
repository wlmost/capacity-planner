"""
UtilizationChartWidget - Balkendiagramm für Worker-Auslastung
"""
from typing import Dict, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtCharts import (
    QChart, QChartView, QBarSet, QHorizontalBarSeries,
    QBarCategoryAxis, QValueAxis
)
from PySide6.QtGui import QColor, QPainter


class UtilizationChartWidget(QWidget):
    """
    Widget für Auslastungs-Balkendiagramm mit QtCharts
    
    Features:
        - Horizontales Balkendiagramm für bessere Lesbarkeit
        - Farbkodierung nach Auslastungs-Status
        - Sortierung nach Auslastung
        - Native Qt-Integration für konsistenten Look
    """
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt UI mit QtCharts"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Chart und View erstellen
        self.chart = QChart()
        self.chart.setTitle("Worker-Auslastung im Überblick")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        layout.addWidget(self.chart_view)
        
        # Initiales leeres Chart
        self._show_empty_chart()
    
    def _show_empty_chart(self):
        """Zeigt leeres Chart mit Platzhalter"""
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)
        
        # Platzhalter-Text wird durch setTitle bereits angezeigt
        self.chart.setTitle("Keine Daten verfügbar\n\nBitte Filter anpassen oder Daten laden")
    
    def update_chart(self, workers: List, utilization_data: Dict[int, Dict]):
        """
        Aktualisiert Chart mit neuen Daten
        
        Args:
            workers: Liste von Worker-Objekten
            utilization_data: Dict mit {worker_id: {hours_planned, hours_worked, utilization_percent}}
        """
        if not utilization_data:
            self._show_empty_chart()
            return
        
        # Alte Series und Achsen entfernen
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)
        
        # Daten vorbereiten und sortieren
        sorted_workers = sorted(
            workers,
            key=lambda w: utilization_data.get(w.id, {}).get('utilization_percent', 0),
            reverse=False  # Von niedrig zu hoch für horizontale Darstellung
        )
        
        categories = []
        series = QHorizontalBarSeries()
        
        for worker in sorted_workers:
            if worker.id not in utilization_data:
                continue
            
            data = utilization_data[worker.id]
            utilization = data['utilization_percent']
            
            # BarSet für diesen Worker
            bar_set = QBarSet(worker.name)
            bar_set.append(utilization)
            
            # Farbkodierung nach Auslastungs-Status
            if utilization < 80:
                color = QColor("#FFA500")  # Orange - Unterauslastung
            elif utilization <= 110:
                color = QColor("#32CD32")  # Lime Green - Optimal
            else:
                color = QColor("#FF4500")  # Red-Orange - Überauslastung
            
            bar_set.setColor(color)
            series.append(bar_set)
            categories.append(worker.name)
        
        # Series zum Chart hinzufügen
        self.chart.addSeries(series)
        
        # Y-Achse (Kategorien - Worker-Namen)
        axis_y = QBarCategoryAxis()
        axis_y.append(categories)
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        # X-Achse (Werte - Auslastung in %)
        axis_x = QValueAxis()
        axis_x.setTitleText("Auslastung (%)")
        axis_x.setRange(0, max(150, max(
            utilization_data.get(w.id, {}).get('utilization_percent', 0) 
            for w in sorted_workers if w.id in utilization_data
        ) + 20))
        axis_x.setLabelFormat("%d")
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        # Legende ausblenden (nicht nötig bei farbkodierten Einzelbalken)
        self.chart.legend().setVisible(False)
        
        # Titel setzen
        self.chart.setTitle("Worker-Auslastung im Überblick")
    
    def clear(self):
        """Löscht das Chart"""
        self._show_empty_chart()
