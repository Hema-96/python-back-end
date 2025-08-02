import re
from typing import Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format (Indian)"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None

def validate_pincode(pincode: str) -> bool:
    """Validate Indian pincode format"""
    pattern = r'^[1-9][0-9]{5}$'
    return re.match(pattern, pincode) is not None

def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age

def format_datetime(dt: datetime) -> str:
    """Format datetime to string"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def parse_datetime(date_string: str) -> Optional[datetime]:
    """Parse datetime string"""
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except ValueError:
        return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def generate_reference_id(prefix: str = "TN") -> str:
    """Generate a unique reference ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    import random
    random_suffix = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    return f"{prefix}{timestamp}{random_suffix}" 