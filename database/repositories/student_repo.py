from typing import Optional, Dict, Any
from database.connection import supabase
from config.constants import STATUS_STARTED, STATUS_PENDING


class StudentRepository:
    def __init__(self):
        self.table = supabase.table("students")

    def get_student(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """የአንድን ተማሪ ዳታ በ Telegram ID ይፈልጋል"""
        response = self.table.select("*").eq("telegram_id", telegram_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    def get_or_create_student(self, telegram_id: int, username: Optional[str] = None) -> Dict[str, Any]:
        """ተማሪው ከሌለ በአዲስ መልክ START ያደርጋል፣ ካለ ያለውን ዳታ ይመልሳል"""
        student = self.get_student(telegram_id)
        if not student:
            new_data = {
                "telegram_id": telegram_id,
                "telegram_username": username,
                "status": STATUS_STARTED
            }
            res = self.table.insert(new_data).execute()
            return res.data[0]
        return student

    def update_student_data(self, telegram_id: int, update_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """የተማሪውን የተወሰነ መረጃ Update ያደርጋል"""
        res = self.table.update(update_dict).eq("telegram_id", telegram_id).execute()
        return res.data[0] if res.data else None

    def submit_for_verification(
        self,
        telegram_id: int,
        full_name: str,
        stream: str,
        payment_method: str,
        file_id: str
    ) -> Optional[Dict[str, Any]]:
        """ምዝገባው ተጠናቆ ደረሰኝ ሲላክ ወደ PENDING የሚቀይር (ሪከርድ ከሌለም አዲስ የሚፈጥር)"""
        data = {
            "telegram_id": telegram_id,  # Upsert እንዲሰራ የ Primary Key መኖር ግዴታ ነው
            "full_name": full_name,
            "stream": stream,
            "payment_method": payment_method,
            "payment_screenshot_file_id": file_id,
            "status": STATUS_PENDING,
            "processing_lock_by": None,
            "processing_lock_until": None
        }
        # UPDATE ከማድረግ ይልቅ UPSERT እንጠቀማለን (ካለ ያዘምናል፣ ከሌለ 100% አዲስ ይፈጥራል)
        res = self.table.upsert(data).execute()
        return res.data[0] if res.data else None


student_repo = StudentRepository()