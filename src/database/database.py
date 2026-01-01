"""
DynamoDB connection manager for AWS Lambda.
"""
import os
import boto3
from typing import Optional

class DynamoDBConnection:
    """Manages DynamoDB connection for Lambda function."""
    
    _table_name: Optional[str] = None
    _dynamodb_resource = None
    _table = None
    
    @classmethod
    def initialize(cls):
        """Initialize DynamoDB connection from environment variables."""
        cls._table_name = os.environ.get('DYNAMODB_TABLE_NAME')
        
        if not cls._table_name:
            raise ValueError("DYNAMODB_TABLE_NAME environment variable is not set")
        
        # Initialize boto3 DynamoDB resource
        cls._dynamodb_resource = boto3.resource('dynamodb')
        cls._table = cls._dynamodb_resource.Table(cls._table_name)
    
    @classmethod
    def get_table(cls):
        """Get the DynamoDB table resource."""
        if cls._table is None:
            cls.initialize()
        return cls._table
    
    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name."""
        if cls._table_name is None:
            cls.initialize()
        return cls._table_name
