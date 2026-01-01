"""
Database configuration and connection management
"""
import os
import logging
from typing import Optional
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration from environment variables"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'bball_app')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        self.min_connections = int(os.getenv('DB_MIN_CONNECTIONS', '1'))
        self.max_connections = int(os.getenv('DB_MAX_CONNECTIONS', '10'))


class DatabaseConnection:
    """Database connection pool manager"""
    
    _pool: Optional[ConnectionPool] = None
    _config: Optional[DatabaseConfig] = None
    
    @classmethod
    def initialize(cls, config: Optional[DatabaseConfig] = None):
        """Initialize the connection pool"""
        if cls._pool is None:
            cls._config = config or DatabaseConfig()
            try:
                conninfo = f"host={cls._config.host} port={cls._config.port} dbname={cls._config.database} user={cls._config.user} password={cls._config.password}"
                cls._pool = ConnectionPool(
                    conninfo,
                    min_size=cls._config.min_connections,
                    max_size=cls._config.max_connections
                )
                logger.info(f"Database connection pool initialized for {cls._config.host}:{cls._config.port}")
            except Exception as e:
                logger.error(f"Failed to initialize database connection pool: {e}")
                raise
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool"""
        if cls._pool is None:
            cls.initialize()
        return cls._pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        """Return a connection to the pool"""
        if cls._pool is not None:
            cls._pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        """Close all connections in the pool"""
        if cls._pool is not None:
            cls._pool.close()
            cls._pool = None
            logger.info("Database connection pool closed")


def get_db_connection():
    """
    Context manager for database connections
    
    Usage:
        with get_db_connection() as conn:
            # use connection
    """
    class ConnectionContext:
        def __enter__(self):
            self.conn = DatabaseConnection.get_connection()
            self.conn.row_factory = dict_row
            return self.conn
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.conn.rollback()
            DatabaseConnection.return_connection(self.conn)
            return False
    
    return ConnectionContext()
