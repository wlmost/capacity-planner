"""
WorkerDetailDialog - Detail-Ansicht für einzelne Workers
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QFormLayout, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from ..models.worker import Worker
from ..services.analytics_service import AnalyticsService
from ..repositories.time_entry_repository import TimeEntryRepository
from ..repositories.capacity_repository import CapacityRepository
from .utilization_chart_widget import UtilizationChartWidget


class WorkerDetailDialog(QDialog):
    """
    Dialog für detaillierte Worker-Ansicht
    
    Features:
        - Worker-Informationen
        - Auslastungs-Statistiken (aktuell & historisch)
        - Zeiterfassungs-Historie
        - Kapazitäts-Übersicht
        - Individuelles Auslastungs-Chart
    """
    
    def __init__(
        self,
        worker: Worker,
        analytics_service: AnalyticsService,
        time_entry_repository: TimeEntryRepository,
        capacity_repository: CapacityRepository,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self._worker = worker
        self._analytics_service = analytics_service
        self._time_entry_repository = time_entry_repository
        self._capacity_repository = capacity_repository
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Erstellt das Dialog-Layout"""
        self.setWindowTitle(f"Worker Details: {self._worker.name}")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # Header mit Worker-Info
        header_group = self._create_header_group()
        layout.addWidget(header_group)
        
        # Tab Widget für verschiedene Ansichten
        self._tabs = QTabWidget()
        
        # Tab 1: Übersicht & Chart
        overview_tab = self._create_overview_tab()
        self._tabs.addTab(overview_tab, "📊 Übersicht")
        
        # Tab 2: Zeiterfassungs-Historie
        time_entries_tab = self._create_time_entries_tab()
        self._tabs.addTab(time_entries_tab, "⏱️ Zeiterfassung")
        
        # Tab 3: Kapazitäts-Historie
        capacities_tab = self._create_capacities_tab()
        self._tabs.addTab(capacities_tab, "📅 Kapazitäten")
        
        layout.addWidget(self._tabs)
        
        # Button-Leiste
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _create_header_group(self) -> QWidget:
        """Erstellt Header mit Worker-Informationen"""
        group = QGroupBox("Worker-Informationen")
        layout = QFormLayout(group)
        
        # Name
        name_label = QLabel(self._worker.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addRow("Name:", name_label)
        
        # Email
        email_label = QLabel(self._worker.email)
        layout.addRow("Email:", email_label)
        
        # Team
        team_label = QLabel(self._worker.team or "-")
        layout.addRow("Team:", team_label)
        
        # Status
        status_label = QLabel("Aktiv" if self._worker.active else "Inaktiv")
        status_label.setStyleSheet(
            "color: green; font-weight: bold;" if self._worker.active 
            else "color: red; font-weight: bold;"
        )
        layout.addRow("Status:", status_label)
        
        # Erstellt am
        created_label = QLabel(self._worker.created_at.strftime("%d.%m.%Y %H:%M"))
        layout.addRow("Erstellt am:", created_label)
        
        return group
    
    def _create_overview_tab(self) -> QWidget:
        """Erstellt Übersichts-Tab mit Statistiken und Chart"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statistik-Gruppen
        stats_layout = QHBoxLayout()
        
        # Aktuelle Auslastung (letzte 30 Tage)
        current_group = QGroupBox("Aktuelle Auslastung (30 Tage)")
        current_layout = QFormLayout(current_group)
        
        self._current_planned_label = QLabel("0.0 h")
        self._current_planned_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        current_layout.addRow("Geplant:", self._current_planned_label)
        
        self._current_worked_label = QLabel("0.0 h")
        self._current_worked_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        current_layout.addRow("Gearbeitet:", self._current_worked_label)
        
        self._current_util_label = QLabel("0.0%")
        self._current_util_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        current_layout.addRow("Auslastung:", self._current_util_label)
        
        stats_layout.addWidget(current_group)
        
        # Historische Auslastung (letzte 90 Tage)
        historical_group = QGroupBox("Historische Auslastung (90 Tage)")
        historical_layout = QFormLayout(historical_group)
        
        self._hist_planned_label = QLabel("0.0 h")
        self._hist_planned_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        historical_layout.addRow("Geplant:", self._hist_planned_label)
        
        self._hist_worked_label = QLabel("0.0 h")
        self._hist_worked_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        historical_layout.addRow("Gearbeitet:", self._hist_worked_label)
        
        self._hist_util_label = QLabel("0.0%")
        self._hist_util_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        historical_layout.addRow("Auslastung:", self._hist_util_label)
        
        stats_layout.addWidget(historical_group)
        
        layout.addLayout(stats_layout)
        
        # Chart für Auslastungs-Trend
        chart_group = QGroupBox("Auslastungs-Trend")
        chart_layout = QVBoxLayout(chart_group)
        
        self._detail_chart = UtilizationChartWidget()
        chart_layout.addWidget(self._detail_chart)
        
        layout.addWidget(chart_group)
        
        return widget
    
    def _create_time_entries_tab(self) -> QWidget:
        """Erstellt Tab für Zeiterfassungs-Historie"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tabelle für Zeiterfassungen
        self._time_entries_table = QTableWidget()
        self._time_entries_table.setColumnCount(4)
        self._time_entries_table.setHorizontalHeaderLabels([
            "Datum", "Dauer", "Projekt", "Beschreibung"
        ])
        self._time_entries_table.setAlternatingRowColors(True)
        self._time_entries_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self._time_entries_table)
        
        return widget
    
    def _create_capacities_tab(self) -> QWidget:
        """Erstellt Tab für Kapazitäts-Historie"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tabelle für Kapazitäten
        self._capacities_table = QTableWidget()
        self._capacities_table.setColumnCount(3)
        self._capacities_table.setHorizontalHeaderLabels([
            "Datum", "Stunden/Tag", "Beschreibung"
        ])
        self._capacities_table.setAlternatingRowColors(True)
        self._capacities_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self._capacities_table)
        
        return widget
    
    def _load_data(self):
        """Lädt alle Daten für den Worker"""
        try:
            # Aktuelle Auslastung (30 Tage)
            end_date = datetime.now()
            start_date_30 = end_date - timedelta(days=30)
            
            current_util = self._analytics_service.calculate_worker_utilization(
                self._worker.id, start_date_30, end_date
            )
            
            if current_util:
                self._current_planned_label.setText(f"{current_util['hours_planned']:.1f} h")
                self._current_worked_label.setText(f"{current_util['hours_worked']:.1f} h")
                self._current_util_label.setText(f"{current_util['utilization_percent']:.1f}%")
                
                # Farbkodierung
                util = current_util['utilization_percent']
                if util < 80:
                    self._current_util_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
                elif util <= 110:
                    self._current_util_label.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")
                else:
                    self._current_util_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
            
            # Historische Auslastung (90 Tage)
            start_date_90 = end_date - timedelta(days=90)
            
            historical_util = self._analytics_service.calculate_worker_utilization(
                self._worker.id, start_date_90, end_date
            )
            
            if historical_util:
                self._hist_planned_label.setText(f"{historical_util['hours_planned']:.1f} h")
                self._hist_worked_label.setText(f"{historical_util['hours_worked']:.1f} h")
                self._hist_util_label.setText(f"{historical_util['utilization_percent']:.1f}%")
                
                # Farbkodierung
                util_hist = historical_util['utilization_percent']
                if util_hist < 80:
                    self._hist_util_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
                elif util_hist <= 110:
                    self._hist_util_label.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")
                else:
                    self._hist_util_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
            
            # Chart mit Einzel-Worker
            if current_util:
                self._detail_chart.update_chart([self._worker], {self._worker.id: current_util})
            
            # Zeiterfassungen laden
            self._load_time_entries()
            
            # Kapazitäten laden
            self._load_capacities()
            
        except Exception as e:
            print(f"Fehler beim Laden der Worker-Details: {e}")
    
    def _load_time_entries(self):
        """Lädt Zeiterfassungen für Worker"""
        try:
            # Letzte 90 Tage
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            entries = self._time_entry_repository.find_by_worker(
                self._worker.id, start_date, end_date
            )
            
            self._time_entries_table.setRowCount(0)
            
            for entry in sorted(entries, key=lambda e: e.date, reverse=True):
                row = self._time_entries_table.rowCount()
                self._time_entries_table.insertRow(row)
                
                # Datum
                date_item = QTableWidgetItem(entry.date.strftime("%d.%m.%Y"))
                self._time_entries_table.setItem(row, 0, date_item)
                
                # Dauer
                hours = entry.duration_minutes / 60
                duration_item = QTableWidgetItem(f"{hours:.2f} h")
                duration_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._time_entries_table.setItem(row, 1, duration_item)
                
                # Projekt
                project_item = QTableWidgetItem(entry.project or "-")
                self._time_entries_table.setItem(row, 2, project_item)
                
                # Beschreibung
                desc_item = QTableWidgetItem(entry.description)
                self._time_entries_table.setItem(row, 3, desc_item)
            
        except Exception as e:
            print(f"Fehler beim Laden der Zeiterfassungen: {e}")
    
    def _load_capacities(self):
        """Lädt Kapazitäten für Worker"""
        try:
            # Letzte 90 Tage
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            capacities = self._capacity_repository.find_by_date_range(
                start_date, end_date, worker_id=self._worker.id
            )
            
            self._capacities_table.setRowCount(0)
            
            for capacity in sorted(capacities, key=lambda c: c.date, reverse=True):
                row = self._capacities_table.rowCount()
                self._capacities_table.insertRow(row)
                
                # Datum
                date_item = QTableWidgetItem(capacity.date.strftime("%d.%m.%Y"))
                self._capacities_table.setItem(row, 0, date_item)
                
                # Stunden pro Tag
                hours_item = QTableWidgetItem(f"{capacity.hours_per_day:.1f} h")
                hours_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._capacities_table.setItem(row, 1, hours_item)
                
                # Beschreibung
                desc_item = QTableWidgetItem(capacity.description or "-")
                self._capacities_table.setItem(row, 2, desc_item)
            
        except Exception as e:
            print(f"Fehler beim Laden der Kapazitäten: {e}")
