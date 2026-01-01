"""
Unit tests for messaging/handler layer with mocked service
"""
import json
import pytest
from unittest.mock import Mock
from datetime import datetime

from src.messaging.handler import Handler
from src.model.models import Entry


class TestHandlerUnit:
    """Unit tests for Handler"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service"""
        return Mock()
    
    @pytest.fixture
    def handler(self, mock_service):
        """Create handler with mocked service"""
        return Handler(service=mock_service)
    
    def test_handle_success(self, handler, mock_service):
        """Test successful creation request"""
        # Setup
        created_entry = Entry(
            id=1,
            name="Test Entry",
            description="Mock test entry",
            value=42,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_service.create_test_entry.return_value = created_entry
        
        event = {
            'name': 'Test Entry',
            'description': 'Mock test entry',
            'value': 42
        }
        
        # Execute
        response = handler.handle(event)
        
        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Entry created successfully'
        assert body['data']['id'] == 1
        assert body['data']['name'] == 'Test Entry'
        
        mock_service.create_test_entry.assert_called_once_with(
            name='Test Entry',
            description='Mock test entry',
            value=42
        )
    
    def test_handle_with_defaults(self, handler, mock_service):
        """Test creation with default values"""
        created_entry = Entry(id=1, name="Test Entry", description="Mock test entry", value=42)
        mock_service.create_test_entry.return_value = created_entry
        
        event = {}
        
        response = handler.handle(event)
        
        assert response['statusCode'] == 200
        mock_service.create_test_entry.assert_called_once_with(
            name='Test Entry',
            description='Mock test entry',
            value=42
        )
    
    def test_handle_validation_error(self, handler, mock_service):
        """Test creation with validation error from service"""
        mock_service.create_test_entry.side_effect = ValueError("Name is required")
        
        event = {'name': ''}
        
        response = handler.handle(event)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Name is required'
    
    def test_handle_internal_error(self, handler, mock_service):
        """Test creation with unexpected error"""
        mock_service.create_test_entry.side_effect = Exception("Database error")
        
        event = {'name': 'Test'}
        
        response = handler.handle(event)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['error'] == 'Internal server error'
