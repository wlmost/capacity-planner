"""
Main Window
Haupt-Fenster der Anwendung
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from .time_entry_widget import TimeEntryWidget
from .worker_widget import WorkerWidget
from .capacity_widget import CapacityWidget
from .analytics_widget import AnalyticsWidget
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
        
        # Services und Repositories initialisieren
        self._init_services()
        
        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
    
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
        self.time_entry_widget = TimeEntryWidget(self.time_entry_viewmodel)
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
        
        export_action = QAction("&Exportieren...", self)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Ansicht-Menü
        view_menu = menubar.addMenu("&Ansicht")
        
        refresh_action = QAction("&Aktualisieren", self)
        view_menu.addAction(refresh_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("&Hilfe")
        
        about_action = QAction("&Über", self)
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
    
    def closeEvent(self, event):
        """Cleanup beim Schließen"""
        if hasattr(self, 'db_service'):
            self.db_service.close()
        event.accept()
