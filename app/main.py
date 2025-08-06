from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import create_db_and_tables, init_db
from app.api.v1.router import api_router
from supabase import create_client, Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    init_db()  # Initialize with default data
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

# === Email Config ===
EMAIL_ADDRESS = "hemanarayanan11@gmail.com"           # Your Gmail
APP_PASSWORD = "hvfbkiwodkyqcsgz"       # Gmail App Password
TO_EMAIL = "hema@agilecyber.com"               # Receiver

@app.get("/send-email/")
def send_test_email():
    try:
        # Optional: You can query Supabase if needed
        user_info = supabase.auth.admin.list_users()  # Just to verify client works

        # Email content
        subject = "Test Email from FastAPI + Supabase"
        body = "This is a test email. Supabase is connected but not storing anything."

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = TO_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send via Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        server.quit()

        return {"status": "success", "message": f"Email sent to {TO_EMAIL}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

