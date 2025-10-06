"""
Seed Data - Beispieldaten für Entwicklung
"""
from datetime import datetime, timedelta
from typing import List

from ..models.worker import Worker
from ..models.time_entry import TimeEntry
from ..models.capacity import Capacity


def get_sample_workers() -> List[Worker]:
    """
    Erstellt Beispiel-Workers für Entwicklung
    
    Returns:
        Liste von Worker-Objekten
    """
    return [
        Worker(
            name="Max Mustermann",
            email="max.mustermann@example.com",
            team="Engineering",
            active=True
        ),
        Worker(
            name="Anna Schmidt",
            email="anna.schmidt@example.com",
            team="Product Management",
            active=True
        ),
        Worker(
            name="Tom Klein",
            email="tom.klein@example.com",
            team="Design",
            active=True
        ),
        Worker(
            name="Lisa Müller",
            email="lisa.mueller@example.com",
            team="Engineering",
            active=False
        ),
    ]


def get_sample_time_entries(worker_id: int) -> List[TimeEntry]:
    """
    Erstellt Beispiel-Zeiterfassungen für einen Worker
    
    Args:
        worker_id: ID des Workers
        
    Returns:
        Liste von TimeEntry-Objekten
    """
    today = datetime.now()
    
    return [
        TimeEntry(
            worker_id=worker_id,
            date=today - timedelta(days=7),
            duration_minutes=480,  # 8h
            description="Sprint Planning & Refinement",
            project="Project Alpha"
        ),
        TimeEntry(
            worker_id=worker_id,
            date=today - timedelta(days=6),
            duration_minutes=420,  # 7h
            description="Feature Implementation",
            project="Project Alpha"
        ),
        TimeEntry(
            worker_id=worker_id,
            date=today - timedelta(days=5),
            duration_minutes=360,  # 6h
            description="Code Review & Testing",
            project="Project Beta"
        ),
        TimeEntry(
            worker_id=worker_id,
            date=today - timedelta(days=4),
            duration_minutes=510,  # 8.5h
            description="Bug Fixes & Documentation",
            project="Project Alpha"
        ),
        TimeEntry(
            worker_id=worker_id,
            date=today - timedelta(days=3),
            duration_minutes=300,  # 5h
            description="Team Meeting & 1:1s",
            project=None
        ),
        TimeEntry(
            worker_id=worker_id,
            date=today - timedelta(days=2),
            duration_minutes=450,  # 7.5h
            description="Architecture Design",
            project="Project Gamma"
        ),
        TimeEntry(
            worker_id=worker_id,
            date=today - timedelta(days=1),
            duration_minutes=390,  # 6.5h
            description="Implementation & Review",
            project="Project Beta"
        ),
    ]


def get_sample_capacities(worker_id: int) -> List[Capacity]:
    """
    Erstellt Beispiel-Kapazitäten für einen Worker
    
    Args:
        worker_id: ID des Workers
        
    Returns:
        Liste von Capacity-Objekten
    """
    today = datetime.now()
    
    # Current month
    current_month_start = datetime(today.year, today.month, 1)
    if today.month == 12:
        next_month_start = datetime(today.year + 1, 1, 1)
    else:
        next_month_start = datetime(today.year, today.month + 1, 1)
    current_month_end = next_month_start - timedelta(days=1)
    
    # Next month
    if next_month_start.month == 12:
        following_month_start = datetime(next_month_start.year + 1, 1, 1)
    else:
        following_month_start = datetime(next_month_start.year, next_month_start.month + 1, 1)
    next_month_end = following_month_start - timedelta(days=1)
    
    return [
        Capacity(
            worker_id=worker_id,
            start_date=current_month_start,
            end_date=current_month_end,
            planned_hours=160.0,  # 20 Tage * 8h
            notes="Standard Arbeitszeit"
        ),
        Capacity(
            worker_id=worker_id,
            start_date=next_month_start,
            end_date=next_month_end,
            planned_hours=140.0,  # Reduziert wegen Urlaub
            notes="Urlaubsplanung: 1 Woche"
        ),
    ]


def seed_database(db_service, crypto_service):
    """
    Fügt Beispieldaten in die Datenbank ein
    
    Args:
        db_service: DatabaseService-Instanz
        crypto_service: CryptoService-Instanz
        
    Returns:
        Dict mit IDs der erstellten Objekte
    """
    from ..repositories.worker_repository import WorkerRepository
    from ..repositories.time_entry_repository import TimeEntryRepository
    from ..repositories.capacity_repository import CapacityRepository
    
    worker_repo = WorkerRepository(db_service, crypto_service)
    entry_repo = TimeEntryRepository(db_service)
    capacity_repo = CapacityRepository(db_service)
    
    created_ids = {
        "workers": [],
        "time_entries": [],
        "capacities": []
    }
    
    # Create Workers
    for worker in get_sample_workers():
        worker_id = worker_repo.create(worker)
        created_ids["workers"].append(worker_id)
        
        # Create TimeEntries for this worker
        for entry in get_sample_time_entries(worker_id):
            entry_id = entry_repo.create(entry)
            created_ids["time_entries"].append(entry_id)
        
        # Create Capacities for this worker
        for capacity in get_sample_capacities(worker_id):
            capacity_id = capacity_repo.create(capacity)
            created_ids["capacities"].append(capacity_id)
    
    return created_ids
