"""
MongoDB Connection Configuration for AI Service
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if not already loaded
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """
    MongoDB connection manager for AI service
    """
    
    _client: MongoClient = None
    _db = None
    
    @classmethod
    def connect(cls):
        """
        Connect to MongoDB
        """
        if cls._client is not None:
            return cls._db
        
        mongo_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("MONGODB_DB_NAME", "unimate")
        
        if not mongo_uri:
            logger.warning("MONGODB_URI not set. Some features may not work.")
            return None
        
        try:
            cls._client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=30000,  # 30 seconds for server selection
                connectTimeoutMS=30000,  # 30 seconds for connection
                socketTimeoutMS=120000,  # 120 seconds for socket operations (writes can be slow)
                maxPoolSize=50,  # Increase connection pool
                retryWrites=True  # Enable retry for writes
            )
            
            # Test connection
            cls._client.admin.command('ping')
            cls._db = cls._client[db_name]
            
            logger.info(f"MongoDB connected: {db_name}")
            return cls._db
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {e}")
            cls._client = None
            return None
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            cls._client = None
            return None
    
    @classmethod
    def get_db(cls):
        """
        Get database instance
        """
        if cls._db is None:
            cls.connect()
        return cls._db
    
    @classmethod
    def disconnect(cls):
        """
        Disconnect from MongoDB
        """
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("MongoDB disconnected")

