"""
Unit tests for Service with mocked repository
"""
import pytest
from unittest.mock import Mock

from src.service.service import Service
from src.model.models import Entry


class TestServiceUnit:
    """Unit tests for Service"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mocked repository"""
        return Service(repository=mock_repository)
    
    def test_create_test_entry_success(self, service, mock_repository):
        """Test creating a valid entry"""
        # Setup mock
        expected_entry = Entry(
            id="123-456",
            name="Test Entry",
            value=42,
            created_at="2025-01-01T12:00:00",
            updated_at="2025-01-01T12:00:00"
        )
        mock_repository.create.return_value = expected_entry
        
        # Execute
        result = service.create_test_entry(
            name="Test Entry",
            value=42
        )
        
        # Assert
        assert result == expected_entry
        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args[0][0]
        assert call_args.name == "Test Entry"
        assert call_args.value == 42
    
    def test_get_test_entry(self, service, mock_repository):
        """Test getting an entry by ID"""
        expected_entry = Entry(id="123", name="Test", value=42)
        mock_repository.get_by_id.return_value = expected_entry
        
        result = service.get_test_entry("123")
        
        assert result == expected_entry
        mock_repository.get_by_id.assert_called_once_with("123")
    
    def test_list_test_entries(self, service, mock_repository):
        """Test listing all entries"""
        entries = [Entry(id="1", name="A", value=1), Entry(id="2", name="B", value=2)]
        mock_repository.get_all.return_value = entries
        
        result = service.list_test_entries()
        
        assert result == entries
        mock_repository.get_all.assert_called_once()
    
    def test_update_test_entry(self, service, mock_repository):
        """Test updating an entry"""
        updated_entry = Entry(id="123", name="Updated", value=100)
        mock_repository.update.return_value = updated_entry
        
        result = service.update_test_entry("123", name="Updated", value=100)
        
        assert result == updated_entry
        mock_repository.update.assert_called_once_with("123", name="Updated", value=100)
    
    def test_delete_test_entry(self, service, mock_repository):
        """Test deleting an entry"""
        mock_repository.delete.return_value = True
        
        result = service.delete_test_entry("123")
        
        assert result is True
        mock_repository.delete.assert_called_once_with("123")
