"""
UI Automation Test Runner
==========================

Quick runner script for UI automation tests with various modes.

Usage:
    python tests/ui_automation/run_ui_tests.py [mode]
    
Modes:
    basic       - Run basic interaction tests only (default)
    advanced    - Run advanced UI flow tests only
    all         - Run all UI tests
    quick       - Run tests with minimal visual pauses (fast mode)
    demo        - Run with extended pauses for demonstration
    
Examples:
    python tests/ui_automation/run_ui_tests.py
    python tests/ui_automation/run_ui_tests.py advanced
    python tests/ui_automation/run_ui_tests.py all
    python tests/ui_automation/run_ui_tests.py quick
"""
import sys
import os
import pytest
from pathlib import Path


def run_tests(mode: str = "basic"):
    """
    Run UI tests with specified mode
    
    Args:
        mode: Test mode (basic, advanced, all, quick, demo)
    """
    # Get test directory
    test_dir = Path(__file__).parent
    
    # Determine which tests to run
    if mode == "basic":
        test_files = [str(test_dir / "test_ui_interaction.py")]
        print("\n🎯 Running BASIC UI interaction tests...")
    elif mode == "advanced":
        test_files = [str(test_dir / "test_advanced_ui_flows.py")]
        print("\n🎯 Running ADVANCED UI flow tests...")
    elif mode == "all":
        test_files = [str(test_dir)]
        print("\n🎯 Running ALL UI automation tests...")
    elif mode == "quick":
        # Set environment variable for fast mode
        os.environ["FAST_MODE"] = "1"
        test_files = [str(test_dir)]
        print("\n⚡ Running tests in QUICK mode (minimal pauses)...")
    elif mode == "demo":
        os.environ["DEMO_MODE"] = "1"
        test_files = [str(test_dir / "test_ui_interaction.py")]
        print("\n🎬 Running tests in DEMO mode (extended pauses)...")
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Valid modes: basic, advanced, all, quick, demo")
        return 1
    
    # Build pytest arguments
    pytest_args = [
        *test_files,
        "-v",              # Verbose
        "-s",              # Show print statements
        "--tb=short",      # Short traceback
        "--color=yes",     # Colored output
        "-x",              # Stop on first failure
    ]
    
    print(f"📂 Test location: {test_dir}")
    print(f"🧪 Test files: {test_files}")
    print("="*70)
    print()
    
    # Run tests
    result = pytest.main(pytest_args)
    
    print("\n" + "="*70)
    if result == 0:
        print("✅ All tests PASSED!")
    else:
        print(f"❌ Tests FAILED (exit code: {result})")
    print("="*70)
    
    return result


def main():
    """Main entry point"""
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest is not installed!")
        print("   Install with: pip install pytest pytest-qt")
        return 1
    
    # Check if PySide6 is available
    try:
        import PySide6
    except ImportError:
        print("❌ PySide6 is not installed!")
        print("   Install with: pip install PySide6")
        return 1
    
    # Get mode from command line
    mode = sys.argv[1] if len(sys.argv) > 1 else "basic"
    
    # Run tests
    return run_tests(mode)


if __name__ == "__main__":
    sys.exit(main())
