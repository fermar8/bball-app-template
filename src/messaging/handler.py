"""
Messaging/Handler layer for Lambda events
"""
import json
import logging
import os
from typing import Any, Dict
from jsonschema import validate, ValidationError

from src.service.service import Service
from src.repository.repository import Repository
from src.database.database import DynamoDBConnection

logger = logging.getLogger(__name__)

# Load JSON Schema
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schemas', 'lambda-event-schema.json')
with open(SCHEMA_PATH, 'r') as f:
    EVENT_SCHEMA = json.load(f)


class Handler:
    """Handler for DynamoDB operations via Lambda"""
    
    def __init__(self, service: Service = None):
        """
        Initialize the handler
        
        Args:
            service: Service instance (for dependency injection)
        """
        self.service = service
    
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Lambda event for CRUD operations
        
        Args:
            event: Lambda event with:
                - action: "create", "get", "list", "update", "delete"
                - data: Action-specific data
                
        Returns:
            Response with operation result
        """
        try:
            # Validate event against JSON schema
            validate(instance=event, schema=EVENT_SCHEMA)
            
            action = event.get('action', 'create')
            data = event.get('data', {})
            
            # Initialize service if not provided (for testing)
            if self.service is None:
                repository = Repository()
                self.service = Service(repository)
            
            if action == 'create':
                entry = self.service.create_test_entry(
                    name=data.get('name', 'Test Entry'),
                    value=data.get('value', 42)
                )
                logger.info(f"Created entry: {entry.id}")
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Entry created successfully',
                        'data': entry.to_dict()
                    })
                }
            
            elif action == 'get':
                entry_id = data.get('id')
                if not entry_id:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'ID is required'})
                    }
                
                entry = self.service.get_test_entry(entry_id)
                if not entry:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': 'Entry not found'})
                    }
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'data': entry.to_dict()
                    })
                }
            
            elif action == 'list':
                entries = self.service.list_test_entries()
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'data': [entry.to_dict() for entry in entries]
                    })
                }
            
            elif action == 'update':
                entry_id = data.get('id')
                if not entry_id:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'ID is required'})
                    }
                
                entry = self.service.update_test_entry(
                    entry_id,
                    name=data.get('name'),
                    value=data.get('value')
                )
                if not entry:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': 'Entry not found'})
                    }
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Entry updated successfully',
                        'data': entry.to_dict()
                    })
                }
            
            elif action == 'delete':
                entry_id = data.get('id')
                if not entry_id:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'ID is required'})
                    }
                
                deleted = self.service.delete_test_entry(entry_id)
                if not deleted:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': 'Entry not found'})
                    }
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Entry deleted successfully'
                    })
                }
            
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f'Unknown action: {action}'
                    })
                }
            
        except ValidationError as e:
            logger.warning(f"Schema validation error: {e.message}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Validation error: {e.message}'
                })
            }
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': str(e)
                })
            }
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Internal server error'
                })
            }


def lambda_handler(event, context):
    """
    Lambda function handler for bball-app-template
    
    Args:
        event: Lambda event data with:
            - action: "create", "get", "list", "update", "delete"
            - data: Action-specific data
        context: Lambda context object
        
    Returns:
        dict: Response object with statusCode and body
        
    Examples:
        Create: {"action": "create", "data": {"name": "test", "value": 42}}
        Get: {"action": "get", "data": {"id": "123-456"}}
        List: {"action": "list"}
        Update: {"action": "update", "data": {"id": "123-456", "name": "new name"}}
        Delete: {"action": "delete", "data": {"id": "123-456"}}
    """
    logger.setLevel(logging.INFO)
    logger.info("Processing Lambda request")
    logger.info(f"Event: {json.dumps(event)}")

    # Force a failure to test retry and DLQ behavior
    if event.get("action") == "test_failure":
        logger.error("Simulating failure for DLQ testing")
        raise RuntimeError("Intentional failure to test DLQ and retry mechanism")
    
    try:
        # Initialize DynamoDB connection (once per container)
        DynamoDBConnection.initialize()
        
        # Create handler and process request
        handler = Handler()
        response = handler.handle(event)
        
        logger.info(f"Response status: {response.get('statusCode')}")
        return response
        
    except Exception as e:
        logger.error(f"Unhandled error in lambda_handler: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }
