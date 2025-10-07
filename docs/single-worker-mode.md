# Single-Worker-Mode Feature

## Überblick

Der **Single-Worker-Mode** ermöglicht es Benutzern, sich als spezifischer Worker anzumelden und nur ihre eigenen Daten zu sehen und zu bearbeiten. Ein zusätzlicher **Admin-Mode** erlaubt die Ansicht aller Worker-Daten (nur Analyse/Reports, keine Zeiterfassung).

## Sinn & Zweck

### Warum?
- **Datenschutz:** Jeder Worker sieht nur seine eigenen Zeiterfassungen
- **Benutzerfreundlichkeit:** Keine versehentliche Zeiterfassung für andere Worker
- **Übersichtlichkeit:** Fokus auf eigene Daten
- **Flexibilität:** Admin-Zugang für Management und Reporting

### Anwendungsfälle
1. **Worker-Mode:** Mitarbeiter erfasst eigene Arbeitszeit
2. **Admin-Mode:** Team-Lead sieht Übersicht aller Mitarbeiter
3. **Wechsel:** Abmelden und als anderer Worker anmelden

## Alternativen (nicht gewählt)

### Alternative 1: Multi-User-Modus mit Rechten-System
- ❌ Zu komplex für kleine Teams
- ❌ Benötigt User-Management, Passwörter, etc.
- ✅ Unser Ansatz: Einfache Worker-Auswahl ohne Passwort

### Alternative 2: Immer alle Worker sichtbar
- ❌ Unübersichtlich für einzelne Mitarbeiter
- ❌ Gefahr von Fehleinträgen
- ✅ Unser Ansatz: Fokussierte Ansicht pro Worker

### Alternative 3: Nur Admin-Mode
- ❌ Keine Personalisierung
- ❌ Worker-Dropdown bei jeder Zeiterfassung
- ✅ Unser Ansatz: Automatische Worker-Vorwahl

## Funktionsweise

### 1. Login-Dialog beim Start

```python
# LoginDialog (src/views/login_dialog.py)
class LoginDialog(QDialog):
    """
    Dialog zur Worker-Auswahl beim Anwendungsstart
    
    Features:
    - Eingabefeld mit Autovervollständigung (Name oder Email)
    - Checkbox "Als Admin anmelden"
    - Checkbox "Anmeldung merken"
    - Validierung gegen Datenbank
    """
```

**Ablauf:**
1. User gibt Name oder Email ein (z.B. "Max" oder "max@example.com")
2. Autovervollständigung schlägt passende Worker vor
3. Optional: Admin-Checkbox aktivieren
4. Dialog validiert und gibt Worker-ID zurück (oder None bei Admin)

### 2. Session-Management

```python
# SessionService (src/services/session_service.py)
class SessionService:
    """
    Verwaltet aktuelle Worker-Session
    
    Funktionen:
    - login(worker_id, is_admin, remember)
    - logout()
    - get_current_worker() -> Optional[Worker]
    - is_admin_mode() -> bool
    - load_saved_session() -> Optional[tuple]
    """
```

**Speicherort:** `settings.json`
```json
{
  "last_worker_id": 5,
  "is_admin": false,
  "remember_login": true
}
```

### 3. UI-Anpassungen

#### Time Entry Widget
```python
def _setup_for_mode(self):
    """Passt UI an Worker/Admin-Mode an"""
    if self.session.is_admin_mode():
        # Admin: Kein Time Entry erlaubt
        self.setEnabled(False)
        self.show_info("⚠️ Zeiterfassung nur im Worker-Mode verfügbar")
    else:
        # Worker: Dropdown verstecken, Worker vorgewählt
        worker = self.session.get_current_worker()
        self.worker_combo.setVisible(False)
        self.worker_label.setText(f"Worker: {worker.name}")
```

#### Workers Tab
```python
def _load_workers(self):
    """Lädt Worker basierend auf Modus"""
    if self.session.is_admin_mode():
        workers = self.viewmodel.get_all_workers()
    else:
        worker = self.session.get_current_worker()
        workers = [worker] if worker else []
    
    self._display_workers(workers)
```

#### Analytics Widget
```python
def _fetch_analytics_data(self):
    """Filtert Analytics nach aktuellem Worker"""
    if self.session.is_admin_mode():
        # Alle Worker
        data = self.viewmodel.get_team_analytics()
    else:
        # Nur aktueller Worker
        worker_id = self.session.get_current_worker().id
        data = self.viewmodel.get_worker_analytics(worker_id)
```

### 4. Menü-Erweiterungen

