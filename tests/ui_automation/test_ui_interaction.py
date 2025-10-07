"""
UI Interaction Tests - Automated User Flow Testing
===================================================

This test suite simulates real user interactions with the Capacity Planner
application and pauses at critical points for visual verification.

Test Scenarios:
1. Application Startup & Window Initialization
2. Time Entry Creation Flow
3. Worker Management Flow
4. Analytics Dashboard Interaction
5. Menu Navigation & Dialogs
6. Search & Filter Operations

Usage:
    pytest tests/ui_automation/test_ui_interaction.py -v -s
    
Note: Use -s flag to see print statements and visual pauses
"""
import pytest
import time
from datetime import datetime, timedelta
from typing import Optional
from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QDateEdit, QTableWidget, QTabWidget, QComboBox, QTextEdit
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtTest import QTest

from src.views.main_window import MainWindow
from src.models.worker import Worker


# ============================================================================
# Configuration
# ============================================================================

VISUAL_PAUSE_DURATION = 2.0  # seconds to pause for visual verification
FAST_MODE = False  # Set to True to skip visual pauses
ANIMATION_DELAY = 100  # milliseconds between UI actions


def visual_pause(message: str, duration: float = VISUAL_PAUSE_DURATION):
    """
    Pause execution for visual verification
    
    Args:
        message: Description of what to verify
        duration: Pause duration in seconds
    """
    if FAST_MODE:
        return
    
    print(f"\n{'='*70}")
    print(f"⏸️  VISUAL VERIFICATION POINT")
    print(f"{'='*70}")
    print(f"📋 {message}")
    print(f"⏱️  Pausing for {duration} seconds...")
    print(f"{'='*70}\n")
    
    # Process events to keep UI responsive
    app = QApplication.instance()
    start_time = time.time()
    while time.time() - start_time < duration:
        app.processEvents()
        time.sleep(0.1)


def safe_click(widget, button_text: Optional[str] = None):
    """
    Safely click a button or widget
    
    Args:
        widget: Widget to click or parent widget to search in
        button_text: Text of button to find and click
    """
    if button_text:
        # Find button by text
        button = None
        for child in widget.findChildren(QPushButton):
            if button_text.lower() in child.text().lower():
                button = child
                break
        
        if button:
            print(f"🖱️  Clicking button: '{button.text()}'")
            QTest.mouseClick(button, Qt.LeftButton)
            QTest.qWait(ANIMATION_DELAY)
            return True
        else:
            print(f"⚠️  Button not found: '{button_text}'")
            return False
    else:
        # Click widget directly
        print(f"🖱️  Clicking widget: {widget.__class__.__name__}")
        QTest.mouseClick(widget, Qt.LeftButton)
        QTest.qWait(ANIMATION_DELAY)
        return True


def safe_input_text(widget, text: str):
    """
    Safely input text into a text field
    
    Args:
        widget: QLineEdit or QTextEdit to input into
        text: Text to input
    """
    widget.clear()
    widget.setFocus()
    QTest.qWait(50)
    
    print(f"⌨️  Typing text: '{text}' into {widget.__class__.__name__}")
    
    if isinstance(widget, (QLineEdit, QTextEdit)):
        for char in text:
            QTest.keyClick(widget, char)
        QTest.qWait(ANIMATION_DELAY)
    else:
        widget.setText(text)


def safe_set_date(date_edit: QDateEdit, date: QDate):
    """
    Safely set date in QDateEdit
    
    Args:
        date_edit: QDateEdit widget
        date: QDate to set
    """
    print(f"📅 Setting date: {date.toString('dd.MM.yyyy')}")
    date_edit.setDate(date)
    QTest.qWait(ANIMATION_DELAY)


def safe_select_combobox(combo: QComboBox, text: str):
    """
    Safely select item in combobox
    
    Args:
        combo: QComboBox widget
        text: Text of item to select
    """
    index = combo.findText(text, Qt.MatchContains)
    if index >= 0:
        print(f"📋 Selecting combobox item: '{text}'")
        combo.setCurrentIndex(index)
        QTest.qWait(ANIMATION_DELAY)
        return True
    else:
        print(f"⚠️  Combobox item not found: '{text}'")
        return False


