"""
Repository layer for DynamoDB operations.
"""
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from decimal import Decimal

from src.database.database import DynamoDBConnection
from src.model.models import Entry
from boto3.dynamodb.conditions import Key


class Repository:
    """Data access layer for Entry model using DynamoDB."""
    
    def __init__(self):
        """Initialize repository with DynamoDB table."""
        self.table = DynamoDBConnection.get_table()
    
    def create(self, entry: Entry) -> Entry:
        """
        Create a new entry in DynamoDB.
        
        Args:
            entry: Entry object to create
            
        Returns:
            Created Entry object with generated ID and timestamps
        """
        # Generate ID if not provided
        if not entry.id:
            entry.id = str(uuid.uuid4())
        
        # Set timestamps
        now = datetime.now(timezone.utc).isoformat()
        if not entry.created_at:
            entry.created_at = now
        entry.updated_at = now
        
        # Convert to DynamoDB format
        item = {
            'id': entry.id,
            'name': entry.name,
            'value': Decimal(str(entry.value)),  # DynamoDB requires Decimal for numbers
            'created_at': entry.created_at,
            'updated_at': entry.updated_at
        }
        
        # Put item in DynamoDB
        self.table.put_item(Item=item)
        
        return entry
    
    def get_by_id(self, entry_id: str) -> Optional[Entry]:
        """
        Get an entry by ID.
        
        Args:
            entry_id: ID of the entry to retrieve
            
        Returns:
            Entry object if found, None otherwise
        """
        response = self.table.get_item(Key={'id': entry_id})
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        return Entry(
            id=item['id'],
            name=item['name'],
            value=int(item['value']),  # Convert Decimal back to int
            created_at=item.get('created_at'),
            updated_at=item.get('updated_at')
        )
    
    def get_all(self) -> List[Entry]:
        """
        Get all entries.
        
        Returns:
            List of all Entry objects
        """
        response = self.table.scan()
        items = response.get('Items', [])
        
        return [
            Entry(
                id=item['id'],
                name=item['name'],
                value=int(item['value']),
                created_at=item.get('created_at'),
                updated_at=item.get('updated_at')
            )
            for item in items
        ]
    
    def update(self, entry_id: str, name: Optional[str] = None, value: Optional[int] = None) -> Optional[Entry]:
        """
        Update an entry.
        
        Args:
            entry_id: ID of the entry to update
            name: New name (optional)
            value: New value (optional)
            
        Returns:
            Updated Entry object if found, None otherwise
        """
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_attr_values = {
            ':updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        if name is not None:
            update_expr += ", #n = :name"
            expr_attr_values[':name'] = name
        
        if value is not None:
            update_expr += ", #v = :value"
            expr_attr_values[':value'] = Decimal(str(value))
        
        # Attribute name aliases (reserved keywords)
        expr_attr_names = {}
        if name is not None:
            expr_attr_names['#n'] = 'name'
        if value is not None:
            expr_attr_names['#v'] = 'value'
        
        try:
            response = self.table.update_item(
                Key={'id': entry_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_attr_values,
                ExpressionAttributeNames=expr_attr_names if expr_attr_names else None,
                ReturnValues='ALL_NEW'
            )
            
            item = response['Attributes']
            return Entry(
                id=item['id'],
                name=item['name'],
                value=int(item['value']),
                created_at=item.get('created_at'),
                updated_at=item.get('updated_at')
            )
        except self.table.meta.client.exceptions.ResourceNotFoundException:
            return None
    
    def delete(self, entry_id: str) -> bool:
        """
        Delete an entry.
        
        Args:
            entry_id: ID of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            response = self.table.delete_item(
                Key={'id': entry_id},
                ReturnValues='ALL_OLD'
            )
            # Check if Attributes exists and is not empty
            return 'Attributes' in response and bool(response['Attributes'])
        except Exception:
            return False
