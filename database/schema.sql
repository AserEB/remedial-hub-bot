-- =====================================================================
-- REMEDIAL HUB TELEGRAM BOT: CORE DATABASE SCHEMA
-- Target Engine: PostgreSQL 15+ (Supabase)
-- =====================================================================

-- 1. Create Enums for strict validation
DO $$ BEGIN
    CREATE TYPE student_stream AS ENUM ('NATURAL', 'SOCIAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE registration_status AS ENUM ('STARTED', 'PENDING', 'VERIFIED', 'DISCARDED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_channel AS ENUM ('CBE', 'ABYSSINIA');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. System Settings & Configuration Table
CREATE TABLE IF NOT EXISTS public.system_settings (
    id SMALLINT PRIMARY KEY DEFAULT 1,
    is_registration_active BOOLEAN NOT NULL DEFAULT TRUE,
    pinned_notice_text VARCHAR(85) DEFAULT NULL,
    pinned_notice_active BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW()),
    updated_by BIGINT DEFAULT NULL,
    CONSTRAINT single_row_check CHECK (id = 1)
);

-- Initialize default system settings
INSERT INTO public.system_settings (id, is_registration_active, pinned_notice_text, pinned_notice_active)
VALUES (1, TRUE, 'እንኳን ወደ Remedial Hub በደህና መጡ! ምዝገባ ክፍት ነው!', TRUE)
ON CONFLICT (id) DO NOTHING;

-- 3. Students Registration Table
CREATE TABLE IF NOT EXISTS public.students (
    telegram_id BIGINT PRIMARY KEY,
    telegram_username VARCHAR(255),
    full_name VARCHAR(255),
    stream student_stream,
    payment_method payment_channel,
    payment_screenshot_file_id TEXT,
    payment_screenshot_url TEXT,
    status registration_status NOT NULL DEFAULT 'STARTED',
    discard_count INT NOT NULL DEFAULT 0,
    discard_reason TEXT,
    processed_by_admin_id BIGINT,
    processed_by_admin_name VARCHAR(255),
    processing_lock_by BIGINT DEFAULT NULL,
    processing_lock_until TIMESTAMPTZ DEFAULT NULL,
    single_use_invite_link TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 4. Registration Audit & History Log Table
CREATE TABLE IF NOT EXISTS public.registration_logs (
    log_id BIGSERIAL PRIMARY KEY,
    student_telegram_id BIGINT NOT NULL REFERENCES public.students(telegram_id) ON DELETE CASCADE,
    action_performed VARCHAR(50) NOT NULL,
    actor_admin_id BIGINT,
    actor_admin_name VARCHAR(255),
    previous_status registration_status,
    new_status registration_status,
    details TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT TIMEZONE('utc', NOW())
);

-- 5. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_students_status ON public.students(status);
CREATE INDEX IF NOT EXISTS idx_students_cursor_pagination ON public.students(status, telegram_id);
CREATE INDEX IF NOT EXISTS idx_students_processing_lock ON public.students(processing_lock_by, processing_lock_until);

-- 6. Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc', NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_students_modtime ON public.students;
CREATE TRIGGER update_students_modtime
BEFORE UPDATE ON public.students
FOR EACH ROW
EXECUTE FUNCTION update_timestamp_column();

DROP TRIGGER IF EXISTS update_settings_modtime ON public.system_settings;
CREATE TRIGGER update_settings_modtime
BEFORE UPDATE ON public.system_settings
FOR EACH ROW
EXECUTE FUNCTION update_timestamp_column();