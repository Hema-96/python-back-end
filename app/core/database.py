from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings
from typing import Generator
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Disable verbose SQL logging
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

def drop_all_tables():
    """Drop all tables to recreate with new schema"""
    try:
        SQLModel.metadata.drop_all(engine)
        logger.info("All database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

def create_db_and_tables():
    """Create database tables"""
    try:
        # First drop all tables to ensure clean slate
        drop_all_tables()
        # Then create all tables with new schema
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

def init_db():
    """Initialize database with default data"""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from datetime import datetime
    
    with Session(engine) as session:
        # Check if admin user exists
        from sqlmodel import select
        statement = select(User).where(User.email == "admin@tncounselling.com")
        admin_user = session.exec(statement).first()
        
        if not admin_user:
            # Create default admin user
            admin_user = User(
                email="admin@tncounselling.com",
                password_hash=get_password_hash("admin123"),
                first_name="System",
                last_name="Administrator",
                role=UserRole.ADMIN,  # This will be stored as 1
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(admin_user)
            session.commit()
            logger.info("Default admin user created") 