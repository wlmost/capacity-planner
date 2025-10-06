"""
UtilizationChartWidget - Balkendiagramm für Worker-Auslastung
"""
from typing import Dict, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class UtilizationChartWidget(QWidget):
    """
    Widget für Auslastungs-Balkendiagramm mit matplotlib
    
    Features:
        - Horizontales Balkendiagramm für bessere Lesbarkeit
        - Farbkodierung nach Auslastungs-Status
        - Sortierung nach Auslastung
        - Responsive Design
    """
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt UI mit matplotlib Canvas"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Matplotlib Figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout.addWidget(self.canvas)
        
        # Initiales leeres Chart
        self._show_empty_chart()
    
    def _show_empty_chart(self):
        """Zeigt leeres Chart mit Platzhalter"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(
            0.5, 0.5, 
            'Keine Daten verfügbar\n\nBitte Filter anpassen oder Daten laden',
            ha='center', va='center',
            fontsize=12, color='gray',
            transform=ax.transAxes
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
    
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
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Daten vorbereiten
        worker_names = []
        utilizations = []
        colors = []
        
        # Nach Auslastung sortieren
        sorted_workers = sorted(
            workers,
            key=lambda w: utilization_data.get(w.id, {}).get('utilization_percent', 0),
            reverse=True
        )
        
        for worker in sorted_workers:
            if worker.id not in utilization_data:
                continue
            
            data = utilization_data[worker.id]
            worker_names.append(worker.name)
            utilization = data['utilization_percent']
            utilizations.append(utilization)
            
            # Farbkodierung
            if utilization < 80:
                colors.append('#FFA500')  # Orange
            elif utilization <= 110:
                colors.append('#32CD32')  # Lime Green
            else:
                colors.append('#FF4500')  # Red-Orange
        
        # Horizontales Balkendiagramm
        y_pos = range(len(worker_names))
        bars = ax.barh(y_pos, utilizations, color=colors, alpha=0.7)
        
        # Referenzlinien für Schwellwerte
        ax.axvline(x=80, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='80% Schwelle')
        ax.axvline(x=110, color='red', linestyle='--', linewidth=1, alpha=0.5, label='110% Schwelle')
        
        # Beschriftung
        ax.set_yticks(y_pos)
        ax.set_yticklabels(worker_names)
        ax.set_xlabel('Auslastung (%)', fontsize=10, fontweight='bold')
        ax.set_title('Worker-Auslastung im Überblick', fontsize=12, fontweight='bold', pad=15)
        
        # Werte in Balken anzeigen
        for i, (bar, util) in enumerate(zip(bars, utilizations)):
            width = bar.get_width()
            ax.text(
                width + 2,
                bar.get_y() + bar.get_height() / 2,
                f'{util:.1f}%',
                ha='left', va='center',
                fontsize=9, fontweight='bold'
            )
        
        # Legende
        ax.legend(loc='lower right', fontsize=8)
        
        # Grid
        ax.grid(axis='x', alpha=0.3, linestyle=':')
        ax.set_axisbelow(True)
        
        # Layout anpassen
        self.figure.tight_layout()
        self.canvas.draw()
    
    def clear(self):
        """Löscht das Chart"""
        self._show_empty_chart()
