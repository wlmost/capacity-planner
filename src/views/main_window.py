"""
Main Window
Haupt-Fenster der Anwendung
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QLabel,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction

from .time_entry_widget import TimeEntryWidget
from .worker_widget import WorkerWidget
from .capacity_widget import CapacityWidget
from .analytics_widget import AnalyticsWidget
from .settings_dialog import SettingsDialog
from .profile_dialog import ProfileDialog
from .help_dialog import HelpDialog
from ..viewmodels.time_entry_viewmodel import TimeEntryViewModel
from ..viewmodels.worker_viewmodel import WorkerViewModel
from ..viewmodels.capacity_viewmodel import CapacityViewModel
from ..services.time_parser_service import TimeParserService
from ..services.database_service import DatabaseService
from ..services.crypto_service import CryptoService
from ..services.analytics_service import AnalyticsService
from ..repositories.time_entry_repository import TimeEntryRepository
from ..repositories.worker_repository import WorkerRepository
from ..repositories.capacity_repository import CapacityRepository


class MainWindow(QMainWindow):
    """
    Haupt-Fenster der Kapazitätsplaner-Anwendung
    
    Layout:
    - Menu Bar (Datei, Ansicht, Hilfe)
    - Tab Widget (Zeiterfassung, Kapazitätsplanung, Analytics)
    - Status Bar
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kapazitäts- & Auslastungsplaner")
        self.setMinimumSize(1024, 768)
        
        # Settings laden
        self.settings = QSettings("CapacityPlanner", "Settings")
        
        # Services und Repositories initialisieren
        self._init_services()
        
        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        
        # Dark Mode anwenden falls aktiviert
        self._apply_dark_mode()
    
    def _init_services(self):
        """Initialisiert Services und Repositories"""
        # Database Service
        self.db_service = DatabaseService()
        self.db_service.initialize()
        
        # Crypto Service
        self.crypto_service = CryptoService()
        self.crypto_service.initialize_keys()
        
        # Time Parser Service
        self.time_parser_service = TimeParserService()
        
        # Analytics Service
        self.analytics_service = AnalyticsService(self.db_service)
        
        # Repositories
        self.time_entry_repository = TimeEntryRepository(self.db_service)
        self.worker_repository = WorkerRepository(self.db_service, self.crypto_service)
        self.capacity_repository = CapacityRepository(self.db_service)
        
        # ViewModels
        self.time_entry_viewmodel = TimeEntryViewModel(
            self.time_parser_service,
            self.time_entry_repository
        )
        self.worker_viewmodel = WorkerViewModel(self.worker_repository)
        self.capacity_viewmodel = CapacityViewModel(
            self.capacity_repository,
            self.worker_repository,
            self.analytics_service
        )
    
    def _setup_ui(self):
        """Erstellt UI-Struktur"""
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        layout = QVBoxLayout(central_widget)
        
        # Tab Widget für verschiedene Ansichten
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Tabs (Platzhalter - werden später mit echten Widgets gefüllt)
        self._add_placeholder_tabs()
    
    def _add_placeholder_tabs(self):
        """Fügt Tabs mit echten Widgets hinzu"""
        # Tab 1: Zeiterfassung (mit echtem Widget)
        self.time_entry_widget = TimeEntryWidget(
            self.time_entry_viewmodel,
            self.time_entry_repository
        )
        self.time_entry_widget.entry_saved.connect(self._on_entry_saved)
        # Lade Workers für Dropdown
        workers = self.worker_repository.find_all()
        self.time_entry_widget.load_workers(workers)
        self.tab_widget.addTab(self.time_entry_widget, "Zeiterfassung")
        
        # Tab 2: Worker Management (mit echtem Widget)
        self.worker_widget = WorkerWidget(self.worker_viewmodel)
        self.tab_widget.addTab(self.worker_widget, "Workers")
        
        # Tab 3: Kapazitätsplanung (mit echtem Widget)
        self.capacity_widget = CapacityWidget(self.capacity_viewmodel)
        self.tab_widget.addTab(self.capacity_widget, "Kapazitätsplanung")
        
        # Tab 4: Analytics (mit echtem Widget)
        self.analytics_widget = AnalyticsWidget(
            self.analytics_service, 
            self.worker_repository,
            self.time_entry_repository,
            self.capacity_repository
        )
        self.tab_widget.addTab(self.analytics_widget, "Analytics")
    
    def _setup_menu(self):
        """Erstellt Menu Bar"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("&Datei")
        
        import_action = QAction("&Importieren...", self)
        import_action.triggered.connect(self._on_import)
        file_menu.addAction(import_action)
        
        save_action = QAction("&Sichern", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)
        
        export_action = QAction("&Exportieren...", self)
        export_action.triggered.connect(self._on_export)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self._on_exit)
        file_menu.addAction(exit_action)
        
        # Einstellungen-Menü
        settings_menu = menubar.addMenu("&Einstellungen")
        
        app_settings_action = QAction("&Anwendungseinstellungen...", self)
        app_settings_action.triggered.connect(self._show_app_settings)
        settings_menu.addAction(app_settings_action)
        
        profile_action = QAction("&Profil...", self)
        profile_action.triggered.connect(self._show_profile_dialog)
        settings_menu.addAction(profile_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("&Hilfe")
        
        help_action = QAction("&Bedienungshilfe", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&Über", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_statusbar(self):
        """Erstellt Status Bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Bereit")
    
    def _on_entry_saved(self, entry_id: int):
        """
        Callback wenn Zeiterfassung gespeichert wurde
        
        Args:
            entry_id: ID des gespeicherten Eintrags
        """
        self.statusbar.showMessage(f"Zeiterfassung erfolgreich gespeichert (ID: {entry_id})", 5000)
    
    # ===== Menü-Actions =====
    
    def _on_import(self):
        """Importiert Daten aus CSV/Excel"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Daten importieren",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if filename:
            # TODO: Import-Funktionalität implementieren
            QMessageBox.information(
                self,
                "Import",
                f"Import-Funktionalität folgt in einer späteren Version.\n\nGewählte Datei:\n{filename}"
            )
    
    def _on_save(self):
        """Erstellt Backup der Datenbank"""
        import os
        import shutil
        from datetime import datetime
        
        # Datenbank-Pfad ermitteln
        db_path = self.db_service.get_db_path()
        
        if not os.path.exists(db_path):
            QMessageBox.warning(
                self,
                "Backup fehlgeschlagen",
                "Datenbank-Datei nicht gefunden."
            )
            return
        
        # Backup-Ordner im Home-Verzeichnis
        backup_dir = os.path.join(os.path.expanduser("~"), ".capacity_planner", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup-Dateiname mit Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"capacity_planner_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            # Datenbank kopieren
            shutil.copy2(db_path, backup_path)
            
            # Erfolgsmeldung
            QMessageBox.information(
                self,
                "Backup erfolgreich",
                f"Datenbank-Backup wurde erstellt:\n\n{backup_path}\n\n"
                f"Größe: {os.path.getsize(backup_path) / 1024:.1f} KB"
            )
            
            self.statusbar.showMessage(f"Backup erstellt: {backup_filename}", 5000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup fehlgeschlagen",
                f"Fehler beim Erstellen des Backups:\n\n{str(e)}"
            )
    
    def _on_export(self):
        """Exportiert Daten"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Daten exportieren",
            "capacity_planner_export.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )
        
        if filename:
            # TODO: Export-Funktionalität implementieren
            QMessageBox.information(
                self,
                "Export",
                f"Export-Funktionalität folgt in einer späteren Version.\n\nZieldatei:\n{filename}"
            )
    
    def _on_exit(self):
        """Beendet die Anwendung"""
        # Prüfen ob ungespeicherte Änderungen vorhanden (später)
        reply = QMessageBox.question(
            self,
            "Beenden",
            "Möchtest du die Anwendung wirklich beenden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
    
    def _show_app_settings(self):
        """Zeigt Anwendungseinstellungen-Dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Dark Mode ggf. neu anwenden
            self._apply_dark_mode()
    
    def _show_profile_dialog(self):
        """Zeigt Profil-Dialog"""
        dialog = ProfileDialog(self.worker_repository, self)
        if dialog.exec():
            # Nach Speichern Worker-Daten neu laden
            workers = self.worker_repository.find_all()
            self.time_entry_widget.load_workers(workers)
    
    def _show_help(self):
        """Zeigt Bedienungshilfe"""
        dialog = HelpDialog(self)
        dialog.exec()
    
    def _show_about(self):
        """Zeigt Über-Dialog"""
        QMessageBox.about(
            self,
            "Über Capacity Planner",
            """<h3>Kapazitäts- & Auslastungsplaner</h3>
            <p>Version 1.0.0</p>
            <p>Eine PySide6-Desktopanwendung für Windows zur Erfassung 
            und Auswertung von Arbeitszeiten und Kapazitäten.</p>
            <p><b>Entwickelt mit:</b><br>
            Python 3.12 • PySide6 6.9.3 • SQLite</p>
            <p><b>Autor:</b> wlmost<br>
            <b>GitHub:</b> <a href='https://github.com/wlmost/capacity-planner'>
            github.com/wlmost/capacity-planner</a></p>
            """
        )
    
    def _apply_dark_mode(self):
        """Wendet Dark Mode an falls aktiviert"""
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        
        if dark_mode:
            # Dark Mode Stylesheet
            dark_stylesheet = """
                QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QMainWindow {
                    background-color: #2b2b2b;
                }
                QTabWidget::pane {
                    border: 1px solid #3a3a3a;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    padding: 8px 16px;
                    border: 1px solid #4a4a4a;
                }
                QTabBar::tab:selected {
                    background-color: #4a4a4a;
                    border-bottom-color: #4a4a4a;
                }
                QTabBar::tab:hover {
                    background-color: #454545;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border-bottom: 1px solid #3a3a3a;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #3a3a3a;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border: 1px solid #3a3a3a;
                }
                QMenu::item:selected {
                    background-color: #3a3a3a;
                }
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    border-top: 1px solid #3a3a3a;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #4a4a4a;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #454545;
                }
                QPushButton:pressed {
                    background-color: #4a4a4a;
                }
                QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QComboBox {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #4a4a4a;
                    padding: 4px;
                    border-radius: 3px;
                }
                QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                    border: 1px solid #5a8fd6;
                }
                QTableWidget {
                    background-color: #2b2b2b;
                    alternate-background-color: #323232;
                    color: #e0e0e0;
                    gridline-color: #3a3a3a;
                    border: 1px solid #3a3a3a;
                }
                QTableWidget::item {
                    padding: 4px;
                }
                QTableWidget::item:selected {
                    background-color: #4a4a4a;
                }
                QHeaderView::section {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    padding: 6px;
                    border: 1px solid #4a4a4a;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QGroupBox {
                    border: 1px solid #4a4a4a;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 8px;
                    color: #e0e0e0;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 4px;
                    color: #e0e0e0;
                }
                QCheckBox {
                    color: #e0e0e0;
                }
                QScrollBar:vertical {
                    background-color: #2b2b2b;
                    width: 14px;
                }
                QScrollBar::handle:vertical {
                    background-color: #4a4a4a;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #5a5a5a;
                }
                QProgressBar {
                    background-color: #3a3a3a;
                    border: 1px solid #4a4a4a;
                    border-radius: 4px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #5a8fd6;
                    border-radius: 3px;
                }
            """
            self.setStyleSheet(dark_stylesheet)
            self.statusbar.showMessage("Dark Mode aktiviert", 3000)
        else:
            # Light Mode (Standard)
            self.setStyleSheet("")
            self.statusbar.showMessage("Light Mode aktiviert", 3000)
    
    def closeEvent(self, event):
        """Cleanup beim Schließen"""
        if hasattr(self, 'db_service'):
            self.db_service.close()
        event.accept()