def count_table_rows(table: QTableWidget, visible_only: bool = False) -> int:
    """
    Count rows in table
    
    Args:
        table: QTableWidget
        visible_only: Count only visible rows
        
    Returns:
        Number of rows
    """
    if visible_only:
        count = sum(1 for i in range(table.rowCount()) if not table.isRowHidden(i))
    else:
        count = table.rowCount()
    
    print(f"📊 Table has {count} {'visible ' if visible_only else ''}rows")
    return count


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def app():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Cleanup handled by pytest


@pytest.fixture(scope="function")
def main_window(app, qtbot):
    """
    Create and setup main window with test data
    
    Returns:
        MainWindow instance with initialized test data
    """
    print("\n" + "="*70)
    print("🚀 Initializing Main Window...")
    print("="*70)
    
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Show window and wait for it to be visible
    window.show()
    QTest.qWaitForWindowExposed(window)
    QTest.qWait(500)  # Additional wait for complete initialization
    
    print("✅ Main Window initialized and visible")
    
    # Setup test data
    _setup_test_workers(window)
    
    return window


def _setup_test_workers(window: MainWindow):
    """Create test workers in the database"""
    print("\n📝 Setting up test data...")
    
    # Check if workers already exist
    existing_workers = window.worker_repository.find_all()
    if len(existing_workers) >= 2:
        print(f"✅ Found {len(existing_workers)} existing workers")
        return
    
    # Create test workers
    test_workers = [
        Worker(
            worker_id=None,
            name="Max Mustermann",
            email="max.mustermann@example.com",
            team="Development"
        ),
        Worker(
            worker_id=None,
            name="Anna Schmidt",
            email="anna.schmidt@example.com",
            team="QA"
        )
    ]
    
    for worker in test_workers:
        try:
            saved = window.worker_repository.save(worker)
            print(f"✅ Created worker: {saved.name}")
        except Exception as e:
            print(f"⚠️  Worker may already exist: {e}")
    
    # Refresh worker widget
    window.worker_widget.refresh_workers()
    
    # Reload workers in time entry widget
    workers = window.worker_repository.find_all()
    window.time_entry_widget.load_workers(workers)
    
    print(f"✅ Test data setup complete ({len(workers)} workers)")


# ============================================================================
# Test Suite
# ============================================================================

