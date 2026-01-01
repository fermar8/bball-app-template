"""
Unit tests for Service with mocked repository
"""
import pytest
from unittest.mock import Mock
from datetime import datetime

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
            id=1,
            name="Test Entry",
            description="Test Description",
            value=42,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repository.create.return_value = expected_entry
        
        # Execute
        result = service.create_test_entry(
            name="Test Entry",
            description="Test Description",
            value=42
        )
        
        # Assert
        assert result == expected_entry
        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args[0][0]
        assert call_args.name == "Test Entry"
        assert call_args.description == "Test Description"
        assert call_args.value == 42
    
    def test_create_test_entry_empty_name(self, service, mock_repository):
        """Test creating entry with empty name fails"""
        with pytest.raises(ValueError, match="Name is required"):
            service.create_test_entry(name="")
        
        mock_repository.create.assert_not_called()
    
    def test_create_test_entry_negative_value(self, service, mock_repository):
        """Test creating entry with negative value fails"""
        with pytest.raises(ValueError, match="cannot be negative"):
            service.create_test_entry(name="Test", value=-1)
        
        mock_repository.create.assert_not_called()
    
    def test_initialize_database(self, service, mock_repository):
        """Test database initialization"""
        service.initialize_database()
        
        mock_repository.create_table_if_not_exists.assert_called_once()
