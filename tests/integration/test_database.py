"""
Integration Tests für Repository Layer
Testet echte Datenbank-Operationen mit SQLite
"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import uuid

from src.services.database_service import DatabaseService
from src.services.crypto_service import CryptoService
from src.repositories.worker_repository import WorkerRepository
from src.repositories.time_entry_repository import TimeEntryRepository
from src.repositories.capacity_repository import CapacityRepository
from src.models.worker import Worker
from src.models.time_entry import TimeEntry
from src.models.capacity import Capacity


@pytest.fixture
def temp_db():
    """Erstellt temporäre Datenbank für Tests"""
    # Unique connection name für parallele Tests
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    # Unique connection name to avoid conflicts
    unique_name = f"test_db_{uuid.uuid4().hex[:8]}"
    db_service = DatabaseService(db_path)
    db_service.connection_name = unique_name
    db_service.initialize()
    
    yield db_service
    
    # Cleanup
    db_service.close()
    try:
        Path(db_path).unlink(missing_ok=True)
    except:
        pass


@pytest.fixture
def temp_crypto():
    """Erstellt temporären CryptoService für Tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        crypto = CryptoService(key_directory=Path(temp_dir))
        crypto.initialize_keys()
        yield crypto


class TestWorkerRepositoryIntegration:
    """Integration Tests für WorkerRepository"""
    
    def test_create_and_retrieve_worker(self, temp_db, temp_crypto):
        """Test: Worker erstellen und wieder abrufen"""
        repo = WorkerRepository(temp_db, temp_crypto)
        
        # Create
        worker = Worker(
            name="Integration Test User",
            email="integration@test.com",
            team="QA"
        )
        worker_id = repo.create(worker)
        
        # Retrieve
        retrieved = repo.find_by_id(worker_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == worker_id
        assert retrieved.name == "Integration Test User"
        assert retrieved.email == "integration@test.com"
        assert retrieved.team == "QA"
        assert retrieved.active is True
    
    def test_update_worker(self, temp_db, temp_crypto):
        """Test: Worker aktualisieren"""
        repo = WorkerRepository(temp_db, temp_crypto)
        
        # Create
        worker = Worker(name="Original", email="original@test.com", team="Team A")
        worker_id = repo.create(worker)
        
        # Update
        worker.id = worker_id
        worker.name = "Updated"
        worker.email = "updated@test.com"
        worker.team = "Team B"
        worker.active = False
        
        result = repo.update(worker)
        assert result is True
        
        # Retrieve
        updated = repo.find_by_id(worker_id)
        assert updated.name == "Updated"
        assert updated.email == "updated@test.com"
        assert updated.team == "Team B"
        assert updated.active is False
    
    def test_delete_worker(self, temp_db, temp_crypto):
        """Test: Worker löschen"""
        repo = WorkerRepository(temp_db, temp_crypto)
        
        # Create
        worker = Worker(name="To Delete", email="delete@test.com", team="Team")
        worker_id = repo.create(worker)
        
        # Delete
        result = repo.delete(worker_id)
        assert result is True
        
        # Verify deleted
        deleted = repo.find_by_id(worker_id)
        assert deleted is None
    
    def test_find_all_workers(self, temp_db, temp_crypto):
        """Test: Alle Worker abrufen"""
        repo = WorkerRepository(temp_db, temp_crypto)
        
        # Create multiple workers
        repo.create(Worker(name="Worker 1", email="w1@test.com", team="Team A"))
        repo.create(Worker(name="Worker 2", email="w2@test.com", team="Team B", active=False))
        repo.create(Worker(name="Worker 3", email="w3@test.com", team="Team A"))
        
        # Find all
        all_workers = repo.find_all()
        assert len(all_workers) == 3
        
        # Find active only
        active_workers = repo.find_all(active_only=True)
        assert len(active_workers) == 2
    
    def test_find_by_email(self, temp_db, temp_crypto):
        """Test: Worker per Email suchen"""
        repo = WorkerRepository(temp_db, temp_crypto)
        
        # Create
        worker = Worker(name="Email Test", email="unique@test.com", team="Team")
        repo.create(worker)
        
        # Find by email
        found = repo.find_by_email("unique@test.com")
        assert found is not None
        assert found.email == "unique@test.com"
        
        # Not found
        not_found = repo.find_by_email("nonexistent@test.com")
        assert not_found is None


class TestTimeEntryRepositoryIntegration:
    """Integration Tests für TimeEntryRepository"""
    
    def test_create_and_retrieve_time_entry(self, temp_db, temp_crypto):
        """Test: TimeEntry erstellen und abrufen"""
        # Setup: Worker erstellen
        worker_repo = WorkerRepository(temp_db, temp_crypto)
        worker_id = worker_repo.create(Worker(name="Test", email="test@test.com", team="Team"))
        
        # TimeEntry Repository
        entry_repo = TimeEntryRepository(temp_db)
        
        # Create
        entry = TimeEntry(
            worker_id=worker_id,
            date=datetime(2025, 10, 6, 10, 0),
            duration_minutes=90,
            description="Integration Test Entry",
            project="Test Project"
        )
        entry_id = entry_repo.create(entry)
        
        # Retrieve
        retrieved = entry_repo.find_by_id(entry_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == entry_id
        assert retrieved.worker_id == worker_id
        assert retrieved.duration_minutes == 90
        assert retrieved.description == "Integration Test Entry"
        assert retrieved.project == "Test Project"
    
    def test_find_by_worker_with_date_filter(self, temp_db, temp_crypto):
        """Test: Zeiterfassungen eines Workers mit Datum-Filter"""
        # Setup Worker
        worker_repo = WorkerRepository(temp_db, temp_crypto)
        worker_id = worker_repo.create(Worker(name="Test", email="test@test.com", team="Team"))
        
        entry_repo = TimeEntryRepository(temp_db)
        
        # Create entries mit verschiedenen Daten
        entry_repo.create(TimeEntry(
            worker_id=worker_id,
            date=datetime(2025, 10, 1),
            duration_minutes=60,
            description="Entry 1"
        ))
        entry_repo.create(TimeEntry(
            worker_id=worker_id,
            date=datetime(2025, 10, 5),
            duration_minutes=90,
            description="Entry 2"
        ))
        entry_repo.create(TimeEntry(
            worker_id=worker_id,
            date=datetime(2025, 10, 10),
            duration_minutes=120,
            description="Entry 3"
        ))
        
        # Find with date filter
        entries = entry_repo.find_by_worker(
            worker_id,
            start_date=datetime(2025, 10, 3),
            end_date=datetime(2025, 10, 7)
        )
        
        assert len(entries) == 1
        assert entries[0].description == "Entry 2"
    
    def test_update_and_delete_time_entry(self, temp_db, temp_crypto):
        """Test: TimeEntry aktualisieren und löschen"""
        # Setup
        worker_repo = WorkerRepository(temp_db, temp_crypto)
        worker_id = worker_repo.create(Worker(name="Test", email="test@test.com", team="Team"))
        
        entry_repo = TimeEntryRepository(temp_db)
        
        # Create
        entry = TimeEntry(
            worker_id=worker_id,
            date=datetime(2025, 10, 6),
            duration_minutes=60,
            description="Original"
        )
        entry_id = entry_repo.create(entry)
        
        # Update
        entry.id = entry_id
        entry.duration_minutes = 120
        entry.description = "Updated"
        result = entry_repo.update(entry)
        assert result is True
        
        # Verify update
        updated = entry_repo.find_by_id(entry_id)
        assert updated.duration_minutes == 120
        assert updated.description == "Updated"
        
        # Delete
        delete_result = entry_repo.delete(entry_id)
        assert delete_result is True
        
        # Verify deleted
        deleted = entry_repo.find_by_id(entry_id)
        assert deleted is None


class TestCapacityRepositoryIntegration:
    """Integration Tests für CapacityRepository"""
    
    def test_create_and_retrieve_capacity(self, temp_db, temp_crypto):
        """Test: Capacity erstellen und abrufen"""
        # Setup Worker
        worker_repo = WorkerRepository(temp_db, temp_crypto)
        worker_id = worker_repo.create(Worker(name="Test", email="test@test.com", team="Team"))
        
        capacity_repo = CapacityRepository(temp_db)
        
        # Create
        capacity = Capacity(
            worker_id=worker_id,
            start_date=datetime(2025, 10, 1),
            end_date=datetime(2025, 10, 31),
            planned_hours=160.0,
            notes="October capacity"
        )
        capacity_id = capacity_repo.create(capacity)
        
        # Retrieve
        retrieved = capacity_repo.find_by_id(capacity_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == capacity_id
        assert retrieved.worker_id == worker_id
        assert retrieved.planned_hours == 160.0
        assert retrieved.notes == "October capacity"
    
    def test_find_by_worker_with_overlapping_dates(self, temp_db, temp_crypto):
        """Test: Capacities mit überlappenden Zeiträumen finden"""
        # Setup Worker
        worker_repo = WorkerRepository(temp_db, temp_crypto)
        worker_id = worker_repo.create(Worker(name="Test", email="test@test.com", team="Team"))
        
        capacity_repo = CapacityRepository(temp_db)
        
        # Create capacities
        capacity_repo.create(Capacity(
            worker_id=worker_id,
            start_date=datetime(2025, 9, 1),
            end_date=datetime(2025, 9, 30),
            planned_hours=160.0
        ))
        capacity_repo.create(Capacity(
            worker_id=worker_id,
            start_date=datetime(2025, 10, 1),
            end_date=datetime(2025, 10, 31),
            planned_hours=160.0
        ))
        capacity_repo.create(Capacity(
            worker_id=worker_id,
            start_date=datetime(2025, 11, 1),
            end_date=datetime(2025, 11, 30),
            planned_hours=160.0
        ))
        
        # Find overlapping with October
        capacities = capacity_repo.find_by_worker(
            worker_id,
            start_date=datetime(2025, 10, 15),
            end_date=datetime(2025, 10, 20)
        )
        
        # Should find October capacity
        assert len(capacities) == 1
        assert capacities[0].start_date == datetime(2025, 10, 1)


class TestForeignKeyConstraints:
    """Tests für Foreign Key Constraints"""
    
    def test_cascade_delete_worker_deletes_entries(self, temp_db, temp_crypto):
        """Test: Löschen eines Workers sollte seine Zeiterfassungen löschen"""
        # Setup
        worker_repo = WorkerRepository(temp_db, temp_crypto)
        entry_repo = TimeEntryRepository(temp_db)
        
        # Create worker und entries
        worker_id = worker_repo.create(Worker(name="Test", email="test@test.com", team="Team"))
        
        entry_repo.create(TimeEntry(
            worker_id=worker_id,
            date=datetime(2025, 10, 6),
            duration_minutes=60,
            description="Entry 1"
        ))
        entry_repo.create(TimeEntry(
            worker_id=worker_id,
            date=datetime(2025, 10, 7),
            duration_minutes=90,
            description="Entry 2"
        ))
        
        # Verify entries exist
        entries_before = entry_repo.find_by_worker(worker_id)
        assert len(entries_before) == 2
        
        # Delete worker
        worker_repo.delete(worker_id)
        
        # Verify entries are deleted (CASCADE)
        entries_after = entry_repo.find_by_worker(worker_id)
        assert len(entries_after) == 0
