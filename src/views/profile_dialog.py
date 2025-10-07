"""
Profile Dialog
Dialog für Worker-Profil-Einstellungen
"""
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox,
    QPushButton, QGroupBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QSettings

from ..models.worker import Worker
from ..repositories.worker_repository import WorkerRepository


class ProfileDialog(QDialog):
    """
    Dialog für Worker-Profil-Einstellungen
    
    Features:
        - Worker-Auswahl (nur bei Mehrfach-Worker-Modus)
        - Worker-Stammdaten: Name, Email, Team, Status
        - Arbeitszeit-Konfiguration: Stunden/Tag, Jahresurlaub, Übertrag
        - Speichern/Laden von Profilen
    """
    
    def __init__(
        self, 
        worker_repository: WorkerRepository,
        parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Profil-Einstellungen")
        self.setMinimumWidth(600)
        
        self.worker_repository = worker_repository
        self.settings = QSettings("CapacityPlanner", "Settings")
        self._current_worker: Optional[Worker] = None
        self._workers = []
        
        self._setup_ui()
        self._load_workers()
    
    def _setup_ui(self):
        """Erstellt UI-Komponenten"""
        layout = QVBoxLayout(self)
        
        # === Worker-Auswahl ===
        worker_select_group = QGroupBox("Worker auswählen")
        worker_select_layout = QFormLayout(worker_select_group)
        
        self.worker_combo = QComboBox()
        self.worker_combo.currentIndexChanged.connect(self._on_worker_changed)
        worker_select_layout.addRow("Worker:", self.worker_combo)
        
        worker_info = QLabel(
            "ℹ️ <i>Wähle den Worker aus, dessen Profil du bearbeiten möchtest</i>"
        )
        worker_info.setWordWrap(True)
        worker_select_layout.addRow(worker_info)
        
        layout.addWidget(worker_select_group)
        
        # === Stammdaten ===
        personal_group = QGroupBox("Stammdaten")
        personal_layout = QFormLayout(personal_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("z.B. Max Mustermann")
        personal_layout.addRow("Name:*", self.name_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("z.B. max.mustermann@firma.de")
        personal_layout.addRow("E-Mail:*", self.email_input)
        
        self.team_input = QLineEdit()
        self.team_input.setPlaceholderText("z.B. Development")
        personal_layout.addRow("Team:", self.team_input)
        
        self.status_checkbox = QCheckBox("Aktiv")
        self.status_checkbox.setChecked(True)
        personal_layout.addRow("Status:", self.status_checkbox)
        
        layout.addWidget(personal_group)
        
        # === Arbeitszeit-Konfiguration ===
        work_group = QGroupBox("Arbeitszeit-Konfiguration")
        work_layout = QFormLayout(work_group)
        
        self.daily_hours_spinbox = QDoubleSpinBox()
        self.daily_hours_spinbox.setMinimum(1.0)
        self.daily_hours_spinbox.setMaximum(24.0)
        self.daily_hours_spinbox.setSingleStep(0.5)
        self.daily_hours_spinbox.setValue(8.0)
        self.daily_hours_spinbox.setSuffix(" h/Tag")
        work_layout.addRow("Regelarbeitszeit:*", self.daily_hours_spinbox)
        
        self.annual_vacation_spinbox = QSpinBox()
        self.annual_vacation_spinbox.setMinimum(0)
        self.annual_vacation_spinbox.setMaximum(365)
        self.annual_vacation_spinbox.setValue(30)
        self.annual_vacation_spinbox.setSuffix(" Tage")
        work_layout.addRow("Jahresurlaub:", self.annual_vacation_spinbox)
        
        self.vacation_carryover_spinbox = QSpinBox()
        self.vacation_carryover_spinbox.setMinimum(0)
        self.vacation_carryover_spinbox.setMaximum(365)
        self.vacation_carryover_spinbox.setValue(0)
        self.vacation_carryover_spinbox.setSuffix(" Tage")
        work_layout.addRow("Übertrag Vorjahr:", self.vacation_carryover_spinbox)
        
        work_info = QLabel(
            "ℹ️ <i>Diese Werte werden für Auslastungsberechnungen verwendet</i>"
        )
        work_info.setWordWrap(True)
        work_layout.addRow(work_info)
        
        layout.addWidget(work_group)
        
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
    
    def _load_workers(self):
        """Lädt alle Workers"""
        self._workers = self.worker_repository.find_all()
        
        self.worker_combo.clear()
        for worker in self._workers:
            display_text = f"{worker.name} ({worker.email})"
            if not worker.active:
                display_text += " [Inaktiv]"
            self.worker_combo.addItem(display_text, worker.id)
        
        # Ersten Worker auswählen wenn vorhanden
        if self._workers:
            self.worker_combo.setCurrentIndex(0)
    
    def _on_worker_changed(self, index: int):
        """Wird aufgerufen wenn Worker gewechselt wird"""
        if index < 0 or index >= len(self._workers):
            return
        
        self._current_worker = self._workers[index]
        self._load_worker_data()
    
    def _load_worker_data(self):
        """Lädt Daten des aktuellen Workers"""
        if not self._current_worker:
            return
        
        # Stammdaten
        self.name_input.setText(self._current_worker.name)
        self.email_input.setText(self._current_worker.email)
        self.team_input.setText(self._current_worker.team or "")
        self.status_checkbox.setChecked(self._current_worker.active)
        
        # Arbeitszeit-Konfiguration (aus QSettings laden)
        worker_id = self._current_worker.id
        daily_hours = self.settings.value(f"worker_{worker_id}_daily_hours", 8.0, type=float)
        annual_vacation = self.settings.value(f"worker_{worker_id}_annual_vacation", 30, type=int)
        vacation_carryover = self.settings.value(f"worker_{worker_id}_vacation_carryover", 0, type=int)
        
        self.daily_hours_spinbox.setValue(daily_hours)
        self.annual_vacation_spinbox.setValue(annual_vacation)
        self.vacation_carryover_spinbox.setValue(vacation_carryover)
    
    def _on_save(self):
        """Speichert Profil-Einstellungen"""
        if not self._current_worker:
            QMessageBox.warning(
                self,
                "Kein Worker ausgewählt",
                "Bitte wähle einen Worker aus."
            )
            return
        
        # Validierung
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        
        if not name:
            QMessageBox.warning(
                self,
                "Validierungsfehler",
                "Bitte gib einen Namen ein."
            )
            return
        
        if not email:
            QMessageBox.warning(
                self,
                "Validierungsfehler",
                "Bitte gib eine E-Mail-Adresse ein."
            )
            return
        
        # Worker-Stammdaten aktualisieren
        self._current_worker.name = name
        self._current_worker.email = email
        self._current_worker.team = self.team_input.text().strip() or None
        self._current_worker.active = self.status_checkbox.isChecked()
        
        # In Repository speichern
        try:
            success = self.worker_repository.update(self._current_worker)
            if not success:
                raise Exception("Update fehlgeschlagen")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler beim Speichern",
                f"Worker-Daten konnten nicht gespeichert werden:\n{str(e)}"
            )
            return
        
        # Arbeitszeit-Konfiguration in QSettings speichern
        worker_id = self._current_worker.id
        self.settings.setValue(f"worker_{worker_id}_daily_hours", self.daily_hours_spinbox.value())
        self.settings.setValue(f"worker_{worker_id}_annual_vacation", self.annual_vacation_spinbox.value())
        self.settings.setValue(f"worker_{worker_id}_vacation_carryover", self.vacation_carryover_spinbox.value())
        
        # Erfolgsmeldung
        QMessageBox.information(
            self,
            "Profil gespeichert",
            f"Profil für {name} wurde erfolgreich gespeichert."
        )
        
        self.accept()
