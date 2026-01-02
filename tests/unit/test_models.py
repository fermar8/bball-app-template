"""
Unit tests for data models
"""
import pytest

from src.model.models import Entry


class TestEntry:
    """Unit tests for Entry model"""
    
    def test_create_entry_with_all_fields(self):
        """Test creating entry with all fields"""
        now = "2025-01-01T12:00:00"
        entry = Entry(
            id="123-456",
            name="Test",
            value=42,
            created_at=now,
            updated_at=now
        )
        
        assert entry.id == "123-456"
        assert entry.name == "Test"
        assert entry.value == 42
        assert entry.created_at == now
        assert entry.updated_at == now
    
    def test_create_entry_with_defaults(self):
        """Test creating entry with default values"""
        entry = Entry()
        
        assert entry.id is None
        assert entry.name == ""
        assert entry.value == 0
        assert entry.created_at is None
        assert entry.updated_at is None
    
    def test_to_dict_with_all_fields(self):
        """Test converting entry to dictionary"""
        now = "2025-01-01T12:00:00"
        entry = Entry(
            id="123",
            name="Test",
            value=99,
            created_at=now,
            updated_at=now
        )
        
        result = entry.to_dict()
        
        assert result['id'] == "123"
        assert result['name'] == "Test"
        assert result['value'] == 99
        assert result['created_at'] == now
        assert result['updated_at'] == now
    
    def test_to_dict_with_defaults(self):
        """Test converting entry with defaults to dictionary"""
        entry = Entry()
        
        result = entry.to_dict()
        
        assert result['id'] is None
        assert result['name'] == ""
        assert result['value'] == 0
        assert result['created_at'] is None
        assert result['updated_at'] is None
