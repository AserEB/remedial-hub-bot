from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from database.connection import supabase
from config.constants import (
    STATUS_VERIFIED,
    STATUS_DISCARDED,
    STATUS_PENDING,
    STREAM_NATURAL,
    STREAM_SOCIAL,
    BANK_CBE,
    BANK_ABYSSINIA,
    BANK_TELEBIRR
)


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
        አንድ አድሚን ውሳኔ መስጠት ሲጀምር ለ 120 ሰከንድ lock ያደርጋል።
        ሌላ አድሚን ቢሞክር Alert ያሳያል።
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
        """ተማሪውን VERIFY ያደርጋል፤ ሊንኩን ያስቀምጣል"""
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
        ቀጣይ ለ Re-registration ምቹ እንዲሆን lock ያነሳል።
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

    def get_quick_status_counts(self) -> Dict[str, int]:
        """ዳታቤዝ ላይ ያሉትን ተማሪዎች በሙሉ በየዘርፉ ቆጥሮ ፈጣን ስታቲስቲክስ ያመጣል"""
        counts = {
            "total_users": 0,
            "pending": 0,
            "verified": 0,
            "discarded": 0,
            "cbe": 0,
            "abyssinia": 0,
            "telebirr": 0,
            "natural": 0,
            "social": 0
        }
        try:
            res = self.students_table.select("status, stream, payment_method").limit(10000).execute()
            if res.data:
                counts["total_users"] = len(res.data)
                for row in res.data:
                    status = row.get("status")
                    stream = row.get("stream")
                    bank = row.get("payment_method")

                    if status == STATUS_PENDING:
                        counts["pending"] += 1
                    elif status == STATUS_VERIFIED:
                        counts["verified"] += 1
                        # Stream የሚቆጠረው VERIFIED ለሆኑት ብቻ ነው
                        if stream == STREAM_NATURAL:
                            counts["natural"] += 1
                        elif stream == STREAM_SOCIAL:
                            counts["social"] += 1
                    elif status == STATUS_DISCARDED:
                        counts["discarded"] += 1

                    if bank == BANK_CBE:
                        counts["cbe"] += 1
                    elif bank == BANK_ABYSSINIA:
                        counts["abyssinia"] += 1
                    elif bank == BANK_TELEBIRR:
                        counts["telebirr"] += 1

        except Exception:
            pass

        return counts

    def get_weekly_status_counts(self) -> Dict[str, int]:
        """
        ከእሑድ ምሽት 3:00 EAT (18:00 UTC) ጀምሮ ያለውን ሳምንታዊ ሪፖርት ያሰላል።
        በሳምንቱ ውስጥ Verify እና Discard የተደረጉትን ከተማሪዎች እና ከሎግ በትክክል ያመጣል።
        """
        counts = {
            "weekly_total": 0,
            "weekly_pending": 0,
            "weekly_verified": 0,
            "weekly_discarded": 0,
            "weekly_natural": 0,
            "weekly_social": 0
        }

        # የኢትዮጵያ እሑድ ምሽት 3:00 EAT = 18:00 UTC
        now_utc = datetime.now(timezone.utc)
        
        # ዛሬ እሑድ ከሆነ weekday() = 6 ነው
        days_since_sunday = (now_utc.weekday() - 6) % 7
        target_sunday = (now_utc - timedelta(days=days_since_sunday)).replace(
            hour=18, minute=0, second=0, microsecond=0
        )

        # ዛሬ እሑድ ሆኖ ሰዓቱ ገና ከ 18:00 UTC (ምሽት 3:00 EAT) በታች ከሆነ ካለፈው ሳምንት እሑድ 18:00 ይጀምራል
        if now_utc < target_sunday:
            target_sunday -= timedelta(days=7)

        target_iso = target_sunday.isoformat()

        try:
            # 1. በዚህ ሳምንት የገቡ ተማሪዎች (/start ያሉ ወይም የተመዘገቡ)
            res_new = self.students_table.select("telegram_id, status, stream, created_at").gte("created_at", target_iso).limit(10000).execute()
            weekly_students = res_new.data or []
            counts["weekly_total"] = len(weekly_students)

            # 2. በዚህ ሳምንት Pending የሆኑ
            for row in weekly_students:
                if row.get("status") == STATUS_PENDING:
                    counts["weekly_pending"] += 1

            # 3. በዚህ ሳምንት Verify እና Discard የተደረጉትን ከ Registration Logs መውሰድ (የቀደሙትንም ጨምሮ እንዳያመልጥ)
            logs_res = self.logs_table.select("student_telegram_id, action_performed, created_at").gte("created_at", target_iso).limit(10000).execute()
            
            weekly_verified_ids = set()
            weekly_discarded_ids = set()

            if logs_res.data:
                for log in logs_res.data:
                    action = log.get("action_performed")
                    s_id = log.get("student_telegram_id")
                    if action == "VERIFY":
                        weekly_verified_ids.add(s_id)
                    elif action == "DISCARD":
                        weekly_discarded_ids.add(s_id)

            # በሳምንቱ ውስጥ ገብተው የተረጋገጡትንም ማካተት
            for row in weekly_students:
                s_id = row.get("telegram_id")
                if row.get("status") == STATUS_VERIFIED:
                    weekly_verified_ids.add(s_id)
                elif row.get("status") == STATUS_DISCARDED:
                    weekly_discarded_ids.add(s_id)

            counts["weekly_verified"] = len(weekly_verified_ids)
            counts["weekly_discarded"] = len(weekly_discarded_ids)

            # 4. በሳምንቱ የጸደቁትን Stream (Natural vs Social) መለየት
            if weekly_verified_ids:
                # በዳታቤዝ ውስጥ የእነዚህን ተማሪዎች Stream ማረጋገጥ
                v_res = self.students_table.select("stream").in_("telegram_id", list(weekly_verified_ids)).execute()
                if v_res.data:
                    for v_row in v_res.data:
                        st = v_row.get("stream")
                        if st == STREAM_NATURAL:
                            counts["weekly_natural"] += 1
                        elif st == STREAM_SOCIAL:
                            counts["weekly_social"] += 1

        except Exception:
            pass

        return counts

    def _log_action(
        self,
        student_id: int,
        action: str,
        admin_id: int,
        admin_name: str,
        new_status: str,
        details: str
    ):
        """የአድሚኑን ውሳኔ በ History Log መዝግቦ ያስቀምጣል"""
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