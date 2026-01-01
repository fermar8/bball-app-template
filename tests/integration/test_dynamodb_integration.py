"""
Integration tests for DynamoDB operations using moto
"""
import os
import pytest
import boto3
from moto import mock_aws
from decimal import Decimal

from src.database.database import DynamoDBConnection
from src.repository.repository import Repository
from src.service.service import Service
from src.model.models import Entry


@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for moto"""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def dynamodb_table(aws_credentials):
    """Create a mock DynamoDB table for testing"""
    with mock_aws():
        # Set environment variable for table name
        os.environ['DYNAMODB_TABLE_NAME'] = 'test-table'
        
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create table
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'name', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'NameIndex',
                    'KeySchema': [
                        {'AttributeName': 'name', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Reset DynamoDB connection to force re-initialization with mocked resource
        DynamoDBConnection._table = None
        DynamoDBConnection._table_name = None
        
        yield table
        
        # Cleanup
        if 'DYNAMODB_TABLE_NAME' in os.environ:
            del os.environ['DYNAMODB_TABLE_NAME']


class TestRepositoryIntegration:
    """Integration tests for Repository with real DynamoDB operations (mocked)"""
    
    def test_create_entry(self, dynamodb_table):
        """Test creating an entry in DynamoDB"""
        repository = Repository()
        entry = Entry(name="Test Entry", value=42)
        
        result = repository.create(entry)
        
        assert result.id is not None
        assert result.name == "Test Entry"
        assert result.value == 42
        assert result.created_at is not None
        assert result.updated_at is not None
    
    def test_get_by_id(self, dynamodb_table):
        """Test retrieving an entry by ID"""
        repository = Repository()
        
        # Create entry
        entry = Entry(name="Test", value=10)
        created = repository.create(entry)
        
        # Get entry
        result = repository.get_by_id(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.name == "Test"
        assert result.value == 10
    
    def test_get_by_id_not_found(self, dynamodb_table):
        """Test getting non-existent entry returns None"""
        repository = Repository()
        
        result = repository.get_by_id("non-existent-id")
        
        assert result is None
    
    def test_get_all(self, dynamodb_table):
        """Test getting all entries"""
        repository = Repository()
        
        # Create multiple entries
        repository.create(Entry(name="Entry 1", value=10))
        repository.create(Entry(name="Entry 2", value=20))
        repository.create(Entry(name="Entry 3", value=30))
        
        # Get all
        results = repository.get_all()
        
        assert len(results) == 3
        assert all(isinstance(e, Entry) for e in results)
    
    def test_update_entry(self, dynamodb_table):
        """Test updating an entry"""
        repository = Repository()
        
        # Create entry
        entry = Entry(name="Original", value=10)
        created = repository.create(entry)
        
        # Update entry
        updated = repository.update(created.id, name="Updated", value=100)
        
        assert updated is not None
        assert updated.id == created.id
        assert updated.name == "Updated"
        assert updated.value == 100
        assert updated.updated_at != created.updated_at
    
    def test_update_partial(self, dynamodb_table):
        """Test updating only some fields"""
        repository = Repository()
        
        # Create entry
        entry = Entry(name="Original", value=10)
        created = repository.create(entry)
        
        # Update only name
        updated = repository.update(created.id, name="Updated Name")
        
        assert updated.name == "Updated Name"
        assert updated.value == 10  # Should remain unchanged
    
    def test_delete_entry(self, dynamodb_table):
        """Test deleting an entry"""
        repository = Repository()
        
        # Create entry
        entry = Entry(name="To Delete", value=999)
        created = repository.create(entry)
        
        # Delete entry
        result = repository.delete(created.id)
        
        assert result is True
        
        # Verify deletion
        deleted = repository.get_by_id(created.id)
        assert deleted is None
    
    def test_delete_nonexistent_entry(self, dynamodb_table):
        """Test deleting non-existent entry"""
        repository = Repository()
        
        result = repository.delete("non-existent-id")
        
        assert result is False


class TestServiceIntegration:
    """Integration tests for Service with real repository"""
    
    def test_create_with_validation(self, dynamodb_table):
        """Test creating entry through service with validation"""
        repository = Repository()
        service = Service(repository)
        
        result = service.create_test_entry(name="Test", value=42)
        
        assert result.id is not None
        assert result.name == "Test"
        assert result.value == 42
    
    def test_create_invalid_name(self, dynamodb_table):
        """Test creating entry with invalid name"""
        repository = Repository()
        service = Service(repository)
        
        with pytest.raises(ValueError, match="Name cannot be empty"):
            service.create_test_entry(name="", value=42)
    
    def test_create_negative_value(self, dynamodb_table):
        """Test creating entry with negative value"""
        repository = Repository()
        service = Service(repository)
        
        with pytest.raises(ValueError, match="must be non-negative"):
            service.create_test_entry(name="Test", value=-1)
    
    def test_get_entry(self, dynamodb_table):
        """Test getting entry through service"""
        repository = Repository()
        service = Service(repository)
        
        # Create entry
        created = service.create_test_entry(name="Test", value=10)
        
        # Get entry
        result = service.get_test_entry(created.id)
        
        assert result is not None
        assert result.id == created.id
    
    def test_list_entries(self, dynamodb_table):
        """Test listing entries through service"""
        repository = Repository()
        service = Service(repository)
        
        # Create entries
        service.create_test_entry(name="Entry 1", value=10)
        service.create_test_entry(name="Entry 2", value=20)
        
        # List entries
        results = service.list_test_entries()
        
        assert len(results) == 2
    
    def test_update_entry(self, dynamodb_table):
        """Test updating entry through service"""
        repository = Repository()
        service = Service(repository)
        
        # Create entry
        created = service.create_test_entry(name="Original", value=10)
        
        # Update entry
        updated = service.update_test_entry(created.id, name="Updated", value=100)
        
        assert updated.name == "Updated"
        assert updated.value == 100
    
    def test_delete_entry(self, dynamodb_table):
        """Test deleting entry through service"""
        repository = Repository()
        service = Service(repository)
        
        # Create entry
        created = service.create_test_entry(name="To Delete", value=999)
        
        # Delete entry
        result = service.delete_test_entry(created.id)
        
        assert result is True
        
        # Verify deletion
        deleted = service.get_test_entry(created.id)
        assert deleted is None
