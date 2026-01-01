"""
Repository layer for database operations
"""
import logging
from typing import List, Optional
from psycopg.rows import dict_row

from src.database.database import get_db_connection
from src.model.models import Entry

logger = logging.getLogger(__name__)


class Repository:
    """Repository for test table operations"""
    
    @staticmethod
    def create_table_if_not_exists():
        """Create the test table if it doesn't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            value INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_test_name ON test(name);
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_sql)
                    conn.commit()
                    logger.info("Test table created or already exists")
        except Exception as e:
            logger.error(f"Error creating test table: {e}")
            raise
    
    @staticmethod
    def create(entry: Entry) -> Entry:
        """
        Create a new test entry
        
        Args:
            entry: Entry object to create
            
        Returns:
            Entry: Created entry with id and timestamps
        """
        insert_sql = """
        INSERT INTO test (name, description, value)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, value, created_at, updated_at
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (entry.name, entry.description, entry.value))
                    result = cursor.fetchone()
                    conn.commit()
                    
                    created_entry = Entry(
                        id=result['id'],
                        name=result['name'],
                        description=result['description'],
                        value=result['value'],
                        created_at=result['created_at'],
                        updated_at=result['updated_at']
                    )
                    
                    logger.info(f"Created test entry with id: {created_entry.id}")
                    return created_entry
        except Exception as e:
            logger.error(f"Error creating test entry: {e}")
            raise
    
    @staticmethod
    def get_by_id(entry_id: int) -> Optional[Entry]:
        """
        Get a test entry by id
        
        Args:
            entry_id: The id of the entry to retrieve
            
        Returns:
            Entry or None if not found
        """
        select_sql = """
        SELECT id, name, description, value, created_at, updated_at
        FROM test
        WHERE id = %s
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(select_sql, (entry_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        return Entry(
                            id=result['id'],
                            name=result['name'],
                            description=result['description'],
                            value=result['value'],
                            created_at=result['created_at'],
                            updated_at=result['updated_at']
                        )
                    return None
        except Exception as e:
            logger.error(f"Error retrieving test entry: {e}")
            raise
    
    @staticmethod
    def get_all(limit: int = 100) -> List[Entry]:
        """
        Get all test entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of Entry objects
        """
        select_sql = """
        SELECT id, name, description, value, created_at, updated_at
        FROM test
        ORDER BY created_at DESC
        LIMIT %s
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(select_sql, (limit,))
                    results = cursor.fetchall()
                    
                    return [
                        Entry(
                            id=row['id'],
                            name=row['name'],
                            description=row['description'],
                            value=row['value'],
                            created_at=row['created_at'],
                            updated_at=row['updated_at']
                        )
                        for row in results
                    ]
        except Exception as e:
            logger.error(f"Error retrieving test entries: {e}")
            raise
    
    @staticmethod
    def update(entry: Entry) -> Optional[Entry]:
        """
        Update an existing test entry
        
        Args:
            entry: Entry object with updated values
            
        Returns:
            Updated Entry or None if not found
        """
        update_sql = """
        UPDATE test
        SET name = %s, description = %s, value = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, name, description, value, created_at, updated_at
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(update_sql, (entry.name, entry.description, entry.value, entry.id))
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if result:
                        return Entry(
                            id=result['id'],
                            name=result['name'],
                            description=result['description'],
                            value=result['value'],
                            created_at=result['created_at'],
                            updated_at=result['updated_at']
                        )
                    return None
        except Exception as e:
            logger.error(f"Error updating test entry: {e}")
            raise
    
    @staticmethod
    def delete(entry_id: int) -> bool:
        """
        Delete a test entry
        
        Args:
            entry_id: The id of the entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        delete_sql = "DELETE FROM test WHERE id = %s"
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(delete_sql, (entry_id,))
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    if deleted_count > 0:
                        logger.info(f"Deleted test entry with id: {entry_id}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"Error deleting test entry: {e}")
            raise
