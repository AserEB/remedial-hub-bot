import csv
import io
from typing import Optional, Tuple
from database.connection import supabase


async def export_students_to_csv(status_filter: Optional[str] = None) -> Tuple[Optional[io.BytesIO], int]:
    """
    ከ 1,000+ በላይ ተማሪዎችን በ-Keyset Pagination አውጥቶ CSV ያዘጋጃል፤
    የተገኙትን ተማሪዎች ብዛትም አብሮ ይመልሳል
    """
    last_id = 0
    batch_size = 500
    all_students = []

    while True:
        query = (
            supabase.table("students")
            .select("telegram_id,telegram_username,full_name,stream,payment_method,status,discard_count,discard_reason,processed_by_admin_name,created_at,updated_at")
            .gt("telegram_id", last_id)
            .order("telegram_id")
        )

        if status_filter and status_filter != "ALL":
            query = query.eq("status", status_filter)

        response = query.limit(batch_size).execute()
        records = response.data

        if not records:
            break

        all_students.extend(records)
        last_id = records[-1]["telegram_id"]

    # ምንም ተማሪ ካልተገኘ
    total_count = len(all_students)
    if total_count == 0:
        return None, 0

    # CSV File በ Memory መገንባት
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Telegram ID",
        "Username",
        "Full Name",
        "Stream",
        "Payment Method",
        "Status",
        "Discard Count",
        "Discard Reason",
        "Processed By Admin",
        "Created At",
        "Updated At"
    ])

    for s in all_students:
        writer.writerow([
            s.get("telegram_id"),
            s.get("telegram_username") or "",
            s.get("full_name") or "",
            s.get("stream") or "",
            s.get("payment_method") or "",
            s.get("status") or "",
            s.get("discard_count", 0),
            s.get("discard_reason") or "",
            s.get("processed_by_admin_name") or "",
            s.get("created_at") or "",
            s.get("updated_at") or ""
        ])

    bytes_output = io.BytesIO()
    bytes_output.write(output.getvalue().encode("utf-8-sig"))
    bytes_output.seek(0)
    return bytes_output, total_count