from app.models.user import UserCreate
from app.supabase_client import get_supabase_client

supabase = get_supabase_client()

async def create_user(user: UserCreate) -> dict:
    """
    Create a new user in Supabase based on Google authentication data
    """
    user_data = user.dict()
    
    # Check if user already exists
    existing_user = await get_user_by_google_id(user.google_id)
    if existing_user and len(existing_user) > 0:
        return existing_user[0]
    
    # Create new user
    result = await supabase.insert("users", user_data)
    
    # Return the created user
    if result:
        return result[0]
    return None

async def get_user(user_id: str) -> dict | None:
    """
    Get a user by their Supabase ID
    """
    result = await supabase.filter("users", "id", "eq", user_id)
    
    if result and len(result) > 0:
        return result[0]
    return None

async def get_user_by_google_id(google_id: str) -> list[dict] | None:
    """
    Get a user by their Google ID
    """
    result = await supabase.filter("users", "google_id", "eq", google_id)
    
    if result:
        return result
    return None

async def get_user_by_email(email: str) -> dict | None:
    """
    Get a user by their email
    """
    result = await supabase.filter("users", "email", "eq", email)
    
    if result and len(result) > 0:
        return result[0]
    return None

async def get_users(skip: int = 0, limit: int = 100) -> list[dict]:
    """
    Get a list of users with pagination
    """
    # Using standard select since we don't have pagination in our client yet
    result = await supabase.select("users")
    
    if result:
        # Manual pagination
        return result[skip:skip+limit]
    return []

async def update_user(user_id: str, user_data: dict) -> dict | None:
    """
    Update a user by their ID
    """
    result = await supabase.update("users", user_data, "id", user_id)
    
    if result and len(result) > 0:
        return result[0]
    return None

async def delete_user(user_id: str) -> bool:
    """
    Delete a user by their ID
    """
    result = await supabase.delete("users", "id", user_id)
    
    return result is not None and len(result) > 0