```python
# Hauptmenü erweitert um:
file_menu.addSeparator()
logout_action = file_menu.addAction("Abmelden")
logout_action.triggered.connect(self._on_logout)

# Status in der Statusleiste:
self.statusBar().showMessage(f"Angemeldet als: {worker.name}")
# oder
self.statusBar().showMessage("Angemeldet als: Administrator")
```

## Implementierungsdetails

### Dateistruktur

```
src/
├── services/
│   └── session_service.py       # NEU: Session-Management
├── views/
│   ├── login_dialog.py          # NEU: Login-Dialog
│   ├── main_window.py           # ÄNDERN: Session-Integration
│   ├── time_entry_widget.py     # ÄNDERN: Mode-Aware
│   ├── worker_widget.py         # ÄNDERN: Filtern nach Mode
│   └── analytics_widget.py      # ÄNDERN: Filtern nach Mode

tests/
└── ui_automation/
    └── test_single_worker_mode.py  # NEU: Tests für Feature
```

### Datenfluss

```
Start → LoginDialog
         ↓
    SessionService.login(worker_id, is_admin)
         ↓
    MainWindow.setup_with_session()
         ↓
    Widgets.configure_for_mode()
         ↓
    [Worker nutzt App]
         ↓
    Menü: Abmelden
         ↓
    SessionService.logout()
         ↓
    LoginDialog (neu anzeigen)
```

## Code-Beispiele

### 1. Login-Dialog verwenden

```python
# In main.py
from src.views.login_dialog import LoginDialog
from src.services.session_service import SessionService

app = QApplication(sys.argv)

# Session-Service initialisieren
session = SessionService()

# Gespeicherte Session laden (falls "Merken" aktiviert)
saved_session = session.load_saved_session()
if saved_session:
    worker_id, is_admin = saved_session
    session.login(worker_id, is_admin, remember=True)
else:
    # Login-Dialog anzeigen
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        worker_id = login_dialog.selected_worker_id
        is_admin = login_dialog.is_admin
        remember = login_dialog.remember_login
        session.login(worker_id, is_admin, remember)
    else:
        sys.exit(0)  # User hat abgebrochen

# Hauptfenster mit Session starten
window = MainWindow(session)
window.show()
```

### 2. Time Entry im Worker-Mode

```python
class TimeEntryWidget(QWidget):
    def __init__(self, session: SessionService):
        self.session = session
        super().__init__()
        self._setup_ui()
        self._configure_for_mode()
    
    def _configure_for_mode(self):
        if self.session.is_admin_mode():
            # Admin kann keine Zeit erfassen
            self.setEnabled(False)
            info_label = QLabel("⚠️ Zeiterfassung nur im Worker-Mode")
            self.layout().insertWidget(0, info_label)
        else:
            # Worker: Dropdown verstecken, Worker ist vorgewählt
            worker = self.session.get_current_worker()
            self.worker_combo.setVisible(False)
            
            # Label statt Dropdown
            worker_label = QLabel(f"👤 {worker.name}")
            worker_label.setStyleSheet("font-weight: bold;")
            # ... Layout anpassen
    
    def _on_save_clicked(self):
        # Worker-ID automatisch aus Session
        worker_id = self.session.get_current_worker().id
        # ... Rest der Speicherfunktion
```

### 3. Analytics mit Filterung

```python
class AnalyticsWidget(QWidget):
    def _load_analytics(self):
        date_from = self.date_range.start_date
        date_to = self.date_range.end_date
        
        if self.session.is_admin_mode():
            # Admin: Alle Worker
            data = self.analytics_service.get_team_overview(date_from, date_to)
            self.title_label.setText("📊 Team-Übersicht (Alle Worker)")
        else:
            # Worker: Nur eigene Daten
            worker = self.session.get_current_worker()
            data = self.analytics_service.get_worker_overview(
                worker.id, date_from, date_to
            )
            self.title_label.setText(f"📊 Meine Übersicht ({worker.name})")
        
        self._display_data(data)
```

### 4. Abmelden-Funktion

```python
class MainWindow(QMainWindow):
    def _create_menus(self):
        file_menu = self.menuBar().addMenu("&Datei")
        
        # ... andere Aktionen
        
        file_menu.addSeparator()
        
        logout_action = QAction("🚪 Abmelden", self)
        logout_action.setShortcut("Ctrl+Q")
        logout_action.triggered.connect(self._on_logout)
        file_menu.addAction(logout_action)
    
    def _on_logout(self):
        """Abmelden und Login-Dialog anzeigen"""
        reply = QMessageBox.question(
            self,
            "Abmelden",
            "Möchtest du dich wirklich abmelden?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.session.logout()
            self.close()
            
            # Login-Dialog neu anzeigen
            login_dialog = LoginDialog()
            if login_dialog.exec() == QDialog.Accepted:
                # Neu einloggen
                self.session.login(
                    login_dialog.selected_worker_id,
                    login_dialog.is_admin,
                    login_dialog.remember_login
                )
                # Neues Hauptfenster
                new_window = MainWindow(self.session)
                new_window.show()
```

