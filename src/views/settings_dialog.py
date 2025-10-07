"""
Settings Dialog
Dialog für Anwendungseinstellungen
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QPushButton, QGroupBox,
    QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QSettings


class SettingsDialog(QDialog):
    """
    Dialog für Anwendungseinstellungen
    
    Features:
        - Einzel-/Mehrfach-Worker-Modus
        - Dark/Light Mode Toggle
        - Autosave-Intervall
        - Einstellungen werden persistent gespeichert (QSettings)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Anwendungseinstellungen")
        self.setMinimumWidth(500)
        
        # QSettings für persistente Speicherung
        self.settings = QSettings("CapacityPlanner", "Settings")
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Erstellt UI-Komponenten"""
        layout = QVBoxLayout(self)
        
        # === Worker-Modus ===
        worker_group = QGroupBox("Worker-Modus")
        worker_layout = QFormLayout(worker_group)
        
        self.worker_mode_combo = QComboBox()
        self.worker_mode_combo.addItem("Einzelworker", "single")
        self.worker_mode_combo.addItem("Mehrfach-Worker", "multi")
        worker_layout.addRow("Modus:", self.worker_mode_combo)
        
        worker_info = QLabel(
            "ℹ️ <i>Einzelworker: Anwendung für einen Worker optimiert<br>"
            "Mehrfach-Worker: Verwaltung mehrerer Workers mit Team-Ansichten</i>"
        )
        worker_info.setWordWrap(True)
        worker_layout.addRow(worker_info)
        
        layout.addWidget(worker_group)
        
        # === Darstellung ===
        display_group = QGroupBox("Darstellung")
        display_layout = QFormLayout(display_group)
        
        self.dark_mode_checkbox = QCheckBox("Dark Mode aktivieren")
        display_layout.addRow(self.dark_mode_checkbox)
        
        display_info = QLabel(
            "ℹ️ <i>Dark Mode wird nach Neustart der Anwendung aktiv</i>"
        )
        display_info.setWordWrap(True)
        display_layout.addRow(display_info)
        
        layout.addWidget(display_group)
        
        # === Autosave ===
        autosave_group = QGroupBox("Automatisches Speichern")
        autosave_layout = QFormLayout(autosave_group)
        
        self.autosave_spinbox = QSpinBox()
        self.autosave_spinbox.setMinimum(1)
        self.autosave_spinbox.setMaximum(60)
        self.autosave_spinbox.setSuffix(" Minuten")
        self.autosave_spinbox.setValue(5)
        autosave_layout.addRow("Intervall:", self.autosave_spinbox)
        
        autosave_info = QLabel(
            "ℹ️ <i>Zeitraum für automatische Datensicherung (in Zukunft)</i>"
        )
        autosave_info.setWordWrap(True)
        autosave_layout.addRow(autosave_info)
        
        layout.addWidget(autosave_group)
        
        # === Buttons ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("💾 Speichern")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("❌ Abbrechen")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _load_settings(self):
        """Lädt gespeicherte Einstellungen"""
        # Worker-Modus
        worker_mode = self.settings.value("worker_mode", "single")
        index = self.worker_mode_combo.findData(worker_mode)
        if index >= 0:
            self.worker_mode_combo.setCurrentIndex(index)
        
        # Dark Mode
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        self.dark_mode_checkbox.setChecked(dark_mode)
        
        # Autosave
        autosave_interval = self.settings.value("autosave_interval", 5, type=int)
        self.autosave_spinbox.setValue(autosave_interval)
    
    def _on_save(self):
        """Speichert Einstellungen"""
        # Worker-Modus
        worker_mode = self.worker_mode_combo.currentData()
        self.settings.setValue("worker_mode", worker_mode)
        
        # Dark Mode
        dark_mode = self.dark_mode_checkbox.isChecked()
        self.settings.setValue("dark_mode", dark_mode)
        
        # Autosave
        autosave_interval = self.autosave_spinbox.value()
        self.settings.setValue("autosave_interval", autosave_interval)
        
        # Erfolgsmeldung
        QMessageBox.information(
            self,
            "Einstellungen gespeichert",
            "Die Einstellungen wurden erfolgreich gespeichert.\n\n"
            "Einige Änderungen werden erst nach einem Neustart der Anwendung aktiv."
        )
        
        self.accept()
    
    def get_worker_mode(self) -> str:
        """Gibt aktuellen Worker-Modus zurück"""
        return self.settings.value("worker_mode", "single")
    
    def get_dark_mode(self) -> bool:
        """Gibt Dark Mode Status zurück"""
        return self.settings.value("dark_mode", False, type=bool)
    
    def get_autosave_interval(self) -> int:
        """Gibt Autosave-Intervall zurück"""
        return self.settings.value("autosave_interval", 5, type=int)
