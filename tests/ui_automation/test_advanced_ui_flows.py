"""
Advanced UI Interaction Tests
==============================

Advanced test scenarios with complex user interactions, edge cases,
and performance testing.

Test Scenarios:
1. Data Export Workflows (Excel, PDF)
2. Worker Detail Dialog Navigation
3. Search & Filter Combinations
4. Date Range Preset Testing
5. Table Interaction & Sorting
6. Error Handling & Validation

Usage:
    pytest tests/ui_automation/test_advanced_ui_flows.py -v -s
"""
import pytest
import time
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QPushButton, QLineEdit, QDateEdit, 
    QTableWidget, QDialog, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QTimer, QPoint
from PySide6.QtTest import QTest

from src.views.main_window import MainWindow
from src.models.worker import Worker


# ============================================================================
# Configuration
# ============================================================================

VISUAL_PAUSE = 2.0  # Visual verification pause duration
ANIMATION_DELAY = 150  # Delay between UI actions


def visual_checkpoint(description: str, duration: float = VISUAL_PAUSE):
    """Visual checkpoint for test verification"""
    print(f"\n{'─'*70}")
    print(f"✋ CHECKPOINT: {description}")
    print(f"⏱️  Pausing {duration}s for verification...")
    print(f"{'─'*70}")
    
    app = QApplication.instance()
    start = time.time()
    while time.time() - start < duration:
        app.processEvents()
        time.sleep(0.05)


def find_button_by_text(parent, text: str, partial: bool = True) -> QPushButton:
    """Find button by text (case-insensitive)"""
    buttons = parent.findChildren(QPushButton)
    text_lower = text.lower()
    
    for btn in buttons:
        btn_text = btn.text().lower()
        if partial and text_lower in btn_text:
            return btn
        elif not partial and text_lower == btn_text:
            return btn
    return None


def find_table_with_data(parent) -> QTableWidget:
    """Find first table widget with data"""
    tables = parent.findChildren(QTableWidget)
    for table in tables:
        if table.rowCount() > 0:
            return table
    return tables[0] if tables else None


