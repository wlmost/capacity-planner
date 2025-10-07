"""
WorkerDetailDialog - Detail-Ansicht für einzelne Workers
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QGroupBox, QFormLayout, QWidget,
    QFileDialog, QMessageBox
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
        
        # PDF-Export Button
        self._export_pdf_button = QPushButton("📄 Als PDF exportieren")
        self._export_pdf_button.clicked.connect(self._export_to_pdf)
        button_layout.addWidget(self._export_pdf_button)
        
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
    
    def _export_to_pdf(self):
        """Exportiert Worker-Details als PDF"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        import os
        
        # Dateinamen vorschlagen
        timestamp = datetime.now().strftime("%Y%m%d")
        worker_name_safe = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in self._worker.name)
        default_filename = f"worker_report_{worker_name_safe}_{timestamp}.pdf"
        
        # Datei-Dialog
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "PDF-Export speichern",
            default_filename,
            "PDF Files (*.pdf)"
        )
        
        if not filename:
            return  # Benutzer hat abgebrochen
        
        try:
            # PDF erstellen
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            
            # === SEITE 1: Header & Statistiken ===
            y_position = height - 2*cm
            
            # Header
            c.setFont("Helvetica-Bold", 20)
            c.drawString(2*cm, y_position, "Worker Report")
            y_position -= 0.8*cm
            
            # Datum
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, y_position, f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            y_position -= 1.5*cm
            
            # Worker-Informationen
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y_position, "Worker-Informationen")
            y_position -= 0.5*cm
            
            c.setFont("Helvetica", 11)
            worker_info = [
                f"Name: {self._worker.name}",
                f"Email: {self._worker.email}",
                f"Team: {self._worker.team or '-'}",
                f"Status: {'Aktiv' if self._worker.active else 'Inaktiv'}",
                f"Erstellt am: {self._worker.created_at.strftime('%d.%m.%Y %H:%M')}"
            ]
            
            for info in worker_info:
                y_position -= 0.6*cm
                c.drawString(2.5*cm, y_position, info)
            
            y_position -= 1.5*cm
            
            # Aktuelle Auslastung (30 Tage)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y_position, "Aktuelle Auslastung (30 Tage)")
            y_position -= 0.5*cm
            
            c.setFont("Helvetica", 11)
            current_stats = [
                f"Geplant: {self._current_planned_label.text()}",
                f"Gearbeitet: {self._current_worked_label.text()}",
                f"Auslastung: {self._current_util_label.text()}"
            ]
            
            for stat in current_stats:
                y_position -= 0.6*cm
                c.drawString(2.5*cm, y_position, stat)
            
            y_position -= 1.5*cm
            
            # Historische Auslastung (90 Tage)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y_position, "Historische Auslastung (90 Tage)")
            y_position -= 0.5*cm
            
            c.setFont("Helvetica", 11)
            hist_stats = [
                f"Geplant: {self._hist_planned_label.text()}",
                f"Gearbeitet: {self._hist_worked_label.text()}",
                f"Auslastung: {self._hist_util_label.text()}"
            ]
            
            for stat in hist_stats:
                y_position -= 0.6*cm
                c.drawString(2.5*cm, y_position, stat)
            
            y_position -= 2*cm
            
            # Zeiterfassungen Tabelle
            if self._time_entries_table.rowCount() > 0:
                c.setFont("Helvetica-Bold", 14)
                c.drawString(2*cm, y_position, "Zeiterfassungen (letzte 20)")
                y_position -= 0.8*cm
                
                # Tabellen-Daten sammeln
                table_data = [['Datum', 'Dauer', 'Projekt', 'Beschreibung']]
                max_rows = min(20, self._time_entries_table.rowCount())
                
                for row in range(max_rows):
                    row_data = [
                        self._time_entries_table.item(row, 0).text(),
                        self._time_entries_table.item(row, 1).text(),
                        self._time_entries_table.item(row, 2).text(),
                        self._time_entries_table.item(row, 3).text()[:30] + '...' if len(self._time_entries_table.item(row, 3).text()) > 30 else self._time_entries_table.item(row, 3).text()
                    ]
                    table_data.append(row_data)
                
                # Tabelle erstellen
                table = Table(table_data, colWidths=[3*cm, 2.5*cm, 4*cm, 7.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                # Tabelle zeichnen
                table_width, table_height = table.wrap(width, height)
                
                # Neue Seite wenn nicht genug Platz
                if y_position - table_height < 2*cm:
                    c.showPage()
                    y_position = height - 2*cm
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(2*cm, y_position, "Zeiterfassungen (Fortsetzung)")
                    y_position -= 0.8*cm
                
                table.drawOn(c, 2*cm, y_position - table_height)
                y_position -= table_height + 1*cm
            
            # === SEITE 2: Kapazitäten (falls vorhanden) ===
            if self._capacities_table.rowCount() > 0 and y_position < 8*cm:
                c.showPage()
                y_position = height - 2*cm
            
            if self._capacities_table.rowCount() > 0:
                if y_position > 8*cm:
                    y_position -= 1*cm
                
                c.setFont("Helvetica-Bold", 14)
                c.drawString(2*cm, y_position, "Kapazitätsplanung (letzte 20)")
                y_position -= 0.8*cm
                
                # Tabellen-Daten sammeln
                cap_data = [['Datum', 'Stunden/Tag', 'Beschreibung']]
                max_rows = min(20, self._capacities_table.rowCount())
                
                for row in range(max_rows):
                    row_data = [
                        self._capacities_table.item(row, 0).text(),
                        self._capacities_table.item(row, 1).text(),
                        self._capacities_table.item(row, 2).text()[:40] + '...' if len(self._capacities_table.item(row, 2).text()) > 40 else self._capacities_table.item(row, 2).text()
                    ]
                    cap_data.append(row_data)
                
                # Tabelle erstellen
                cap_table = Table(cap_data, colWidths=[3*cm, 3*cm, 11*cm])
                cap_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                # Tabelle zeichnen
                cap_width, cap_height = cap_table.wrap(width, height)
                
                if y_position - cap_height < 2*cm:
                    c.showPage()
                    y_position = height - 2*cm
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(2*cm, y_position, "Kapazitätsplanung (Fortsetzung)")
                    y_position -= 0.8*cm
                
                cap_table.drawOn(c, 2*cm, y_position - cap_height)
            
            # PDF speichern
            c.save()
            
            # Erfolgsmeldung
            file_size = os.path.getsize(filename) / 1024
            QMessageBox.information(
                self,
                "PDF-Export erfolgreich",
                f"Worker-Report wurde erfolgreich exportiert:\n\n{filename}\n\nGröße: {file_size:.1f} KB"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "PDF-Export fehlgeschlagen",
                f"Fehler beim Erstellen des PDFs:\n\n{str(e)}"
            )
