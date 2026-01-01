"""
Unit tests for data models
"""
import pytest
from datetime import datetime

from src.model.models import Entry


class TestEntry:
    """Unit tests for Entry model"""
    
    def test_create_entry_with_all_fields(self):
        """Test creating entry with all fields"""
        now = datetime.now()
        entry = Entry(
            id=1,
            name="Test",
            description="Description",
            value=42,
            created_at=now,
            updated_at=now
        )
        
        assert entry.id == 1
        assert entry.name == "Test"
        assert entry.description == "Description"
        assert entry.value == 42
        assert entry.created_at == now
        assert entry.updated_at == now
    
    def test_create_entry_with_defaults(self):
        """Test creating entry with default values"""
        entry = Entry()
        
        assert entry.id is None
        assert entry.name == ""
        assert entry.description == ""
        assert entry.value == 0
        assert entry.created_at is None
        assert entry.updated_at is None
    
    def test_to_dict_with_all_fields(self):
        """Test converting entry to dictionary"""
        now = datetime(2025, 1, 1, 12, 0, 0)
        entry = Entry(
            id=1,
            name="Test",
            description="Desc",
            value=99,
            created_at=now,
            updated_at=now
        )
        
        result = entry.to_dict()
        
        assert result == {
            'id': 1,
            'name': 'Test',
            'description': 'Desc',
            'value': 99,
            'created_at': '2025-01-01T12:00:00',
            'updated_at': '2025-01-01T12:00:00'
        }
