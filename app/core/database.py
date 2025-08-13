from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings
from typing import Generator
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global flag to track initialization state
_db_initialized = False

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

def reset_database():
    """Reset database by dropping all tables and recreating them"""
    global _db_initialized
    try:
        logger.info("Resetting database...")
        drop_all_tables()
        _db_initialized = False  # Reset the flag
        create_db_and_tables()
        init_db()
        logger.info("Database reset completed successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise

def create_db_and_tables():
    """Create database tables if they don't exist"""
    try:
        # Only create tables if they don't exist (don't drop existing tables)
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created/verified successfully")
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

def is_database_initialized() -> bool:
    """Check if database is properly initialized"""
    try:
        with Session(engine) as session:
            from sqlmodel import select
            from app.models.user import User
            from app.models.access_control import Permission, Role
            
            # Check if basic tables exist and have data
            user_count = len(session.exec(select(User)).all())
            permission_count = len(session.exec(select(Permission)).all())
            role_count = len(session.exec(select(Role)).all())
            
            # Consider initialized if we have at least one user and some permissions/roles
            return user_count > 0 and (permission_count > 0 or role_count > 0)
    except Exception as e:
        logger.error(f"Error checking database initialization: {e}")
        return False

def init_db():
    """Initialize database with default data"""
    global _db_initialized
    
    # Prevent multiple initializations
    if _db_initialized:
        logger.info("Database already initialized, skipping...")
        return
    
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from datetime import datetime
    from app.services.access_control_service import AccessControlService
    
    try:
        with Session(engine) as session:
            # Check if admin user exists
            from sqlmodel import select
            from app.models.access_control import Role
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
                session.refresh(admin_user)
                logger.info("Default admin user created")
                
                # Initialize access control system
                access_service = AccessControlService(session)
                access_service.initialize_default_permissions()
                access_service.initialize_default_roles()
                
                # Initialize stage management system
                from app.services.stage_service import StageService
                stage_service = StageService(session)
                stage_service.initialize_default_stages()
                
                # Assign super_admin role to admin user
                try:
                    # Get super_admin role
                    super_admin_role = session.exec(
                        select(Role).where(Role.name == "super_admin")
                    ).first()
                    
                    if super_admin_role:
                        # Assign role to admin user
                        access_service.assign_role_to_user(
                            admin_user.id,
                            super_admin_role.id,
                            admin_user.id  # Self-assigned
                        )
                        logger.info("Super admin role assigned to default admin user")
                except Exception as e:
                    logger.error(f"Error assigning super admin role: {e}")
            else:
                logger.info("Admin user already exists, skipping user creation")
            
            # Mark as initialized
            _db_initialized = True
            logger.info("Database initialization completed successfully")
            
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        _db_initialized = False  # Reset flag on error
        raise 