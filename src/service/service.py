"""
Service layer for business logic
"""
import logging
from typing import List, Optional

from src.model.models import Entry
from src.repository import Repository

logger = logging.getLogger(__name__)


class Service:
    """Service for test entry business logic"""
    
    def __init__(self, repository: Repository = None):
        """
        Initialize the service
        
        Args:
            repository: TestRepository instance (for dependency injection)
        """
        self.repository = repository or Repository()
    
    def create_test_entry(self, name: str, description: str = "", value: int = 0) -> Entry:
        """
        Create a new test entry with validation
        
        Args:
            name: Entry name (required)
            description: Entry description (optional)
            value: Entry value (default: 0)
            
        Returns:
            Created Entry
            
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Name is required and cannot be empty")
        
        if len(name) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        
        if value < 0:
            raise ValueError("Value cannot be negative")
        
        # Create entry
        entry = Entry(
            name=name.strip(),
            description=description.strip() if description else "",
            value=value
        )
        
        logger.info(f"Creating test entry: {name}")
        created_entry = self.repository.create(entry)
        logger.info(f"Successfully created test entry with id: {created_entry.id}")
        
        return created_entry
    
    def get_test_entry(self, entry_id: int) -> Optional[Entry]:
        """
        Get a test entry by id
        
        Args:
            entry_id: The id of the entry to retrieve
            
        Returns:
            Entry or None if not found
        """
        if entry_id <= 0:
            raise ValueError("Entry ID must be positive")
        
        return self.repository.get_by_id(entry_id)
    
    def list_test_entries(self, limit: int = 100) -> List[Entry]:
        """
        List all entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of Entry objects
        """
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
        
        return self.repository.get_all(limit)
    
    def update_test_entry(
        self,
        entry_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        value: Optional[int] = None
    ) -> Optional[Entry]:
        """
        Update an existing test entry
        
        Args:
            entry_id: The id of the entry to update
            name: New name (optional)
            description: New description (optional)
            value: New value (optional)
            
        Returns:
            Updated Entry or None if not found
        """
        # Get existing entry
        existing_entry = self.repository.get_by_id(entry_id)
        if not existing_entry:
            return None
        
        # Update fields if provided
        if name is not None:
            if not name.strip():
                raise ValueError("Name cannot be empty")
            if len(name) > 255:
                raise ValueError("Name cannot exceed 255 characters")
            existing_entry.name = name.strip()
        
        if description is not None:
            existing_entry.description = description.strip()
        
        if value is not None:
            if value < 0:
                raise ValueError("Value cannot be negative")
            existing_entry.value = value
        
        logger.info(f"Updating test entry with id: {entry_id}")
        return self.repository.update(existing_entry)
    
    def delete_test_entry(self, entry_id: int) -> bool:
        """
        Delete a test entry
        
        Args:
            entry_id: The id of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        if entry_id <= 0:
            raise ValueError("Entry ID must be positive")
        
        logger.info(f"Deleting test entry with id: {entry_id}")
        return self.repository.delete(entry_id)
    
    def initialize_database(self):
        """Initialize database schema"""
        logger.info("Initializing database schema")
        self.repository.create_table_if_not_exists()
