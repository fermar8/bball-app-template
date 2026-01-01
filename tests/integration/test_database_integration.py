"""
Integration tests for database operations
"""
import os
import pytest
import psycopg
from psycopg import IsolationLevel

from src.database.database import DatabaseConnection, DatabaseConfig
from src.model.models import Entry
from src.repository import Repository
from src.service import Service


@pytest.fixture(scope='session')
def test_db_config():
    """Create test database configuration"""
    # Create config with hardcoded test values to avoid Windows env var encoding issues
    config = DatabaseConfig()
    # Override with explicit ASCII-safe test values
    config.host = 'localhost'
    config.port = 5433
    config.user = 'testuser'
    config.password = 'testpassword'
    config.database = 'testdb'
    config.min_connections = 1
    config.max_connections = 5
    return config


@pytest.fixture(scope='session')
def test_database(test_db_config):
    """Create and drop test database"""
    # Use connection string to avoid Windows encoding issues
    conn_string = f"postgresql://{test_db_config.user}:{test_db_config.password}@{test_db_config.host}:{test_db_config.port}/postgres"
    
    # Connect to default database to create test database
    conn = psycopg.connect(conn_string, autocommit=True)
    cursor = conn.cursor()
    
    # Drop test database if exists
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config.database}_test")
    
    # Create test database
    cursor.execute(f"CREATE DATABASE {test_db_config.database}_test")
    
    cursor.close()
    conn.close()
    
    # Update config to use test database
    test_db_config.database = f"{test_db_config.database}_test"
    
    yield test_db_config
    
    # Cleanup: drop test database
    conn_string = f"postgresql://{test_db_config.user}:{test_db_config.password}@{test_db_config.host}:{test_db_config.port}/postgres"
    conn = psycopg.connect(conn_string, autocommit=True)
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config.database}")
    cursor.close()
    conn.close()


@pytest.fixture(scope='function')
def db_connection(test_database):
    """Initialize database connection for each test"""
    DatabaseConnection.initialize(test_database)
    
    # Create tables
    Repository().create_table_if_not_exists()
    
    yield
    
    # Cleanup: truncate table after each test
    from src.database.database import get_db_connection
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE test RESTART IDENTITY CASCADE")
            conn.commit()
    
    # Close all connections
    DatabaseConnection.close_all()


class TestRepositoryIntegration:
    """Integration tests for Repository"""
    
    def test_create_table(self, db_connection):
        """Test table creation"""
        # Table should already be created by fixture
        from src.database.database import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'test'
                    )
                """)
                exists = cursor.fetchone()[0]
                assert exists is True
    
    def test_create_entry(self, db_connection):
        """Test creating an entry"""
        repository = Repository()
        entry = Entry(name="Test Entry", description="Test Description", value=42)
        created = repository.create(entry)
        
        assert created.id is not None
        assert created.name == "Test Entry"
        assert created.description == "Test Description"
        assert created.value == 42
        assert created.created_at is not None
        assert created.updated_at is not None
    
    def test_get_by_id(self, db_connection):
        """Test retrieving an entry by id"""
        repository = Repository()
        # Create entry
        entry = Entry(name="Test Entry", description="Test", value=10)
        created = repository.create(entry)
        
        # Retrieve entry
        retrieved = repository.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
        assert retrieved.value == created.value
    
    def test_get_by_id_not_found(self, db_connection):
        """Test retrieving non-existent entry"""
        repository = Repository()
        retrieved = repository.get_by_id(9999)
        assert retrieved is None
    
    def test_get_all(self, db_connection):
        """Test retrieving all entries"""
        repository = Repository()
        # Create multiple entries
        repository.create(Entry(name="Entry 1", value=1))
        repository.create(Entry(name="Entry 2", value=2))
        repository.create(Entry(name="Entry 3", value=3))
        
        # Retrieve all
        entries = repository.get_all()
        
        assert len(entries) == 3
        assert all(isinstance(e, Entry) for e in entries)
    
    def test_update_entry(self, db_connection):
        """Test updating an entry"""
        repository = Repository()
        # Create entry
        entry = Entry(name="Original", description="Original Desc", value=1)
        created = repository.create(entry)
        
        # Update entry
        created.name = "Updated"
        created.description = "Updated Desc"
        created.value = 99
        updated = repository.update(created)
        
        assert updated is not None
        assert updated.name == "Updated"
        assert updated.description == "Updated Desc"
        assert updated.value == 99
    
    def test_delete_entry(self, db_connection):
        """Test deleting an entry"""
        repository = Repository()
        # Create entry
        entry = Entry(name="To Delete", value=1)
        created = repository.create(entry)
        
        # Delete entry
        deleted = repository.delete(created.id)
        assert deleted is True
        
        # Verify deletion
        retrieved = repository.get_by_id(created.id)
        assert retrieved is None
    
    def test_delete_nonexistent_entry(self, db_connection):
        """Test deleting non-existent entry"""
        repository = Repository()
        deleted = repository.delete(9999)
        assert deleted is False


class TestServiceIntegration:
    """Integration tests for Service"""
    
    def test_create_with_validation(self, db_connection):
        """Test creating entry through service with validation"""
        service = Service()
        entry = service.create_test_entry(
            name="Service Test",
            description="Created via service",
            value=100
        )
        
        assert entry.id is not None
        assert entry.name == "Service Test"
        assert entry.value == 100
    
    def test_create_invalid_name(self, db_connection):
        """Test creating entry with invalid name"""
        service = Service()
        
        with pytest.raises(ValueError, match="Name is required"):
            service.create_test_entry(name="")
    
    def test_create_negative_value(self, db_connection):
        """Test creating entry with negative value"""
        service = Service()
        
        with pytest.raises(ValueError, match="cannot be negative"):
            service.create_test_entry(name="Test", value=-1)
    
    def test_get_entry(self, db_connection):
        """Test getting entry through service"""
        service = Service()
        created = service.create_test_entry(name="Get Test")
        
        retrieved = service.get_test_entry(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
    
    def test_list_entries(self, db_connection):
        """Test listing entries through service"""
        service = Service()
        service.create_test_entry(name="Entry 1")
        service.create_test_entry(name="Entry 2")
        
        entries = service.list_test_entries()
        assert len(entries) == 2
    
    def test_update_entry(self, db_connection):
        """Test updating entry through service"""
        service = Service()
        created = service.create_test_entry(name="Original")
        
        updated = service.update_test_entry(
            created.id,
            name="Modified",
            value=200
        )
        
        assert updated is not None
        assert updated.name == "Modified"
        assert updated.value == 200
    
    def test_delete_entry(self, db_connection):
        """Test deleting entry through service"""
        service = Service()
        created = service.create_test_entry(name="To Delete")
        
        deleted = service.delete_test_entry(created.id)
        assert deleted is True
        
        retrieved = service.get_test_entry(created.id)
        assert retrieved is None
