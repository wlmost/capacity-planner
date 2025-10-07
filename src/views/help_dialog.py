"""
Help Dialog
Dialog für Bedienungshilfe
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextBrowser, QTabWidget, QWidget
)
from PySide6.QtCore import Qt


class HelpDialog(QDialog):
    """
    Dialog für Bedienungshilfe
    
    Features:
        - Tutorial-Tab
        - Feature-Übersicht
        - Tastatur-Shortcuts
        - FAQ
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bedienungshilfe")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Erstellt UI-Komponenten"""
        layout = QVBoxLayout(self)
        
        # Tab Widget
        tab_widget = QTabWidget()
        
        # === Tutorial Tab ===
        tutorial_tab = self._create_tutorial_tab()
        tab_widget.addTab(tutorial_tab, "📖 Tutorial")
        
        # === Features Tab ===
        features_tab = self._create_features_tab()
        tab_widget.addTab(features_tab, "✨ Features")
        
        # === Shortcuts Tab ===
        shortcuts_tab = self._create_shortcuts_tab()
        tab_widget.addTab(shortcuts_tab, "⌨️ Shortcuts")
        
        # === FAQ Tab ===
        faq_tab = self._create_faq_tab()
        tab_widget.addTab(faq_tab, "❓ FAQ")
        
        layout.addWidget(tab_widget)
        
        # === Close Button ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _create_tutorial_tab(self) -> QWidget:
        """Erstellt Tutorial-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
            <h2>Willkommen beim Kapazitäts- & Auslastungsplaner!</h2>
            
            <h3>Erste Schritte</h3>
            <ol>
                <li><b>Workers anlegen:</b> Gehe zum Tab "Workers" und lege deine Mitarbeiter an</li>
                <li><b>Zeiterfassung:</b> Nutze den Tab "Zeiterfassung" um Arbeitszeiten zu erfassen</li>
                <li><b>Kapazität planen:</b> Im Tab "Kapazitätsplanung" kannst du geplante Stunden eintragen</li>
                <li><b>Auslastung analysieren:</b> Der Tab "Analytics" zeigt dir Auslastungs-Statistiken</li>
            </ol>
            
            <h3>Zeiterfassung</h3>
            <p>Die Zeiterfassung unterstützt flexible Eingaben:</p>
            <ul>
                <li><b>1:30</b> → 1 Stunde 30 Minuten (90 Minuten)</li>
                <li><b>90m</b> → 90 Minuten</li>
                <li><b>1.5h</b> → 1,5 Stunden (90 Minuten)</li>
                <li><b>2</b> → 2 Stunden (120 Minuten)</li>
            </ul>
            
            <h3>Worker Detail-Dialog</h3>
            <p>Doppelklick auf einen Worker im Analytics-Tab öffnet einen Detail-Dialog mit:</p>
            <ul>
                <li>Statistiken (30-Tage & 90-Tage Auslastung)</li>
                <li>Visualisierung als Chart</li>
                <li>Historie der Zeiterfassungen</li>
                <li>Kapazitätsplanung</li>
            </ul>
            
            <h3>Filter & Suche</h3>
            <p>Im Analytics-Tab kannst du:</p>
            <ul>
                <li>Nach <b>Team</b> filtern</li>
                <li>Nach <b>Auslastungs-Status</b> filtern (Unter/Optimal/Über)</li>
                <li>Tabellen durch Klick auf <b>Spalten-Header sortieren</b></li>
            </ul>
            
            <h3>Export-Funktionen</h3>
            <ul>
                <li><b>CSV-Export:</b> Exportiert Daten als Comma-Separated Values</li>
                <li><b>Excel-Export:</b> Erstellt formatierte .xlsx-Datei</li>
                <li><b>PDF-Export:</b> Exportiert Worker-Details als PDF (folgt)</li>
            </ul>
        """)
        
        layout.addWidget(browser)
        return widget
    
    def _create_features_tab(self) -> QWidget:
        """Erstellt Features-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
            <h2>Feature-Übersicht</h2>
            
            <h3>📊 Zeiterfassung</h3>
            <ul>
                <li>Split View: Formular (oben) + Liste aller Einträge (unten)</li>
                <li>Flexible Zeit-Eingabe mit Parser</li>
                <li>Typ-Auswahl: Arbeit, Urlaub, Abwesenheit</li>
                <li>Projekt mit Autovervollständigung</li>
                <li>Kategorie für zusätzliche Klassifizierung</li>
                <li>Löschen-Funktion mit Bestätigungsdialog</li>
                <li>Automatisches Refresh der Liste</li>
            </ul>
            
            <h3>👥 Worker-Management</h3>
            <ul>
                <li>CRUD-Operationen für Workers</li>
                <li>Verschlüsselte Datenspeicherung (RSA/AES)</li>
                <li>Tabelle mit Suche & Filter</li>
                <li>Status: Aktiv/Inaktiv</li>
                <li>Team-Zuordnung</li>
            </ul>
            
            <h3>📅 Kapazitätsplanung</h3>
            <ul>
                <li>Zeitraum-basierte Planung</li>
                <li>Geplante Stunden pro Monat</li>
                <li>Auslastungsberechnung in Echtzeit</li>
                <li>Farbkodierung: Orange (&lt;80%), Grün (80-110%), Rot (&gt;110%)</li>
                <li>Progress Bar mit Prozentanzeige</li>
            </ul>
            
            <h3>📈 Analytics Dashboard</h3>
            <ul>
                <li>Team-Übersicht mit Auslastung</li>
                <li>Filter: Team, Status (Unter/Optimal/Über)</li>
                <li>Sortierbare Tabellen</li>
                <li>Worker Detail-Dialog (Doppelklick)</li>
                <li>Chart-Visualisierung (QtCharts)</li>
                <li>CSV & Excel Export</li>
            </ul>
            
            <h3>⚙️ Einstellungen</h3>
            <ul>
                <li>Anwendungseinstellungen: Worker-Modus, Dark Mode, Autosave</li>
                <li>Profil-Dialog: Worker-spezifische Konfiguration</li>
                <li>Persistente Speicherung (QSettings)</li>
            </ul>
            
            <h3>🔐 Sicherheit</h3>
            <ul>
                <li>Hybrid-Verschlüsselung (RSA-2048 + AES-256)</li>
                <li>Verschlüsselte Worker-Daten (Name, Email)</li>
                <li>Lokale SQLite-Datenbank</li>
            </ul>
        """)
        
        layout.addWidget(browser)
        return widget
    
    def _create_shortcuts_tab(self) -> QWidget:
        """Erstellt Shortcuts-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        browser = QTextBrowser()
        browser.setHtml("""
            <h2>Tastatur-Shortcuts</h2>
            
            <h3>Globale Shortcuts</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="width: 100%">
                <tr style="background-color: #f0f0f0">
                    <th>Shortcut</th>
                    <th>Aktion</th>
                </tr>
                <tr>
                    <td><b>Ctrl+S</b></td>
                    <td>Sichern / Backup erstellen</td>
                </tr>
                <tr>
                    <td><b>Ctrl+Q</b></td>
                    <td>Anwendung beenden</td>
                </tr>
                <tr>
                    <td><b>F1</b></td>
                    <td>Bedienungshilfe öffnen</td>
                </tr>
            </table>
            
            <h3>Zeiterfassung</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="width: 100%">
                <tr style="background-color: #f0f0f0">
                    <th>Eingabe</th>
                    <th>Ergebnis</th>
                </tr>
                <tr>
                    <td><b>1:30</b></td>
                    <td>1 Stunde 30 Minuten (90 Minuten)</td>
                </tr>
                <tr>
                    <td><b>90m</b></td>
                    <td>90 Minuten</td>
                </tr>
                <tr>
                    <td><b>1.5h</b></td>
                    <td>1,5 Stunden (90 Minuten)</td>
                </tr>
                <tr>
                    <td><b>2</b></td>
                    <td>2 Stunden (120 Minuten)</td>
                </tr>
            </table>
            
            <h3>Navigation</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="width: 100%">
                <tr style="background-color: #f0f0f0">
                    <th>Aktion</th>
                    <th>Beschreibung</th>
                </tr>
                <tr>
                    <td><b>Tab-Wechsel</b></td>
                    <td>Klick auf Tab-Namen oder Ctrl+Tab</td>
                </tr>
                <tr>
                    <td><b>Doppelklick</b></td>
                    <td>Worker-Details öffnen (Analytics-Tab)</td>
                </tr>
                <tr>
                    <td><b>Spalten-Sortierung</b></td>
                    <td>Klick auf Tabellen-Header</td>
                </tr>
            </table>
            
            <h3>Tipps & Tricks</h3>
            <ul>
                <li>Nutze <b>Tab</b> zum schnellen Wechseln zwischen Feldern</li>
                <li><b>Enter</b> in Formularen speichert automatisch</li>
                <li>Nutze die <b>Autovervollständigung</b> bei Projekten</li>
                <li><b>Rechtsklick</b> auf Einträge für Kontext-Menü (folgt)</li>
            </ul>
        """)
        
        layout.addWidget(browser)
        return widget
    
    def _create_faq_tab(self) -> QWidget:
        """Erstellt FAQ-Tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
            <h2>Häufig gestellte Fragen (FAQ)</h2>
            
            <h3>Allgemein</h3>
            
            <h4>Wo werden meine Daten gespeichert?</h4>
            <p>Alle Daten werden lokal in einer SQLite-Datenbank gespeichert. 
            Die Datenbank befindet sich im Benutzerverzeichnis unter 
            <code>~/.capacity_planner/capacity_planner.db</code></p>
            
            <h4>Sind meine Daten verschlüsselt?</h4>
            <p>Ja! Worker-Daten (Name, Email) werden mit Hybrid-Verschlüsselung 
            (RSA-2048 + AES-256) gespeichert. Die Verschlüsselungsschlüssel liegen 
            in <code>~/.capacity_planner/keys/</code></p>
            
            <h4>Kann ich meine Daten exportieren?</h4>
            <p>Ja! Nutze die Export-Funktionen im Analytics-Tab:
            <ul>
                <li><b>CSV:</b> Für einfachen Datenaustausch</li>
                <li><b>Excel:</b> Für formatierte Berichte</li>
                <li><b>PDF:</b> Für Worker-Details (folgt)</li>
            </ul>
            </p>
            
            <h3>Zeiterfassung</h3>
            
            <h4>Welche Zeit-Formate werden unterstützt?</h4>
            <p>Der Parser erkennt mehrere Formate:
            <ul>
                <li><b>Stunden:Minuten</b> → 1:30, 2:45</li>
                <li><b>Minuten</b> → 90m, 120m</li>
                <li><b>Stunden (Dezimal)</b> → 1.5h, 2.25h</li>
                <li><b>Ganzzahl</b> → 2 (= 2 Stunden)</li>
            </ul>
            </p>
            
            <h4>Kann ich Einträge nachträglich bearbeiten?</h4>
            <p>Aktuell können Einträge nur gelöscht werden. Eine Edit-Funktion 
            folgt in einer späteren Version.</p>
            
            <h3>Analytics</h3>
            
            <h4>Wie wird die Auslastung berechnet?</h4>
            <p>Auslastung = (Gearbeitete Stunden / Geplante Stunden) × 100%
            <ul>
                <li><b>Unter</b> (&lt;80%): Orange</li>
                <li><b>Optimal</b> (80-110%): Grün</li>
                <li><b>Über</b> (&gt;110%): Rot</li>
            </ul>
            </p>
            
            <h4>Was zeigt der Worker Detail-Dialog?</h4>
            <p>Doppelklick auf einen Worker öffnet einen Dialog mit:
            <ul>
                <li>30-Tage und 90-Tage Statistiken</li>
                <li>Auslastungs-Chart (QtCharts)</li>
                <li>Historie aller Zeiterfassungen</li>
                <li>Kapazitätsplanung</li>
            </ul>
            </p>
            
            <h3>Probleme & Support</h3>
            
            <h4>Die Anwendung startet nicht</h4>
            <p>Prüfe ob alle Abhängigkeiten installiert sind:
            <code>pip install -r requirements.txt</code>
            </p>
            
            <h4>Wo finde ich weitere Hilfe?</h4>
            <p>
                <ul>
                    <li><b>GitHub:</b> <a href="https://github.com/wlmost/capacity-planner">github.com/wlmost/capacity-planner</a></li>
                    <li><b>Issues:</b> Melde Bugs oder Feature-Requests auf GitHub</li>
                </ul>
            </p>
        """)
        
        layout.addWidget(browser)
        return widget
