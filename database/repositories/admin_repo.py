from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from database.connection import supabase
from config.constants import STATUS_VERIFIED, STATUS_DISCARDED


class AdminRepository:
    def __init__(self):
        self.students_table = supabase.table("students")
        self.logs_table = supabase.table("registration_logs")

    def acquire_processing_lock(
        self,
        student_id: int,
        admin_id: int,
        admin_name: str,
        lock_seconds: int = 120
    ) -> Tuple[bool, str]:
        """
        Concurrency Locking:
        አንድ አድሚን ውሳኔ መስጠት ሲጀምር ለ 120 ሰከንድ lock ያደርጋል[cite: 1]።
        ሌላ አድሚን ቢሞክር Alert ያሳያል[cite: 1]።
        """
        res = self.students_table.select("*").eq("telegram_id", student_id).execute()
        if not res.data:
            return False, "ተማሪው በዳታቤዝ ውስጥ አልተገኘም!"

        student = res.data[0]

        # 1. ቀድሞ ውሳኔ ከተሰጠበት
        if student.get("status") in [STATUS_VERIFIED, STATUS_DISCARDED]:
            by_who = student.get("processed_by_admin_name") or "ሌላ አድሚን"
            return False, f"ይህ ተማሪ ቀደም ሲል በ {by_who} ውሳኔ ተሰጥቶበታል!"

        lock_by = student.get("processing_lock_by")
        lock_until_str = student.get("processing_lock_until")

        now = datetime.now(timezone.utc)

        # 2. በሌላ አድሚን ተይዞ ከሆነና ጊዜው ካላለቀ
        if lock_by and lock_by != admin_id and lock_until_str:
            lock_until = datetime.fromisoformat(lock_until_str.replace("Z", "+00:00"))
            if lock_until > now:
                return False, f"አሁን በ {student.get('processed_by_admin_name', 'ሌላ አድሚን')} ውሳኔ እየተሰጠበት ነው!"

        # 3. Lock መያዝ
        expire_at = now + timedelta(seconds=lock_seconds)
        self.students_table.update({
            "processing_lock_by": admin_id,
            "processing_lock_until": expire_at.isoformat(),
            "processed_by_admin_name": admin_name
        }).eq("telegram_id", student_id).execute()

        return True, "Lock ተሳክቷል"

    def verify_student(
        self,
        student_id: int,
        admin_id: int,
        admin_name: str,
        invite_link: str
    ) -> Optional[Dict[str, Any]]:
        """ተማሪውን VERIFY ያደርጋል፤ ሊንኩን ያስቀምጣል[cite: 1]"""
        data = {
            "status": STATUS_VERIFIED,
            "processed_by_admin_id": admin_id,
            "processed_by_admin_name": admin_name,
            "processing_lock_by": None,
            "processing_lock_until": None,
            "single_use_invite_link": invite_link
        }
        res = self.students_table.update(data).eq("telegram_id", student_id).execute()
        if res.data:
            self._log_action(student_id, "VERIFY", admin_id, admin_name, STATUS_VERIFIED, f"Link: {invite_link}")
            return res.data[0]
        return None

    def discard_student(
        self,
        student_id: int,
        admin_id: int,
        admin_name: str,
        reason: str
    ) -> Optional[Dict[str, Any]]:
        """
        ተማሪውን DISCARD ያደርጋል፤ ምክንያቱን ይይዛል፤
        ቀጣይ ለ Re-registration ምቹ እንዲሆን lock ያነሳል[cite: 1]።
        """
        student_res = self.students_table.select("discard_count").eq("telegram_id", student_id).execute()
        current_count = student_res.data[0].get("discard_count", 0) if student_res.data else 0

        data = {
            "status": STATUS_DISCARDED,
            "discard_reason": reason,
            "discard_count": current_count + 1,
            "processed_by_admin_id": admin_id,
            "processed_by_admin_name": admin_name,
            "processing_lock_by": None,
            "processing_lock_until": None
        }
        res = self.students_table.update(data).eq("telegram_id", student_id).execute()
        if res.data:
            self._log_action(student_id, "DISCARD", admin_id, admin_name, STATUS_DISCARDED, f"Reason: {reason}")
            return res.data[0]
        return None

    def _log_action(
        self,
        student_id: int,
        action: str,
        admin_id: int,
        admin_name: str,
        new_status: str,
        details: str
    ):
        """የአድሚኑን ውሳኔ በ History Log መዝግቦ ያስቀምጣል[cite: 1]"""
        try:
            self.logs_table.insert({
                "student_telegram_id": student_id,
                "action_performed": action,
                "actor_admin_id": admin_id,
                "actor_admin_name": admin_name,
                "new_status": new_status,
                "details": details
            }).execute()
        except Exception:
            pass


admin_repo = AdminRepository()