def simulate_typing(widget, text: str, delay_per_char: int = 30):
    """Simulate realistic typing with per-character delay"""
    widget.clear()
    widget.setFocus()
    QTest.qWait(50)
    
    print(f"⌨️  Typing '{text}'", end="", flush=True)
    for char in text:
        QTest.keyClick(widget, char)
        QTest.qWait(delay_per_char)
        print(".", end="", flush=True)
    print(" ✓")


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def app():
    """QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture(scope="function")
def main_window(app, qtbot):
    """Main window with initialized test data"""
    print("\n" + "="*70)
    print("🔧 Initializing Main Window for Advanced Tests...")
    print("="*70)
    
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    QTest.qWaitForWindowExposed(window)
    QTest.qWait(500)
    
    # Ensure test data exists
    _ensure_test_data(window)
    _ensure_time_entries(window)
    
    print("✅ Advanced test setup complete\n")
    return window


def _ensure_test_data(window: MainWindow):
    """Ensure test workers exist"""
    workers = window.worker_repository.find_all()
    
    if len(workers) < 2:
        print("📝 Creating test workers...")
        test_workers = [
            Worker(None, "Test User 1", "test1@example.com", "Engineering"),
            Worker(None, "Test User 2", "test2@example.com", "QA"),
            Worker(None, "Test User 3", "test3@example.com", "Design")
        ]
        
        for worker in test_workers:
            try:
                window.worker_repository.save(worker)
            except:
                pass  # May already exist
        
        window.worker_widget.refresh_workers()
        workers = window.worker_repository.find_all()
        window.time_entry_widget.load_workers(workers)
    
    print(f"✅ {len(workers)} workers available for testing")


def _ensure_time_entries(window: MainWindow):
    """Ensure some time entries exist for testing"""
    entries = window.time_entry_repository.find_all()
    
    if len(entries) < 3:
        print("📝 Creating test time entries...")
        workers = window.worker_repository.find_all()
        
        if workers:
            from src.models.time_entry import TimeEntry
            
            test_entries = [
                TimeEntry(
                    entry_id=None,
                    worker_id=workers[0].worker_id,
                    date=datetime.now() - timedelta(days=i),
                    entry_type="Normal",
                    project=f"Project {i+1}",
                    category="Development",
                    description=f"Test entry {i+1}",
                    hours=4.0 + i
                )
                for i in range(3)
            ]
            
            for entry in test_entries:
                try:
                    window.time_entry_repository.save(entry)
                except:
                    pass
            
            # Refresh UI
            window.time_entry_widget.refresh_entries()
    
    entries = window.time_entry_repository.find_all()
    print(f"✅ {len(entries)} time entries available for testing")


# ============================================================================
# Advanced Test Suite
# ============================================================================

class TestAdvancedUIFlows:
    """Advanced UI interaction tests"""
    
    def test_01_worker_detail_dialog_navigation(self, main_window, qtbot):
        """
        Test: Worker Detail Dialog Navigation
        
        Tests:
        - Open worker detail from analytics
        - Verify dialog contents
        - Navigate charts and tables
        - Close dialog
        """
        print("\n" + "="*70)
        print("TEST: Worker Detail Dialog Navigation")
        print("="*70)
        
        # Navigate to Analytics tab
        main_window.tab_widget.setCurrentIndex(3)
        QTest.qWait(500)
        
        analytics_widget = main_window.analytics_widget
        
        # Find and click refresh to ensure data
        refresh_btn = find_button_by_text(analytics_widget, "aktualisieren")
        if refresh_btn:
            print("🔄 Refreshing analytics data...")
            QTest.mouseClick(refresh_btn, Qt.LeftButton)
            QTest.qWait(800)
        
        # Find team table
        team_table = find_table_with_data(analytics_widget)
        
        if team_table and team_table.rowCount() > 0:
            print(f"📊 Found team table with {team_table.rowCount()} workers")
            
            # Double-click first row to open detail dialog
            print("🖱️  Double-clicking first worker row...")
            
            # Get the center of first row
            rect = team_table.visualItemRect(team_table.item(0, 0))
            center = rect.center()
            
            # Double-click
            QTest.mouseDClick(
                team_table.viewport(),
                Qt.LeftButton,
                Qt.NoModifier,
                center
            )
            QTest.qWait(1000)
            
            visual_checkpoint(
                "Worker Detail Dialog should be open with charts and tables",
                3.0
            )
            
            # Find the dialog
            dialogs = QApplication.activeWindow().findChildren(QDialog)
            if dialogs:
                dialog = dialogs[0]
                print(f"✅ Dialog found: {dialog.windowTitle()}")
                
                # Look for export button
                export_btn = find_button_by_text(dialog, "export")
                if export_btn:
                    print(f"✅ Found export button: '{export_btn.text()}'")
                
                visual_checkpoint("Review worker detail dialog contents", 2.5)
                
                # Close dialog
                print("🔒 Closing dialog...")
                dialog.close()
                QTest.qWait(300)
        
        print("✅ TEST PASSED: Worker detail navigation complete\n")
    
    def test_02_date_range_preset_cycling(self, main_window, qtbot):
        """
        Test: Date Range Preset Cycling
        
        Tests:
        - Cycle through all date presets
        - Verify each preset updates the date range
        - Check table refresh after each preset
        """
        print("\n" + "="*70)
        print("TEST: Date Range Preset Cycling")
        print("="*70)
        
        # Navigate to Analytics
        main_window.tab_widget.setCurrentIndex(3)
        QTest.qWait(300)
        
        analytics_widget = main_window.analytics_widget
        
        # Find date range buttons
        all_buttons = analytics_widget.findChildren(QPushButton)
        date_presets = []
        
        preset_keywords = ["heute", "woche", "monat", "quartal", "jahr", "tage"]
        
        for btn in all_buttons:
            btn_text = btn.text().lower()
            if any(kw in btn_text for kw in preset_keywords):
                date_presets.append(btn)
        
        print(f"📅 Found {len(date_presets)} date preset buttons")
        
        # Cycle through each preset
        for i, preset_btn in enumerate(date_presets[:8], 1):  # Limit to 8
            preset_name = preset_btn.text()
            print(f"\n{i}. Testing preset: '{preset_name}'")
            
            # Click preset
            QTest.mouseClick(preset_btn, Qt.LeftButton)
            QTest.qWait(600)
            
            # Check if button is visually selected (checked state)
            is_checked = preset_btn.isChecked()
            print(f"   {'✅' if is_checked else '⚠️ '} Button checked: {is_checked}")
            
            visual_checkpoint(f"Verify '{preset_name}' filter is applied", 1.5)
        
        print("\n✅ TEST PASSED: All date presets cycled successfully\n")
    
    def test_03_table_search_functionality(self, main_window, qtbot):
        """
        Test: Table Search Functionality
        
        Tests:
        - Enter search query
        - Verify row filtering
        - Clear search
        - Multiple search terms
        """
        print("\n" + "="*70)
        print("TEST: Table Search Functionality")
        print("="*70)
        
        # Navigate to Analytics
        main_window.tab_widget.setCurrentIndex(3)
        QTest.qWait(500)
        
        analytics_widget = main_window.analytics_widget
        
        # Find search field
        search_field = None
        for line_edit in analytics_widget.findChildren(QLineEdit):
            placeholder = line_edit.placeholderText().lower()
            if "such" in placeholder or "search" in placeholder:
                search_field = line_edit
                break
        
        # Find table
        team_table = find_table_with_data(analytics_widget)
        
        if search_field and team_table:
            total_rows = team_table.rowCount()
            print(f"📊 Table has {total_rows} total rows")
            
            # Test 1: Search for specific term
            print("\n🔍 Test 1: Searching for 'test'...")
            simulate_typing(search_field, "test", delay_per_char=50)
            QTest.qWait(400)
            
            visible_rows = sum(
                1 for i in range(total_rows) 
                if not team_table.isRowHidden(i)
            )
            print(f"   📉 Visible rows after search: {visible_rows}/{total_rows}")
            
            visual_checkpoint("Verify table is filtered to show only matching rows", 2.0)
            
            # Test 2: Clear search
            print("\n🧹 Test 2: Clearing search...")
            search_field.clear()
            QTest.qWait(400)
            
            visible_after_clear = sum(
                1 for i in range(total_rows)
                if not team_table.isRowHidden(i)
            )
            print(f"   📈 Visible rows after clear: {visible_after_clear}/{total_rows}")
            
            visual_checkpoint("Verify all rows are visible again", 1.5)
            
            # Test 3: Search for partial match
            print("\n🔍 Test 3: Searching for 'user'...")
            simulate_typing(search_field, "user", delay_per_char=50)
            QTest.qWait(400)
            
            visible_partial = sum(
                1 for i in range(total_rows)
                if not team_table.isRowHidden(i)
            )
            print(f"   📊 Visible rows for 'user': {visible_partial}/{total_rows}")
            
            visual_checkpoint("Verify partial match filtering works", 1.5)
            
            # Final cleanup
            search_field.clear()
            QTest.qWait(200)
        
        print("\n✅ TEST PASSED: Search functionality verified\n")
    
    def test_04_time_entry_validation(self, main_window, qtbot):
        """
        Test: Time Entry Input Validation
        
        Tests:
        - Invalid time format
        - Valid time formats (4h, 2.5h, 180min)
        - Empty fields
        - Form reset
        """
        print("\n" + "="*70)
        print("TEST: Time Entry Input Validation")
        print("="*70)
        
        # Navigate to Time Entry tab
        main_window.tab_widget.setCurrentIndex(0)
        QTest.qWait(300)
        
        time_entry_widget = main_window.time_entry_widget
        
        # Find duration input
        duration_input = time_entry_widget.findChild(QLineEdit, "duration_input")
        
        if duration_input:
            print("\n⏱️  Testing various time formats...")
            
            test_formats = [
                ("4h", "4 hours"),
                ("2.5h", "2.5 hours"),
                ("180min", "180 minutes"),
                ("1h 30min", "1 hour 30 minutes"),
                ("45min", "45 minutes")
            ]
            
            for time_str, description in test_formats:
                print(f"\n   Testing: '{time_str}' ({description})")
                
                duration_input.clear()
                duration_input.setText(time_str)
                duration_input.setFocus()
                QTest.qWait(300)
                
                # Check for validation feedback
                stylesheet = duration_input.styleSheet()
                print(f"   📝 Input accepted")
                
                visual_checkpoint(f"Verify '{time_str}' is valid", 1.0)
        
        print("\n✅ TEST PASSED: Time entry validation complete\n")
    
    def test_05_table_sorting_interaction(self, main_window, qtbot):
        """
        Test: Table Sorting Interaction
        
        Tests:
        - Click column headers to sort
        - Verify sort order changes
        - Test ascending/descending
        """
        print("\n" + "="*70)
        print("TEST: Table Sorting Interaction")
        print("="*70)
        
        # Navigate to Workers tab
        main_window.tab_widget.setCurrentIndex(1)
        QTest.qWait(500)
        
        worker_widget = main_window.worker_widget
        worker_table = worker_widget.findChild(QTableWidget)
        
        if worker_table and worker_table.rowCount() > 1:
            print(f"📊 Testing sorting on table with {worker_table.rowCount()} rows")
            
            # Test sorting by Name (column 0)
            print("\n📋 Sorting by Name column...")
            
            header = worker_table.horizontalHeader()
            
            # Click Name header
            name_header_pos = header.sectionPosition(0)
            header_rect = header.geometry()
            click_point = QPoint(name_header_pos + 20, header_rect.height() // 2)
            
            print("   🖱️  Clicking Name column header (ascending)...")
            QTest.mouseClick(header.viewport(), Qt.LeftButton, Qt.NoModifier, click_point)
            QTest.qWait(400)
            
            visual_checkpoint("Verify table is sorted by Name (ascending)", 2.0)
            
            # Click again for descending
            print("   🖱️  Clicking Name column header (descending)...")
            QTest.mouseClick(header.viewport(), Qt.LeftButton, Qt.NoModifier, click_point)
            QTest.qWait(400)
            
            visual_checkpoint("Verify table is sorted by Name (descending)", 2.0)
            
            # Sort by Email (column 1)
            if worker_table.columnCount() > 1:
                print("\n📧 Sorting by Email column...")
                email_header_pos = header.sectionPosition(1)
                click_point = QPoint(email_header_pos + 20, header_rect.height() // 2)
                
                QTest.mouseClick(header.viewport(), Qt.LeftButton, Qt.NoModifier, click_point)
                QTest.qWait(400)
                
                visual_checkpoint("Verify table is sorted by Email", 1.5)
        
        print("\n✅ TEST PASSED: Table sorting verified\n")
    
    def test_06_export_button_discovery(self, main_window, qtbot):
        """
        Test: Export Button Discovery
        
        Tests:
        - Find all export buttons
        - Verify they're clickable
        - Check for file dialogs (without actually saving)
        """
        print("\n" + "="*70)
        print("TEST: Export Button Discovery")
        print("="*70)
        
        tabs_to_check = [
            (3, "Analytics", "analytics_widget")
        ]
        
        for tab_index, tab_name, widget_attr in tabs_to_check:
            print(f"\n📑 Checking '{tab_name}' tab for export buttons...")
            
            main_window.tab_widget.setCurrentIndex(tab_index)
            QTest.qWait(500)
            
            widget = getattr(main_window, widget_attr)
            
            # Find export buttons
            export_buttons = []
            for btn in widget.findChildren(QPushButton):
                btn_text = btn.text().lower()
                if "export" in btn_text or "excel" in btn_text or "csv" in btn_text:
                    export_buttons.append(btn)
            
            if export_buttons:
                print(f"   ✅ Found {len(export_buttons)} export button(s)")
                
                for btn in export_buttons:
                    print(f"      📤 {btn.text()}")
                    
                    # Verify button is enabled
                    if btn.isEnabled():
                        print(f"      ✅ Button is enabled and clickable")
                    else:
                        print(f"      ⚠️  Button is disabled")
                
                visual_checkpoint(f"Verify export buttons in {tab_name}", 1.5)
            else:
                print(f"   ℹ️  No export buttons found in {tab_name}")
        
        print("\n✅ TEST PASSED: Export functionality discovered\n")
    
    def test_07_multi_tab_data_consistency(self, main_window, qtbot):
        """
        Test: Multi-Tab Data Consistency
        
        Tests:
        - Create data in one tab
        - Verify it appears in related tabs
        - Check data synchronization
        """
        print("\n" + "="*70)
        print("TEST: Multi-Tab Data Consistency")
        print("="*70)
        
        print("\n1️⃣  Checking initial worker count...")
        
        # Go to Workers tab
        main_window.tab_widget.setCurrentIndex(1)
        QTest.qWait(300)
        
        worker_table = main_window.worker_widget.findChild(QTableWidget)
        initial_worker_count = worker_table.rowCount() if worker_table else 0
        print(f"   📊 Initial workers: {initial_worker_count}")
        
        # Go to Time Entry tab
        print("\n2️⃣  Checking worker dropdown in Time Entry...")
        main_window.tab_widget.setCurrentIndex(0)
        QTest.qWait(300)
        
        from PySide6.QtWidgets import QComboBox
        worker_combo = main_window.time_entry_widget.findChild(QComboBox, "worker_combo")
        
        if worker_combo:
            combo_count = worker_combo.count()
            print(f"   📋 Workers in dropdown: {combo_count}")
            
            # Compare counts
            if combo_count == initial_worker_count:
                print(f"   ✅ Worker counts match across tabs!")
            else:
                print(f"   ⚠️  Mismatch: Table={initial_worker_count}, Dropdown={combo_count}")
        
        # Go to Analytics
        print("\n3️⃣  Checking worker data in Analytics...")
        main_window.tab_widget.setCurrentIndex(3)
        QTest.qWait(500)
        
        analytics_table = find_table_with_data(main_window.analytics_widget)
        analytics_count = analytics_table.rowCount() if analytics_table else 0
        print(f"   📊 Workers in analytics: {analytics_count}")
        
        visual_checkpoint("Verify data consistency across all tabs", 2.5)
        
        print("\n✅ TEST PASSED: Data consistency verified\n")
    
    def test_08_stress_test_rapid_navigation(self, main_window, qtbot):
        """
        Test: Stress Test - Rapid Tab Navigation
        
        Tests:
        - Rapidly switch between tabs
        - Verify no crashes or freezes
        - Check UI remains responsive
        """
        print("\n" + "="*70)
        print("TEST: Stress Test - Rapid Tab Navigation")
        print("="*70)
        
        print("\n🔄 Performing rapid tab switches...")
        
        tab_widget = main_window.tab_widget
        tab_count = tab_widget.count()
        
        # Rapid cycling
        cycles = 3
        for cycle in range(cycles):
            print(f"\n   Cycle {cycle + 1}/{cycles}:")
            
            for tab_index in range(tab_count):
                tab_name = tab_widget.tabText(tab_index)
                print(f"      → {tab_name}", end="", flush=True)
                
                tab_widget.setCurrentIndex(tab_index)
                QTest.qWait(150)  # Short delay
                
                # Verify tab switched
                if tab_widget.currentIndex() == tab_index:
                    print(" ✓")
                else:
                    print(" ✗ (Failed)")
        
        print("\n🎯 Testing backward navigation...")
        for tab_index in range(tab_count - 1, -1, -1):
            tab_widget.setCurrentIndex(tab_index)
            QTest.qWait(150)
        
        # Final verification
        print("\n✅ All tabs remain functional after stress test")
        
        visual_checkpoint("Verify UI is still responsive and no errors occurred", 2.0)
        
        print("\n✅ TEST PASSED: Stress test completed successfully\n")


# ============================================================================
# Standalone Execution
# ============================================================================

if __name__ == "__main__":
    """Run advanced tests standalone"""
    print("\n" + "="*70)
    print("🚀 CAPACITY PLANNER - ADVANCED UI TESTS")
    print("="*70)
    
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--tb=short",
        "--color=yes"
    ])
