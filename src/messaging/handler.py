"""
Messaging/Handler layer for Lambda events
"""
import json
import logging
from typing import Any, Dict

from src.service.service import Service
from src.database.database import DatabaseConnection

logger = logging.getLogger(__name__)


class Handler:
    """Handler for database operations"""
    
    def __init__(self, service: Service = None):
        """
        Initialize the handler
        
        Args:
            service: Service instance (for dependency injection)
        """
        self.service = service or Service()
    
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Lambda event - creates a new entry in the database
        
        Args:
            event: Lambda event with:
                - name: Entry name (required)
                - description: Entry description (optional)
                - value: Entry value (optional)
                
        Returns:
            Response with created entry details
        """
        try:
            # Extract parameters from event
            name = event.get('name', 'Test Entry')
            description = event.get('description', 'Mock test entry')
            value = event.get('value', 42)
            
            # Create entry in database
            entry = self.service.create_test_entry(
                name=name,
                description=description,
                value=value
            )
            
            logger.info(f"Created test entry: {entry.id}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Entry created successfully',
                    'data': entry.to_dict()
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
            logger.error(f"Error creating entry: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Internal server error'
                })
            }


def lambda_handler(event, context):
    """
    Lambda function handler for bball-app-template
    Creates a test entry in the database
    
    Args:
        event: Lambda event data (should contain name, description, value)
        context: Lambda context object
        
    Returns:
        dict: Response object with statusCode and body
    """
    logger.setLevel(logging.INFO)
    logger.info("Processing Lambda request")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        # Initialize database connection pool (once per container)
        DatabaseConnection.initialize()
        
        # Initialize database schema
        service = Service()
        service.initialize_database()
        
        # Create handler and process request
        handler = Handler(service)
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
