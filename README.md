Remedial Hub Telegram Bot
Remedial Hub Automated Student Enrollment & Verification System
A production-oriented Telegram bot designed for Remedial Hub to
automate student registration, payment-receipt submission, administrator
verification, and controlled access to the appropriate learning group.

Blueprint Version: 1.0
Architecture: Async Telegram Bot + Supabase PostgreSQL + Render +
GitHub

📌 Project Overview
The system automates the complete student enrollment workflow:

Student starts the bot with /start.

The bot verifies membership in the required public Telegram channel.

The student opens the registration flow.

The student enters their full name.

The student selects an academic stream:

Natural Science

Social Science

The student selects a payment bank:

CBE

Abyssinia Bank

The student submits a payment receipt as an image or PDF.

The registration is saved as PENDING.

The receipt and student information are sent to the configured
administrators.

An administrator verifies or discards the registration.

After verification, the bot generates a single-use Telegram invite
link for the student's selected stream.

The student joins the correct learning group.

The system also supports re-registration after a discarded application,
multi-admin concurrency protection, CSV exports, broadcasts, and a
global pinned announcement.

🏗️ Technology Stack
Layer Technology

Language Python 3.12+ / Python 3.14 compatible
Telegram Framework python-telegram-bot v21.x+
Database Supabase / PostgreSQL 15+
Database Client supabase-py / postgrest-py
Hosting Render
Version Control Git + GitHub
Local Development VS Code

The bot is designed around an asynchronous runtime and production-grade
Telegram bot framework.

📂 Project Structure
Remedial_Hub_Bot/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── Procfile
├── runtime.txt
├── README.md
│
├── assets/
│   ├── media/
│   │   └── How-to-register.mp4
│   └── templates/
│       └── export_template.csv
│
├── config/
│   ├── __init__.py
│   ├── constants.py
│   └── settings.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── schema.sql
│   └── repositories/
│       ├── __init__.py
│       ├── student_repo.py
│       ├── admin_repo.py
│       └── config_repo.py
│
├── handlers/
│   ├── __init__.py
│   ├── common_handlers.py
│   ├── navigation_handlers.py
│   ├── registration_handlers.py
│   ├── status_handlers.py
│   └── admin_handlers.py
│
├── keyboards/
│   ├── __init__.py
│   ├── user_keyboards.py
│   └── admin_keyboards.py
│
├── services/
│   ├── __init__.py
│   ├── invite_service.py
│   ├── export_service.py
│   ├── broadcast_service.py
│   └── channel_service.py
│
└── main.py
🧩 Main Components
config/
Contains static configuration and environment-variable loading.

constants.py --- static text, Telegram group IDs, bank
information, and admin configuration.

settings.py --- environment configuration loader.

database/
Supabase/PostgreSQL data-access layer.

connection.py --- Supabase client.

schema.sql --- PostgreSQL database schema.

student_repo.py --- student creation, status updates, and checks.

admin_repo.py --- administrator actions, locks, and auditing.

config_repo.py --- global settings and pinned announcement.

handlers/
Telegram update-handling logic.

common_handlers.py --- /start, /cancel, and
channel-subscription checks.

navigation_handlers.py --- About Us, Testimonials, FAQ, How-to,
and Contact.

registration_handlers.py --- multi-step registration FSM.

status_handlers.py --- /status, tracking, and re-registration.

admin_handlers.py --- admin dashboard, verification, discard,
broadcast, and pin controls.

keyboards/
Reusable Telegram inline keyboards.

user_keyboards.py

admin_keyboards.py

services/
Business-logic layer.

invite_service.py --- single-use invite-link generation.

export_service.py --- cursor/keyset CSV export.

broadcast_service.py --- batch broadcasting and flood-wait
protection.

channel_service.py --- Telegram membership verification.

🗄️ Database Architecture
The project uses Supabase PostgreSQL.

Enums
Student Stream
CREATE TYPE student_stream AS ENUM ('NATURAL', 'SOCIAL');
Registration Status
STARTED
PENDING
VERIFIED
DISCARDED
Payment Channel
CBE
ABYSSINIA
Main Tables
system_settings
Stores global system configuration.

Important fields:

is_registration_active

pinned_notice_text

pinned_notice_active

updated_at

updated_by

The table is designed as a single-row configuration table.

students
Stores student registration data.

Important fields include:

telegram_id

telegram_username

full_name

stream

payment_method

payment_screenshot_file_id

payment_screenshot_url

status

discard_count

discard_reason

processed_by_admin_id

processed_by_admin_name

processing_lock_by

processing_lock_until

single_use_invite_link

created_at

updated_at

registration_logs
Provides an audit/history trail.

It records:

action performed

administrator

previous status

new status

details

timestamp

🔄 Registration Flow
/start
   │
   ▼
