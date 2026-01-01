"""
Unit tests for messaging/handler layer with mocked service
"""
import json
import pytest
from unittest.mock import Mock

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
    
    def test_handle_create_success(self, handler, mock_service):
        """Test successful create action"""
        # Setup
        created_entry = Entry(
            id="123-456",
            name="Test Entry",
            value=42,
            created_at="2025-01-01T12:00:00",
            updated_at="2025-01-01T12:00:00"
        )
        mock_service.create_test_entry.return_value = created_entry
        
        event = {
            'action': 'create',
            'data': {
                'name': 'Test Entry',
                'value': 42
            }
        }
        
        # Execute
        response = handler.handle(event)
        
        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Entry created successfully'
        assert body['data']['id'] == "123-456"
        assert body['data']['name'] == 'Test Entry'
        
        mock_service.create_test_entry.assert_called_once_with(
            name='Test Entry',
            value=42
        )
    
    def test_handle_get_success(self, handler, mock_service):
        """Test successful get action"""
        entry = Entry(id="123", name="Test", value=42)
        mock_service.get_test_entry.return_value = entry
        
        event = {'action': 'get', 'data': {'id': '123'}}
        response = handler.handle(event)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['data']['id'] == '123'
        mock_service.get_test_entry.assert_called_once_with('123')
    
    def test_handle_get_not_found(self, handler, mock_service):
        """Test get action with non-existent entry"""
        mock_service.get_test_entry.return_value = None
        
        event = {'action': 'get', 'data': {'id': '999'}}
        response = handler.handle(event)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['error'] == 'Entry not found'
    
    def test_handle_list_success(self, handler, mock_service):
        """Test successful list action"""
        entries = [
            Entry(id="1", name="Entry 1", value=10),
            Entry(id="2", name="Entry 2", value=20)
        ]
        mock_service.list_test_entries.return_value = entries
        
        event = {'action': 'list'}
        response = handler.handle(event)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body['data']) == 2
        assert body['data'][0]['id'] == '1'
    
    def test_handle_update_success(self, handler, mock_service):
        """Test successful update action"""
        updated_entry = Entry(id="123", name="Updated", value=100)
        mock_service.update_test_entry.return_value = updated_entry
        
        event = {'action': 'update', 'data': {'id': '123', 'name': 'Updated', 'value': 100}}
        response = handler.handle(event)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Entry updated successfully'
        assert body['data']['name'] == 'Updated'
    
    def test_handle_delete_success(self, handler, mock_service):
        """Test successful delete action"""
        mock_service.delete_test_entry.return_value = True
        
        event = {'action': 'delete', 'data': {'id': '123'}}
        response = handler.handle(event)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Entry deleted successfully'
    
    def test_handle_validation_error(self, handler, mock_service):
        """Test action with validation error from service"""
        mock_service.create_test_entry.side_effect = ValueError("Name cannot be empty")
        
        event = {'action': 'create', 'data': {'name': ''}}
        response = handler.handle(event)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Name cannot be empty'
    
    def test_handle_unknown_action(self, handler, mock_service):
        """Test unknown action"""
        event = {'action': 'unknown'}
        response = handler.handle(event)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Unknown action' in body['error']
