from typing import Dict, Any, Optional
from datetime import datetime, timezone
from database.connection import supabase


class ConfigRepository:
    def __init__(self):
        self.table = supabase.table("system_settings")

    def get_settings(self) -> Dict[str, Any]:
        """የሲስተሙን ወቅታዊ ቅንብሮች ያመጣል"""
        res = self.table.select("*").eq("id", 1).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return {
            "id": 1,
            "is_registration_active": True,
            "pinned_notice_text": "እንኳን ወደ Remedial Hub በደህና መጡ! ምዝገባ ክፍት ነው!",
            "pinned_notice_active": True
        }

    def toggle_registration_status(self, admin_id: int) -> bool:
        """የምዝገባውን ክፍት/ዝግ ሁኔታ ይቀይራል"""
        current = self.get_settings()
        new_state = not current.get("is_registration_active", True)
        self.table.update({
            "is_registration_active": new_state,
            "updated_by": admin_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", 1).execute()
        return new_state

    def update_pinned_notice(self, notice_text: Optional[str], active: bool, admin_id: int) -> bool:
        """የ Pinned ማስታወቂያ ጽሑፍን ያሻሽላል (Max 85 chars)"""
        if notice_text and len(notice_text) > 85:
            notice_text = notice_text[:85]

        data = {
            "pinned_notice_text": notice_text,
            "pinned_notice_active": active,
            "updated_by": admin_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        res = self.table.update(data).eq("id", 1).execute()
        return bool(res.data)


config_repo = ConfigRepository()