Check Telegram Channel Membership
   │
   ├── Not a member ──► Join Channel ──► Verify
   │
   └── Member
          │
          ▼
      Main Menu
          │
          ▼
    Register Now
          │
          ▼
      Full Name
          │
          ▼
   Select Stream
   ┌──────┴──────┐
   ▼             ▼
Natural        Social
   │             │
   └──────┬──────┘
          ▼
     Select Bank
   ┌──────┴────────┐
   ▼               ▼
  CBE           Abyssinia
   │               │
   └──────┬────────┘
          ▼
   Submit Receipt
    Image / PDF
          │
          ▼
       PENDING
          │
          ▼
   Admin Verification
      ┌───┴───┐
      ▼       ▼
   Verify   Discard
      │       │
      ▼       ▼
Invite Link  Reason
      │
      ▼
Learning Group
👨‍🎓 User Interface
After successful channel verification, the main menu contains:

ℹ️ About Us
🎓 Testimonials
❓ FAQs
📝 How to Register
🚀 Register Now
📊 My Status
📞 Contact Us
About Us
The blueprint describes Remedial Hub as an educational center
established to support remedial students with preparation, course
materials, and educational support.

Testimonials
Students can access the official testimonials channel and view previous
student experiences.

FAQ
The FAQ system uses an accordion-style inline-keyboard flow.

Configured questions include:

How is the education delivered?

How do I follow the course?

How can I access missed lessons?

Is the payment monthly or one-time?

How much is the registration fee?

How to Register
The bot sends:

assets/media/How-to-register.mp4
The registration guide covers:

Press Start.

Press Register Now.

Enter full name.

Select stream.

Select bank.

Send payment receipt.

Wait for admin approval.

Receive the private learning-group link.

Join and pin the group.

🧠 Registration FSM
The registration process is implemented as a finite-state flow.

IDLE
  ↓
WAITING_FULL_NAME
  ↓
SELECTING_STREAM
  ↓
SELECTING_BANK
  ↓
AWAITING_RECEIPT
  ↓
PENDING_VERIFICATION
The user can go back and edit earlier choices where supported.

💳 Payment Receipt Verification
The blueprint specifies a registration fee of 500 ETB.

Supported payment channels:

CBE

Abyssinia Bank

The bot displays the configured payment information and provides a
receipt-submission action.

Accepted receipt formats:

Image

PDF

After submission, the student receives a pending/review confirmation.

👮 Multi-Admin Verification
The system supports four administrators.

When a student submits a receipt:

Student
   ↓
Receipt
   ↓
All configured Admins
   ↓
Verify / Discard
The system uses a 120-second processing lock to prevent two
administrators from processing the same student simultaneously.

Example:

Admin A → Discard
Admin B → Verify at same time

Admin A acquires lock
        ↓
Admin B is rejected
        ↓
Admin A completes decision
        ↓
Lock cleared
        ↓
Other admin messages updated
This protects against conflicting verification decisions.

🔁 Discard & Re-Registration
If an administrator discards a registration:

The student receives the discard reason.

The student can choose Re-Register.

The previous stream is cleared.

The previous payment_method is cleared.

The previous receipt file ID is cleared.

discard_count is increased by 1.

The student starts the registration process again.

The student must select the stream again.

This specifically prevents an old/wrong stream selection from being
reused during re-registration.

🔐 Single-Use Invite Links
After successful verification, the bot determines the student's selected
stream and generates an invite link for the corresponding learning
group.

The blueprint specifies:

chat_id = NATURAL_GROUP_ID if stream == "NATURAL" else SOCIAL_GROUP_ID

invite_link_obj = await bot.create_chat_invite_link(
    chat_id=chat_id,
    name=f"Student_{student_id}",
    member_limit=1
)
The important security property is:

member_limit = 1
Therefore, the generated invite link is intended for one student only.

The student is instructed not to share the link and to pin the group
after joining.

📊 Student Status
The bot provides a self-service status system.

Possible registration states:

STARTED
PENDING
VERIFIED
DISCARDED
For discarded registrations, the status can also expose the discard
count and reason.

🛠️ Admin Dashboard
Administrators access the dashboard through:

/admin
The dashboard includes:

Registration: ACTIVE / OFF

📥 Verified Students (CSV)
❌ Discarded Students (CSV)
👥 All Users (CSV)
📢 Broadcast
📌 Post Announcement
The dashboard also displays the active registration state and pinned
announcement.

📤 CSV Export
The exporter uses keyset/cursor pagination instead of large OFFSET
queries.

Default batch size:

500 records
Conceptually:

last_id = 0

while records exist:
    fetch records where telegram_id > last_id
    process batch
    last_id = last record telegram_id
This is designed to support exports for large student datasets,
including 1,000+ students.

Available export categories include:

Verified

Discarded

All users

📢 Broadcast System
Administrators can broadcast:

