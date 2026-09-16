from supabase import create_client, Client
from config.settings import settings


class SupabaseManager:
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY
            )
        return cls._instance


# Global instance access
supabase: Client = SupabaseManager.get_client()