## Testing-Strategie

### Test 1: Login-Dialog
```python
def test_login_dialog_worker_selection():
    """Test Worker-Auswahl im Login-Dialog"""
    dialog = LoginDialog()
    
    # Name eingeben
    dialog.name_input.setText("Max")
    
    # Erster Vorschlag auswählen
    assert dialog.name_input.completer().completionCount() > 0
    
    # Admin nicht aktiviert
    assert not dialog.admin_checkbox.isChecked()
    
    # Dialog akzeptieren
    dialog.accept()
    assert dialog.selected_worker_id is not None
```

### Test 2: Single-Worker-Mode
```python
def test_time_entry_in_worker_mode():
    """Test Zeiterfassung im Worker-Mode"""
    session = SessionService()
    session.login(worker_id=1, is_admin=False)
    
    widget = TimeEntryWidget(session)
    
    # Worker-Dropdown sollte versteckt sein
    assert not widget.worker_combo.isVisible()
    
    # Zeiterfassung sollte enabled sein
    assert widget.isEnabled()
    
    # Worker sollte vorgewählt sein
    assert session.get_current_worker().id == 1
```

### Test 3: Admin-Mode
```python
def test_time_entry_disabled_in_admin_mode():
    """Test dass Zeiterfassung im Admin-Mode deaktiviert ist"""
    session = SessionService()
    session.login(worker_id=None, is_admin=True)
    
    widget = TimeEntryWidget(session)
    
    # Zeiterfassung sollte disabled sein
    assert not widget.isEnabled()
    
    # Warnung sollte sichtbar sein
    info_labels = widget.findChildren(QLabel)
    assert any("nur im Worker-Mode" in label.text() for label in info_labels)
```

## Migration bestehender Daten

Keine Migration nötig! Das Feature ist **opt-in** und abwärtskompatibel:
- Ohne gespeicherte Session: Login-Dialog erscheint
- Mit gespeicherter Session: Automatischer Login
- Alte Daten bleiben unverändert

## Best Practices

1. **Session immer prüfen:**
   ```python
   if not self.session.is_logged_in():
       raise RuntimeError("Keine aktive Session")
   ```

2. **Admin-Checks konsequent:**
   ```python
   if self.session.is_admin_mode() and requires_worker_mode:
       QMessageBox.warning(self, "Hinweis", "Funktion nur im Worker-Mode")
       return
   ```

3. **Defensive Programmierung:**
   ```python
   worker = self.session.get_current_worker()
   if not worker:
       # Fallback oder Fehlerbehandlung
   ```

## Zukünftige Erweiterungen

### Phase 1 (aktuell)
- ✅ Login-Dialog mit Worker-Auswahl
- ✅ Session-Management
- ✅ Worker/Admin-Mode
- ✅ Abmelden-Funktion

### Phase 2 (optional)
- 🔮 Passwort-Schutz (optional)
- 🔮 Multi-Workspace (verschiedene Datenbanken)
- 🔮 Cloud-Sync für persönliche Daten
- 🔮 Offline-Modus mit Sync

### Phase 3 (optional)
- 🔮 OAuth/SSO-Integration
- 🔮 Mobile App mit gleichem Login
- 🔮 Audit-Log (wer hat was geändert)

## Performance-Überlegungen

- **Login-Dialog:** < 500ms Startup-Zeit
- **Session-Load:** Cached, kein DB-Zugriff bei jedem Check
- **Filter-Queries:** Indiziert auf `worker_id`
- **UI-Updates:** Nur betroffene Widgets neu laden

## Sicherheit

⚠️ **Hinweis:** Aktuell KEIN Passwort-Schutz!
- Jeder kann sich als beliebiger Worker anmelden
- Geeignet für vertrauenswürdige Umgebungen (kleines Team)
- Für Multi-User mit Sicherheit: Passwort-Feature implementieren (Phase 2)

## Zusammenfassung

Das **Single-Worker-Mode Feature** bietet:
- ✅ Personalisierte Ansicht für jeden Worker
- ✅ Admin-Modus für Team-Übersicht
- ✅ Einfache Bedienung ohne Passwörter
- ✅ Session-Persistenz ("Merken")
- ✅ Klare Trennung: Worker erfasst, Admin analysiert
- ✅ Abmelden und Neuanmeldung jederzeit möglich

**Status:** Ready for Implementation 🚀
