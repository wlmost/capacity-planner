# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File für Capacity Planner
Erstellt eine standalone Windows-Executable

Verwendung:
    pyinstaller capacity-planner.spec
"""

import sys
from pathlib import Path

# Projekt-Root
project_root = Path('.').resolve()

# Daten-Dateien sammeln
datas = []

# PySide6 Plugins (QtCharts, etc.)
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
datas += collect_data_files('PySide6')

# Hidden Imports - alle verwendeten Module
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtCharts',
    'pycryptodome',
    'Crypto.Cipher.AES',
    'Crypto.Random',
    'Crypto.Protocol.KDF',
    'sqlite3',
]

# Alle src-Module automatisch sammeln
hiddenimports += collect_submodules('src')

# Analysis - welche Dateien sollen gebündelt werden
a = Analysis(
    ['run.py'],  # Entry Point mit absolutem Import-Wrapper
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Nicht mehr benötigt seit QtCharts
        'numpy',
        'PIL',
        'tkinter',
        'test',
        'unittest',
        'pytest',
    ],
    noarchive=False,
    optimize=0,
)

# PYZ - Python Archive erstellen
pyz = PYZ(a.pure)

# EXE - Executable erstellen
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CapacityPlanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Keine Konsole im Hintergrund
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Hier kannst du später ein Icon hinzufügen
)
