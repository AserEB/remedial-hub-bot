import os
from typing import List
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


class Settings:
    # Telegram Bot Token
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

    # Channel & Group Configurations
    REQUIRED_CHANNEL_USERNAME: str = os.getenv("REQUIRED_CHANNEL_USERNAME", "@Remedial_Hub").strip()
    REQUIRED_CHANNEL_ID: int = int(os.getenv("REQUIRED_CHANNEL_ID", "-1001852983055"))
    NATURAL_GROUP_ID: int = int(os.getenv("NATURAL_GROUP_ID", "-1004296586498"))
    SOCIAL_GROUP_ID: int = int(os.getenv("SOCIAL_GROUP_ID", "-1004488651652"))

    # Admin Telegram IDs
    ADMIN_IDS_STR: str = os.getenv("ADMIN_IDS", "5034405093,1498230374,6511741820,5570011875")
    ADMIN_CONTACT_USERNAME: str = os.getenv("ADMIN_CONTACT_USERNAME", "Remedial_Admin").strip()

    # Supabase API Credentials
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "").strip()

    # Payment Accounts Information
    CBE_ACCOUNT_NUMBER: str = os.getenv("CBE_ACCOUNT_NUMBER", "1000505701066").strip()
    CBE_ACCOUNT_NAME: str = os.getenv("CBE_ACCOUNT_NAME", "Amanuel Mulugeta Negera").strip()
    ABYSSINIA_ACCOUNT_NUMBER: str = os.getenv("ABYSSINIA_ACCOUNT_NUMBER", "187858787").strip()
    ABYSSINIA_ACCOUNT_NAME: str = os.getenv("ABYSSINIA_ACCOUNT_NAME", "Amanuel Mulugeta Negera").strip()
    REGISTRATION_FEE_ETB: int = int(os.getenv("REGISTRATION_FEE_ETB", "500"))

    @property
    def admin_ids(self) -> List[int]:
        return [int(admin_id.strip()) for admin_id in self.ADMIN_IDS_STR.split(",") if admin_id.strip()]


settings = Settings()