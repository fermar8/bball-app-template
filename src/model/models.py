"""
Database models for the application
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Entry:
    """
    Entry test model for the database table
    """
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    value: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
