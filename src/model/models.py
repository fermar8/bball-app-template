"""
Database models for the application
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Entry:
    """
    Entry test model for the database table
    """
    name: str = ""
    value: int = 0
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
