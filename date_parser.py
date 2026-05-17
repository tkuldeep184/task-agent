"""Convert natural language dates to YYYY-MM-DD format."""

from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
import re


def parse_date(text):
    """
    Convert natural language date to YYYY-MM-DD string.
    Returns None if parsing fails.
    
    Handles: "tomorrow", "next Friday", "in 3 days", "2026-05-20", 
             "May 20", "next week", "monday", etc.
    """
    if not text:
        return None
    
    text = text.lower().strip()
    today = datetime.now().date()
    
    # Handle simple relative dates first
    if text in ['today']:
        return today.isoformat()
    
    if text in ['tomorrow']:
        return (today + timedelta(days=1)).isoformat()
    
    if text in ['day after tomorrow']:
        return (today + timedelta(days=2)).isoformat()
    
    # Handle "in X days" / "in X weeks"
    match = re.match(r'in (\d+) days?', text)
    if match:
        days = int(match.group(1))
        return (today + timedelta(days=days)).isoformat()
    
    match = re.match(r'in (\d+) weeks?', text)
    if match:
        weeks = int(match.group(1))
        return (today + timedelta(weeks=weeks)).isoformat()
    
    # Handle "next week" / "next month"
    if text == 'next week':
        return (today + timedelta(weeks=1)).isoformat()
    
    if text == 'next month':
        return (today + timedelta(days=30)).isoformat()
    
    # Handle "next monday", "next friday", etc.
    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    for day_name, day_num in weekdays.items():
        # "next friday" -> next occurrence of friday (always future)
        if text == f'next {day_name}':
            days_ahead = day_num - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).isoformat()
        
        # Just "friday" -> upcoming friday
        if text == day_name:
            days_ahead = day_num - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).isoformat()
    
    # Fallback: use dateutil for anything else (e.g., "May 20", "2026-05-20")
    try:
        parsed = dateutil_parser.parse(text, fuzzy=True, default=datetime.now())
        return parsed.date().isoformat()
    except (ValueError, TypeError):
        return None


def days_until(date_str):
    """Return number of days until the given YYYY-MM-DD date. Negative if past."""
    if not date_str:
        return None
    try:
        target = datetime.fromisoformat(date_str).date()
        today = datetime.now().date()
        return (target - today).days
    except (ValueError, TypeError):
        return None


def format_deadline(date_str):
    """Format a deadline for display: '2026-05-20 (in 3 days)' or '2026-05-15 (2 days overdue)'."""
    if not date_str:
        return ""
    
    days = days_until(date_str)
    if days is None:
        return date_str
    
    if days < 0:
        return f"{date_str} ({abs(days)} days overdue)"
    elif days == 0:
        return f"{date_str} (today)"
    elif days == 1:
        return f"{date_str} (tomorrow)"
    else:
        return f"{date_str} (in {days} days)"