Text

Photos

Videos

Documents

Before broadcasting, the bot asks for confirmation:

This message will be sent to all registered users.
Are you sure?
Actions:

✅ Send Now
❌ Cancel
The blueprint also specifies a small delay between messages to reduce
Telegram flood-wait risk.

📌 Global Pinned Announcement
Administrators can publish a global announcement.

Rules:

Maximum length: 85 characters

Stored in system_settings

Can be activated/deactivated

Displayed above the main menu

Flow:

Admin creates announcement
        ↓
Validate ≤ 85 characters
        ↓
Save to system_settings
        ↓
Show above main menu
🔧 Environment Configuration
Create a local .env file.

Never commit .env to GitHub.

Example:

# Telegram
BOT_TOKEN=your_telegram_bot_token

# Required channel
REQUIRED_CHANNEL_USERNAME=@Remedial_Hub
REQUIRED_CHANNEL_ID=your_channel_id

# Learning groups
NATURAL_GROUP_ID=your_natural_group_id
SOCIAL_GROUP_ID=your_social_group_id

# Admins
ADMIN_IDS=admin_id_1,admin_id_2,admin_id_3,admin_id_4
ADMIN_CONTACT_USERNAME=Remedial_Admin

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key

# Payment
CBE_ACCOUNT_NUMBER=your_cbe_account
CBE_ACCOUNT_NAME=your_account_name
ABYSSINIA_ACCOUNT_NUMBER=your_abyssinia_account
ABYSSINIA_ACCOUNT_NAME=your_account_name

# Registration
REGISTRATION_FEE_ETB=500
⚠️ Security
The original blueprint contains credentials and account information.
Do not copy those secrets into this README or commit them to GitHub.

If a real Telegram bot token or Supabase secret key has ever been
exposed publicly, rotate/revoke the affected credential before
production deployment.

📦 Installation
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Remedial_Hub_Bot
2. Create a virtual environment
Windows:

python -m venv .venv
Activate:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure environment variables
Create:

.env
using:

.env.example
as the template.

5. Configure Supabase
Create the required PostgreSQL schema using:

database/schema.sql
Then configure:

SUPABASE_URL=...
SUPABASE_KEY=...
6. Configure Telegram
Set:

Bot token

Required channel

Natural group

Social group

Admin IDs

The bot must have the required Telegram permissions to check membership
and generate invite links.

7. Run locally
python main.py
🚀 Render Deployment
The blueprint specifies Render as the hosting platform.

Deployment architecture:

GitHub
   ↓
Render
   ↓
Python Telegram Bot
   ↓
Supabase PostgreSQL
Recommended deployment configuration:

Connect the GitHub repository to Render.

Configure environment variables in Render.

Do not upload .env.

Use the project's Procfile and runtime.txt as deployment
configuration.

Deploy as the appropriate Render service/background worker according
to the bot runtime configuration.

🧪 Recommended Pre-Production Tests
Before going live, test:

Registration
/start

Channel membership check

Register Now

Full name

Natural selection

Social selection

CBE selection

Abyssinia selection

Image receipt

PDF receipt

Pending state

Editing
Edit name

Edit stream

Edit bank

Cancel registration

Admin
Verify

Discard

Discard reason

Concurrent Verify/Discard

120-second lock

Admin message updates

Re-Registration
Previous stream cleared

Previous bank cleared

Previous receipt cleared

discard_count incremented

Fresh stream selection

Invite Links
Natural → Natural group

Social → Social group

Member limit = 1

Student receives the correct invite link

Dashboard
Registration ON/OFF

Verified CSV

Discarded CSV

All users CSV

Broadcast confirmation

Announcement

85-character validation

🔒 Security Checklist
Before production:


.env is in .gitignore


No bot token is committed


No Supabase secret key is committed


Database credentials are stored as environment variables


Admin IDs are configured correctly


Bot has required Telegram permissions


Learning groups are configured correctly


Single-use invite links are enabled


Admin concurrency locking is tested


Receipt handling is tested for image and PDF


Broadcast confirmation is tested


Registration ON/OFF is tested


Database audit logs are working

📝 Project Status Model
STARTED
   │
   ▼
PENDING
   │
   ├──────────────► VERIFIED
   │
   └──────────────► DISCARDED
                         │
                         ▼
                     RE-REGISTER
                         │
                         ▼
                     STARTED
📚 Source Blueprint
This README is based on the Remedial Hub Telegram Bot --- System
Blueprint, Standard Version 1.0, which defines the architecture, data
models, registration workflow, admin workflow, services, deployment
structure, and operational rules.

Source document: REMEDIAL HUB TELEGRAM BOT BLUPRINT.pdf

Remedial Hub
Remedial Hub --- ከእኛ ጋር ይታለፋል!

Aser Production -- Visual Creative Solutions!
