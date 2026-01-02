"""
Service layer with business logic.
"""
from typing import Optional, List

from src.repository.repository import Repository
from src.model.models import Entry


class Service:
    """Business logic layer for Entry operations."""
    
    def __init__(self, repository: Repository):
        """Initialize service with repository."""
        self.repository = repository
    
    def create_test_entry(self, name: str, value: int) -> Entry:
        """
        Create a new test entry.
        
        Args:
            name: Name of the entry
            value: Value of the entry
            
        Returns:
            Created Entry object
        """
        # Create entry
        entry = Entry(name=name, value=value)
        return self.repository.create(entry)
    
    def get_test_entry(self, entry_id: str) -> Optional[Entry]:
        """
        Get a test entry by ID.
        
        Args:
            entry_id: ID of the entry
            
        Returns:
            Entry object if found, None otherwise
        """
        return self.repository.get_by_id(entry_id)
    
    def list_test_entries(self) -> List[Entry]:
        """
        List all test entries.
        
        Returns:
            List of all Entry objects
        """
        return self.repository.get_all()
    
    def update_test_entry(self, entry_id: str, name: Optional[str] = None, 
                         value: Optional[int] = None) -> Optional[Entry]:
        """
        Update a test entry with validation.
        
        Args:
            entry_id: ID of the entry to update
            name: New name (optional, must not be empty if provided)
            value: New value (optional, must be non-negative if provided)
            
        Returns:
            Updated Entry object if found, None otherwise
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if name is not None and (not name or not name.strip()):
            raise ValueError("Name cannot be empty")
        
        if value is not None and value < 0:
            raise ValueError("Value must be non-negative")
        
        # Update entry
        name_to_update = name.strip() if name else None
        return self.repository.update(entry_id, name=name_to_update, value=value)
    
    def delete_test_entry(self, entry_id: str) -> bool:
        """
        Delete a test entry.
        
        Args:
            entry_id: ID of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(entry_id)
