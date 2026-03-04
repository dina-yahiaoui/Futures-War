"""
CRUD operations for generations table (Pure SQLite)
"""

from .database import execute_query, fetch_one, get_db
from datetime import datetime


def create_generation(prompt: str, image_path: str, is_sfw: bool = True, flagged_reason: str = None):
    """
    Create a new generation record
    
    Args:
        prompt: The AI prompt used
        image_path: Path to generated image
        is_sfw: Safe For Work status
        flagged_reason: Reason if blocked
        
    Returns:
        dict with id and other fields
    """
    query = """
        INSERT INTO generations (prompt, image_path, is_sfw, flagged_reason)
        VALUES (?, ?, ?, ?)
    """
    cursor = execute_query(query, (prompt, image_path, is_sfw, flagged_reason))
    
    # Get the inserted record
    return {
        "id": cursor.lastrowid,
        "prompt": prompt,
        "image_path": image_path,
        "is_sfw": is_sfw,
        "flagged_reason": flagged_reason,
        "created_at": datetime.utcnow().isoformat()
    }


def get_generation(gen_id: int):
    """Get a generation by ID"""
    query = "SELECT * FROM generations WHERE id = ?"
    row = fetch_one(query, (gen_id,))
    
    if row:
        return dict(row)
    return None


def get_all_generations(limit: int = 50, offset: int = 0):
    """Get all generations with pagination"""
    query = "SELECT * FROM generations ORDER BY created_at DESC LIMIT ? OFFSET ?"
    rows = fetch_one(query, (limit, offset))
    
    return [dict(row) for row in rows] if rows else []


def get_sfw_stats():
    """Get SFW filtering statistics"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total requests
        cursor.execute("SELECT COUNT(*) as total FROM generations")
        total = cursor.fetchone()["total"]
        
        # SFW pass
        cursor.execute("SELECT COUNT(*) as passed FROM generations WHERE is_sfw = 1")
        passed = cursor.fetchone()["passed"]
        
        # SFW blocked
        cursor.execute("SELECT COUNT(*) as blocked FROM generations WHERE is_sfw = 0")
        blocked = cursor.fetchone()["blocked"]
        
        return {
            "total": total,
            "passed": passed,
            "blocked": blocked,
            "pass_rate": round(100 * passed / total, 2) if total > 0 else 0
        }
