"""
Unit Tests für Dialoge (SettingsDialog, ProfileDialog, HelpDialog)
"""
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

from src.views.settings_dialog import SettingsDialog
from src.views.help_dialog import HelpDialog


@pytest.fixture(scope="module")
def qapp():
    """Qt Application für GUI-Tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def clean_settings():
    """Bereinigt QSettings vor jedem Test"""
    settings = QSettings("CapacityPlanner", "Settings")
    settings.clear()
    yield settings
    settings.clear()


class TestSettingsDialog:
    """Tests für SettingsDialog"""
    
    def test_dialog_creation(self, qapp, clean_settings):
        """Dialog kann erstellt werden"""
        dialog = SettingsDialog()
        assert dialog is not None
        assert dialog.windowTitle() == "Anwendungseinstellungen"
    
    def test_default_values(self, qapp, clean_settings):
        """Dialog hat korrekte Default-Werte"""
        dialog = SettingsDialog()
        
        # Worker-Modus
        assert dialog.worker_mode_combo.currentData() == "single"
        
        # Dark Mode
        assert dialog.dark_mode_checkbox.isChecked() is False
        
        # Autosave
        assert dialog.autosave_spinbox.value() == 5
    
    def test_load_saved_settings(self, qapp, clean_settings):
        """Gespeicherte Einstellungen werden geladen"""
        # Einstellungen speichern
        settings = QSettings("CapacityPlanner", "Settings")
        settings.setValue("worker_mode", "multi")
        settings.setValue("dark_mode", True)
        settings.setValue("autosave_interval", 10)
        
        # Dialog erstellen
        dialog = SettingsDialog()
        
        # Prüfen ob Werte geladen wurden
        assert dialog.worker_mode_combo.currentData() == "multi"
        assert dialog.dark_mode_checkbox.isChecked() is True
        assert dialog.autosave_spinbox.value() == 10
    
    def test_get_methods(self, qapp, clean_settings):
        """Get-Methoden geben korrekte Werte zurück"""
        dialog = SettingsDialog()
        
        # Default-Werte
        assert dialog.get_worker_mode() == "single"
        assert dialog.get_dark_mode() is False
        assert dialog.get_autosave_interval() == 5


class TestHelpDialog:
    """Tests für HelpDialog"""
    
    def test_dialog_creation(self, qapp):
        """Dialog kann erstellt werden"""
        dialog = HelpDialog()
        assert dialog is not None
        assert dialog.windowTitle() == "Bedienungshilfe"
    
    def test_dialog_has_tabs(self, qapp):
        """Dialog hat alle erwarteten Tabs"""
        from PySide6.QtWidgets import QTabWidget
        dialog = HelpDialog()
        
        # Dialog sollte ein Tab Widget haben
        tab_widget = dialog.findChild(QTabWidget)
        assert tab_widget is not None
        assert tab_widget.count() == 4  # Tutorial, Features, Shortcuts, FAQ
    
    def test_dialog_minimum_size(self, qapp):
        """Dialog hat Mindestgröße"""
        dialog = HelpDialog()
        assert dialog.minimumWidth() == 800
        assert dialog.minimumHeight() == 600


class TestWorkerDetailDialog:
    """Tests für WorkerDetailDialog"""
    
    @pytest.fixture
    def sample_worker(self):
        """Beispiel-Worker für Tests"""
        from datetime import datetime
        from src.models.worker import Worker
        return Worker(
            id=1,
            name="Max Mustermann",
            email="max@example.com",
            team="Development",
            active=True,
            created_at=datetime.now()
        )
    
    def test_dialog_creation(self, qapp, sample_worker):
        """Dialog kann mit Worker erstellt werden"""
        from src.views.worker_detail_dialog import WorkerDetailDialog
        from unittest.mock import Mock
        
        # Mock-Services
        analytics_service = Mock()
        time_entry_repo = Mock()
        capacity_repo = Mock()
        
        dialog = WorkerDetailDialog(
            sample_worker,
            analytics_service,
            time_entry_repo,
            capacity_repo
        )
        
        assert dialog is not None
        assert "Worker Details" in dialog.windowTitle()
        assert sample_worker.name in dialog.windowTitle()
    
    def test_pdf_export_button_exists(self, qapp, sample_worker):
        """PDF-Export Button ist vorhanden"""
        from src.views.worker_detail_dialog import WorkerDetailDialog
        from PySide6.QtWidgets import QPushButton
        from unittest.mock import Mock
        
        analytics_service = Mock()
        time_entry_repo = Mock()
        capacity_repo = Mock()
        
        dialog = WorkerDetailDialog(
            sample_worker,
            analytics_service,
            time_entry_repo,
            capacity_repo
        )
        
        # Suche nach PDF-Export Button
        buttons = dialog.findChildren(QPushButton)
        button_texts = [btn.text() for btn in buttons]
        
        # Button sollte vorhanden sein
        assert any("PDF" in text for text in button_texts)
