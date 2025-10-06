"""
Unit Tests für WorkerRepository
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.repositories.worker_repository import WorkerRepository
from src.models.worker import Worker
from src.services.database_service import DatabaseService
from src.services.crypto_service import CryptoService


class TestWorkerRepository:
    """Tests für WorkerRepository"""
    
    @pytest.fixture
    def db_service(self):
        """Mock DatabaseService"""
        mock_db = Mock(spec=DatabaseService)
        mock_db.execute_query = MagicMock()
        return mock_db
    
    @pytest.fixture
    def crypto_service(self):
        """Mock CryptoService"""
        mock_crypto = Mock(spec=CryptoService)
        mock_crypto.encrypt = MagicMock(side_effect=lambda x: f"encrypted_{x}")
        mock_crypto.decrypt = MagicMock(side_effect=lambda x: x.replace("encrypted_", ""))
        return mock_crypto
    
    @pytest.fixture
    def repository(self, db_service, crypto_service):
        """Erstellt WorkerRepository für Tests"""
        return WorkerRepository(db_service, crypto_service)
    
    # Tests für create
    def test_create_worker_encrypts_sensitive_data(self, repository, db_service, crypto_service):
        """Test: Name und Email sollten verschlüsselt werden"""
        worker = Worker(
            name="Max Mustermann",
            email="max@example.com",
            team="Engineering"
        )
        
        # Mock Query Result
        mock_query = Mock()
        mock_query.lastInsertId = MagicMock(return_value=1)
        db_service.execute_query.return_value = mock_query
        
        # Act
        worker_id = repository.create(worker)
        
        # Assert
        assert worker_id == 1
        crypto_service.encrypt.assert_any_call("Max Mustermann")
        crypto_service.encrypt.assert_any_call("max@example.com")
        
        # Verify SQL call
        db_service.execute_query.assert_called_once()
        call_args = db_service.execute_query.call_args
        assert "INSERT INTO workers" in call_args[0][0]
        params = call_args[1]["params"] if len(call_args) > 1 and "params" in call_args[1] else call_args[0][1]
        assert params[0] == "encrypted_Max Mustermann"
        assert params[1] == "encrypted_max@example.com"
    
    def test_create_worker_with_inactive_status(self, repository, db_service, crypto_service):
        """Test: Worker mit active=False sollte korrekt gespeichert werden"""
        worker = Worker(
            name="Inactive User",
            email="inactive@example.com",
            team="Sales",
            active=False
        )
        
        mock_query = Mock()
        mock_query.lastInsertId = MagicMock(return_value=2)
        db_service.execute_query.return_value = mock_query
        
        worker_id = repository.create(worker)
        
        assert worker_id == 2
        call_args = db_service.execute_query.call_args
        params = call_args[1]["params"] if len(call_args) > 1 and "params" in call_args[1] else call_args[0][1]
        assert params[3] == 0  # active=False -> 0
    
    # Tests für find_by_id
    def test_find_by_id_decrypts_data(self, repository, db_service, crypto_service):
        """Test: Gefundener Worker sollte entschlüsselt werden"""
        # Mock Query Result
        mock_query = Mock()
        mock_query.next = MagicMock(return_value=True)
        mock_query.value = MagicMock(side_effect=lambda field: {
            "id": 1,
            "name": "encrypted_John Doe",
            "email": "encrypted_john@example.com",
            "team": "Marketing",
            "active": 1,
            "created_at": "2025-10-06T10:00:00"
        }[field])
        db_service.execute_query.return_value = mock_query
        
        # Act
        worker = repository.find_by_id(1)
        
        # Assert
        assert worker is not None
        assert worker.id == 1
        assert worker.name == "John Doe"  # Entschlüsselt
        assert worker.email == "john@example.com"  # Entschlüsselt
        assert worker.team == "Marketing"
        assert worker.active is True
        
        crypto_service.decrypt.assert_any_call("encrypted_John Doe")
        crypto_service.decrypt.assert_any_call("encrypted_john@example.com")
    
    def test_find_by_id_returns_none_if_not_found(self, repository, db_service):
        """Test: Nicht gefundener Worker sollte None zurückgeben"""
        mock_query = Mock()
        mock_query.next = MagicMock(return_value=False)
        db_service.execute_query.return_value = mock_query
        
        worker = repository.find_by_id(999)
        
        assert worker is None
    
    # Tests für find_all
    def test_find_all_returns_all_workers(self, repository, db_service, crypto_service):
        """Test: Alle Worker sollten zurückgegeben werden"""
        # Mock Query Result with multiple workers
        mock_query = Mock()
        call_count = [0]
        
        def next_side_effect():
            call_count[0] += 1
            return call_count[0] <= 2  # 2 Workers
        
        def value_side_effect(field):
            if call_count[0] == 1:
                return {
                    "id": 1,
                    "name": "encrypted_Worker1",
                    "email": "encrypted_w1@test.com",
                    "team": "Team A",
                    "active": 1,
                    "created_at": "2025-10-06T10:00:00"
                }[field]
            else:
                return {
                    "id": 2,
                    "name": "encrypted_Worker2",
                    "email": "encrypted_w2@test.com",
                    "team": "Team B",
                    "active": 0,
                    "created_at": "2025-10-06T11:00:00"
                }[field]
        
        mock_query.next = MagicMock(side_effect=next_side_effect)
        mock_query.value = MagicMock(side_effect=value_side_effect)
        db_service.execute_query.return_value = mock_query
        
        # Act
        workers = repository.find_all()
        
        # Assert
        assert len(workers) == 2
        assert workers[0].name == "Worker1"
        assert workers[1].name == "Worker2"
        assert workers[0].active is True
        assert workers[1].active is False
    
    def test_find_all_with_active_filter(self, repository, db_service):
        """Test: find_all mit active_only sollte Filter anwenden"""
        mock_query = Mock()
        mock_query.next = MagicMock(return_value=False)
        db_service.execute_query.return_value = mock_query
        
        repository.find_all(active_only=True)
        
        # Verify SQL includes WHERE clause
        call_args = db_service.execute_query.call_args
        assert "WHERE active = 1" in call_args[0][0]
    
    # Tests für update
    def test_update_worker_encrypts_data(self, repository, db_service, crypto_service):
        """Test: Update sollte Daten verschlüsseln"""
        worker = Worker(
            id=1,
            name="Updated Name",
            email="updated@example.com",
            team="New Team",
            active=True
        )
        
        mock_query = Mock()
        mock_query.numRowsAffected = MagicMock(return_value=1)
        db_service.execute_query.return_value = mock_query
        
        # Act
        result = repository.update(worker)
        
        # Assert
        assert result is True
        crypto_service.encrypt.assert_any_call("Updated Name")
        crypto_service.encrypt.assert_any_call("updated@example.com")
        
        call_args = db_service.execute_query.call_args
        assert "UPDATE workers" in call_args[0][0]
        params = call_args[1]["params"] if len(call_args) > 1 and "params" in call_args[1] else call_args[0][1]
        assert params[0] == "encrypted_Updated Name"
    
    def test_update_worker_returns_false_if_not_found(self, repository, db_service, crypto_service):
        """Test: Update sollte False zurückgeben wenn Worker nicht existiert"""
        worker = Worker(id=999, name="Test", email="test@test.com", team="Team")
        
        mock_query = Mock()
        mock_query.numRowsAffected = MagicMock(return_value=0)
        db_service.execute_query.return_value = mock_query
        
        result = repository.update(worker)
        
        assert result is False
    
    # Tests für delete
    def test_delete_worker(self, repository, db_service):
        """Test: Worker sollte gelöscht werden"""
        mock_query = Mock()
        mock_query.numRowsAffected = MagicMock(return_value=1)
        db_service.execute_query.return_value = mock_query
        
        result = repository.delete(1)
        
        assert result is True
        call_args = db_service.execute_query.call_args
        assert "DELETE FROM workers" in call_args[0][0]
        params = call_args[1]["params"] if len(call_args) > 1 and "params" in call_args[1] else call_args[0][1]
        assert params[0] == 1
    
    # Tests für find_by_email
    def test_find_by_email_searches_encrypted_email(self, repository, db_service, crypto_service):
        """Test: Suche nach Email sollte verschlüsselte Email verwenden"""
        mock_query = Mock()
        mock_query.next = MagicMock(return_value=True)
        mock_query.value = MagicMock(side_effect=lambda field: {
            "id": 1,
            "name": "encrypted_Test User",
            "email": "encrypted_test@example.com",
            "team": "Team",
            "active": 1,
            "created_at": "2025-10-06T10:00:00"
        }[field])
        db_service.execute_query.return_value = mock_query
        
        # Act
        worker = repository.find_by_email("test@example.com")
        
        # Assert
        assert worker is not None
        crypto_service.encrypt.assert_called_with("test@example.com")
        call_args = db_service.execute_query.call_args
        params = call_args[1]["params"] if len(call_args) > 1 and "params" in call_args[1] else call_args[0][1]
        assert params[0] == "encrypted_test@example.com"
