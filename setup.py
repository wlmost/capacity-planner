"""
Setup-Skript für Kapazitäts- & Auslastungsplaner
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="capacity-planner",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Kapazitäts- & Auslastungsplaner für Knowledge Worker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wlmost/capacity-planner",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.6.0",
        "pycryptodome>=3.19.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "capacity-planner=main:main",
        ],
    },
)
