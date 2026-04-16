-- Schema for Vunoh Global AI Assistant
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_code TEXT UNIQUE NOT NULL,
    intent TEXT NOT NULL,
    entities TEXT NOT NULL,
    risk_score INTEGER NOT NULL,
    status TEXT DEFAULT 'Pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    employee_category TEXT NOT NULL,
    steps TEXT NOT NULL,
    whatsapp_message TEXT NOT NULL,
    email_message TEXT NOT NULL,
    sms_message TEXT NOT NULL
);