from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import create_db_and_tables, init_db, is_database_initialized
from app.api.v1.router import api_router
from supabase import create_client, Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Create tables first
        create_db_and_tables()
        
        # Check if database is already initialized
        if not is_database_initialized():
            init_db()  # Initialize with default data
        else:
            print("Database already initialized, skipping initialization")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Tamil Nadu Engineering College Counselling Backend API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stage access middleware
from app.middleware.stage_middleware import stage_access_middleware
app.middleware("http")(stage_access_middleware)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Tamil Nadu Engineering College Counselling API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