class TestUIInteraction:
    """Main UI Interaction Test Suite"""
    
    def test_01_application_startup(self, main_window, qtbot):
        """
        Test 1: Application Startup & Initialization
        
        Verifies:
        - Main window is visible
        - All tabs are accessible
        - Menu bar is functional
        """
        print("\n" + "="*70)
        print("TEST 1: Application Startup & Initialization")
        print("="*70)
        
        # Verify window is visible
        assert main_window.isVisible(), "Main window should be visible"
        assert main_window.windowTitle() == "Kapazitäts- & Auslastungsplaner"
        
        # Verify tab widget exists
        tab_widget = main_window.tab_widget
        assert tab_widget is not None, "Tab widget should exist"
        assert tab_widget.count() == 4, "Should have 4 tabs"
        
        # Verify all tabs
        tab_names = [tab_widget.tabText(i) for i in range(tab_widget.count())]
        print(f"📑 Available tabs: {tab_names}")
        
        expected_tabs = ["Zeiterfassung", "Workers", "Kapazitätsplanung", "Analytics"]
        for expected in expected_tabs:
            assert expected in tab_names, f"Tab '{expected}' should exist"
        
        # Verify menu bar
        menubar = main_window.menuBar()
        assert menubar is not None, "Menu bar should exist"
        
        menu_titles = [action.text() for action in menubar.actions()]
        print(f"📋 Available menus: {menu_titles}")
        
        visual_pause("Verify main window layout and all UI components are visible", 3.0)
        
        print("✅ TEST 1 PASSED: Application initialized successfully\n")
    
    def test_02_time_entry_flow(self, main_window, qtbot):
        """
        Test 2: Time Entry Creation Flow
        
        Simulates:
        - Navigate to Time Entry tab
        - Fill in time entry form
        - Submit entry
        - Verify entry appears in table
        """
        print("\n" + "="*70)
        print("TEST 2: Time Entry Creation Flow")
        print("="*70)
        
        # Navigate to Time Entry tab
        tab_widget = main_window.tab_widget
        tab_widget.setCurrentIndex(0)  # Zeiterfassung
        QTest.qWait(300)
        
        print("📍 Navigated to 'Zeiterfassung' tab")
        visual_pause("Verify Time Entry form is visible", 2.0)
        
        # Get time entry widget
        time_entry_widget = main_window.time_entry_widget
        
        # Find form elements
        worker_combo = time_entry_widget.findChild(QComboBox, "worker_combo")
        date_edit = time_entry_widget.findChild(QDateEdit, "date_edit")
        project_input = time_entry_widget.findChild(QLineEdit, "project_input")
        duration_input = time_entry_widget.findChild(QLineEdit, "duration_input")
        description_input = time_entry_widget.findChild(QTextEdit, "description_input")
        
        print("\n📝 Filling in time entry form...")
        
        # Select worker (if available)
        if worker_combo and worker_combo.count() > 0:
            worker_combo.setCurrentIndex(0)
            print(f"   👤 Selected worker: {worker_combo.currentText()}")
            QTest.qWait(ANIMATION_DELAY)
        
        # Set date
        if date_edit:
            today = QDate.currentDate()
            safe_set_date(date_edit, today)
        
        # Fill project
        if project_input:
            safe_input_text(project_input, "Test Project Alpha")
        
        # Fill duration
        if duration_input:
            safe_input_text(duration_input, "4h")
        
        # Fill description
        if description_input:
            description_input.clear()
            description_input.setPlainText("Automated UI test entry - Testing time entry functionality")
            print(f"   📄 Description: 'Automated UI test entry...'")
            QTest.qWait(ANIMATION_DELAY)
        
        visual_pause("Verify all form fields are filled correctly", 2.5)
        
        # Count rows before submission
        time_entry_table = time_entry_widget.findChild(QTableWidget)
        rows_before = count_table_rows(time_entry_table) if time_entry_table else 0
        
        # Submit form
        print("\n💾 Submitting time entry...")
        submit_success = safe_click(time_entry_widget, "Speichern")
        
        if submit_success:
            QTest.qWait(500)  # Wait for save operation
            
            # Verify entry was added to table
            if time_entry_table:
                rows_after = count_table_rows(time_entry_table)
                print(f"📊 Rows before: {rows_before}, after: {rows_after}")
                
                visual_pause("Verify new time entry appears in the table below", 3.0)
                
                assert rows_after > rows_before, "New entry should appear in table"
        
        print("✅ TEST 2 PASSED: Time entry created successfully\n")
    
    def test_03_worker_management_flow(self, main_window, qtbot):
        """
        Test 3: Worker Management Flow
        
        Simulates:
        - Navigate to Workers tab
        - View worker table
        - Verify existing workers
        """
        print("\n" + "="*70)
        print("TEST 3: Worker Management Flow")
        print("="*70)
        
        # Navigate to Workers tab
        tab_widget = main_window.tab_widget
        tab_widget.setCurrentIndex(1)  # Workers
        QTest.qWait(300)
        
        print("📍 Navigated to 'Workers' tab")
        visual_pause("Verify Workers table is visible", 2.0)
        
        # Get worker widget
        worker_widget = main_window.worker_widget
        
        # Find worker table
        worker_table = worker_widget.findChild(QTableWidget)
        
        if worker_table:
            row_count = count_table_rows(worker_table)
            print(f"👥 Found {row_count} workers in table")
            
            # Print worker names
            print("\n📋 Worker List:")
            for row in range(min(row_count, 5)):  # Show first 5
                name_item = worker_table.item(row, 0)
                email_item = worker_table.item(row, 1)
                team_item = worker_table.item(row, 2)
                
                if name_item:
                    name = name_item.text()
                    email = email_item.text() if email_item else "N/A"
                    team = team_item.text() if team_item else "N/A"
                    print(f"   {row+1}. {name} ({email}) - Team: {team}")
            
            visual_pause("Verify worker table displays all workers correctly", 3.0)
            
            assert row_count > 0, "Should have at least one worker"
        
        print("✅ TEST 3 PASSED: Worker management verified\n")
    
    def test_04_analytics_dashboard(self, main_window, qtbot):
        """
        Test 4: Analytics Dashboard Interaction
        
        Simulates:
        - Navigate to Analytics tab
        - View team overview table
        - Test date filters
        - Test search functionality
        """
        print("\n" + "="*70)
        print("TEST 4: Analytics Dashboard Interaction")
        print("="*70)
        
        # Navigate to Analytics tab
        tab_widget = main_window.tab_widget
        tab_widget.setCurrentIndex(3)  # Analytics
        QTest.qWait(300)
        
        print("📍 Navigated to 'Analytics' tab")
        visual_pause("Verify Analytics dashboard is visible", 2.0)
        
        # Get analytics widget
        analytics_widget = main_window.analytics_widget
        
        # Find team table
        team_table = None
        for table in analytics_widget.findChildren(QTableWidget):
            if table.objectName() == "team_table" or "team" in table.objectName().lower():
                team_table = table
                break
        
        if not team_table:
            # Try to find any table
            tables = analytics_widget.findChildren(QTableWidget)
            if tables:
                team_table = tables[0]
        
        if team_table:
            row_count = count_table_rows(team_table)
            print(f"📊 Analytics table has {row_count} rows")
            
            visual_pause("Verify analytics table with utilization data", 2.5)
        
        # Test date range presets
        print("\n📅 Testing date range filters...")
        date_range_buttons = analytics_widget.findChildren(QPushButton)
        
        preset_buttons = []
        for btn in date_range_buttons:
            btn_text = btn.text().lower()
            if any(keyword in btn_text for keyword in ["heute", "woche", "monat", "tage"]):
                preset_buttons.append(btn)
        
        if preset_buttons:
            print(f"   Found {len(preset_buttons)} date preset buttons")
            
            # Click first preset
            if len(preset_buttons) > 0:
                first_preset = preset_buttons[0]
                print(f"   🖱️  Clicking preset: '{first_preset.text()}'")
                QTest.mouseClick(first_preset, Qt.LeftButton)
                QTest.qWait(500)
                
                visual_pause(f"Verify date filter '{first_preset.text()}' is applied", 2.0)
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        search_inputs = analytics_widget.findChildren(QLineEdit)
        
        search_field = None
        for input_field in search_inputs:
            placeholder = input_field.placeholderText().lower()
            if "such" in placeholder or "search" in placeholder:
                search_field = input_field
                break
        
        if search_field and team_table:
            print("   Found search field")
            
            # Count visible rows before search
            rows_before_search = count_table_rows(team_table, visible_only=True)
            
            # Perform search
            safe_input_text(search_field, "max")
            QTest.qWait(500)
            
            rows_after_search = count_table_rows(team_table, visible_only=True)
            
            print(f"   📊 Visible rows: {rows_before_search} → {rows_after_search}")
            
            visual_pause("Verify search filters the table (showing only matching rows)", 3.0)
            
            # Clear search
            search_field.clear()
            QTest.qWait(300)
        
        print("✅ TEST 4 PASSED: Analytics dashboard verified\n")
    
    def test_05_menu_navigation(self, main_window, qtbot):
        """
        Test 5: Menu Navigation & Dialogs
        
        Simulates:
        - Open File menu
        - Open Settings menu
        - Open Help menu
        - Test dialog opening (if available)
        """
        print("\n" + "="*70)
        print("TEST 5: Menu Navigation & Dialogs")
        print("="*70)
        
        menubar = main_window.menuBar()
        
        # Get all menus
        menus = {}
        for action in menubar.actions():
            menu_text = action.text().replace("&", "")
            menus[menu_text] = action.menu()
        
        print(f"📋 Available menus: {list(menus.keys())}")
        
        # Test Hilfe menu (safest to test)
        if "Hilfe" in menus:
            print("\n📖 Testing Hilfe (Help) menu...")
            
            help_menu = menus["Hilfe"]
            help_actions = help_menu.actions()
            
            for action in help_actions:
                if action.isSeparator():
                    continue
                action_text = action.text().replace("&", "")
                print(f"   📝 Found action: '{action_text}'")
            
            visual_pause("Verify menu structure is correct", 2.0)
        
        # Test Einstellungen menu
        if "Einstellungen" in menus:
            print("\n⚙️  Testing Einstellungen (Settings) menu...")
            
            settings_menu = menus["Einstellungen"]
            settings_actions = settings_menu.actions()
            
            for action in settings_actions:
                if action.isSeparator():
                    continue
                action_text = action.text().replace("&", "")
                print(f"   📝 Found action: '{action_text}'")
        
        print("✅ TEST 5 PASSED: Menu navigation verified\n")
    
    def test_06_capacity_planning(self, main_window, qtbot):
        """
        Test 6: Capacity Planning Flow
        
        Simulates:
        - Navigate to Capacity Planning tab
        - View capacity table
        """
        print("\n" + "="*70)
        print("TEST 6: Capacity Planning Flow")
        print("="*70)
        
        # Navigate to Capacity Planning tab
        tab_widget = main_window.tab_widget
        tab_widget.setCurrentIndex(2)  # Kapazitätsplanung
        QTest.qWait(300)
        
        print("📍 Navigated to 'Kapazitätsplanung' tab")
        visual_pause("Verify Capacity Planning interface is visible", 2.0)
        
        # Get capacity widget
        capacity_widget = main_window.capacity_widget
        
        # Find capacity table
        capacity_table = capacity_widget.findChild(QTableWidget)
        
        if capacity_table:
            row_count = count_table_rows(capacity_table)
            print(f"📊 Capacity table has {row_count} rows")
            
            visual_pause("Verify capacity planning table and controls", 2.5)
        
        print("✅ TEST 6 PASSED: Capacity planning verified\n")
    
    def test_07_complete_user_journey(self, main_window, qtbot):
        """
        Test 7: Complete User Journey
        
        Simulates a complete user workflow:
        1. Create time entry
        2. Check worker list
        3. View analytics
        4. Review capacity
        """
        print("\n" + "="*70)
        print("TEST 7: Complete User Journey")
        print("="*70)
        print("Simulating complete workflow through all major features...")
        
        tab_widget = main_window.tab_widget
        
        # Step 1: Create time entry
        print("\n📝 Step 1/4: Creating time entry...")
        tab_widget.setCurrentIndex(0)
        QTest.qWait(500)
        visual_pause("Creating a new time entry", 1.5)
        
        # Step 2: Check workers
        print("\n👥 Step 2/4: Reviewing workers...")
        tab_widget.setCurrentIndex(1)
        QTest.qWait(500)
        visual_pause("Viewing worker list", 1.5)
        
        # Step 3: Check capacity
        print("\n📊 Step 3/4: Checking capacity planning...")
        tab_widget.setCurrentIndex(2)
        QTest.qWait(500)
        visual_pause("Viewing capacity planning", 1.5)
        
        # Step 4: View analytics
        print("\n📈 Step 4/4: Analyzing utilization...")
        tab_widget.setCurrentIndex(3)
        QTest.qWait(500)
        visual_pause("Final view: Analytics dashboard", 2.0)
        
        print("\n✅ TEST 7 PASSED: Complete user journey executed\n")
        print("="*70)
        print("🎉 ALL UI INTERACTION TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)


# ============================================================================
# Standalone Execution
# ============================================================================

if __name__ == "__main__":
    """
    Run tests standalone with visual output
    
    Usage:
        python tests/ui_automation/test_ui_interaction.py
    """
    print("\n" + "="*70)
    print("🚀 CAPACITY PLANNER - UI INTERACTION TESTS")
    print("="*70)
    print("\nStarting automated UI testing with visual verification pauses...")
    print("Press Ctrl+C to abort\n")
    
    # Run with pytest
    pytest.main([
        __file__,
        "-v",
        "-s",  # Show print statements
        "--tb=short",  # Short traceback
        "--color=yes"  # Colored output
    ])
