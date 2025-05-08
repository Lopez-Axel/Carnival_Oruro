import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")  # Cambiado para usar SUPABASE_API_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL y SUPABASE_API_KEY deben estar configurados en el archivo .env")

class SupabaseClient:
    def __init__(self, url: str, key: str):
        self.base_url = url
        self.api_key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def select(self, table: str, columns: str = "*"):
        """
        Select data from a table
        """
        url = f"{self.base_url}/rest/v1/{table}?select={columns}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def insert(self, table: str, data: dict):
        """
        Insert data into a table
        """
        url = f"{self.base_url}/rest/v1/{table}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def update(self, table: str, data: dict, column: str, value: str):
        """
        Update data in a table
        """
        url = f"{self.base_url}/rest/v1/{table}?{column}=eq.{value}"
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
    
    async def delete(self, table: str, column: str, value: str):
        """
        Delete data from a table
        """
        url = f"{self.base_url}/rest/v1/{table}?{column}=eq.{value}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def filter(self, table: str, column: str, operator: str, value: str, columns: str = "*"):
        """
        Filter data from a table
        """
        url = f"{self.base_url}/rest/v1/{table}?select={columns}&{column}={operator}.{value}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def auth_user(self, token: str):
        """
        Get user data from auth token
        """
        # Usando SUPABASE_AUTH_URL específicamente para Auth
        auth_url = os.getenv("SUPABASE_AUTH_URL")
        url = f"{auth_url}/user"
        headers = {**self.headers, "Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return None

# Singleton instance
supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    return supabase