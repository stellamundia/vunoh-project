import sqlite3

conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

# Insert 5 complete sample tasks
cursor.executescript("""
INSERT OR IGNORE INTO task 
(task_code, intent, entities, risk_score, status, created_at, employee_category, steps, whatsapp_message, email_message, sms_message) 
VALUES

('VUN-20260416-101', 'send_money', '{"amount":15000,"recipient":"Mother","location":"Kisumu","urgency":"urgent"}', 80, 'Pending', '2026-04-16 09:00:00', 'Finance', '["Verify sender ID", "Confirm recipient phone", "Initiate M-Pesa transfer", "Send receipt"]', 'Hi! Your KES 15,000 to Mum in Kisumu is being processed urgently 🚀\\nTask: VUN-20260416-101', 'Dear Customer,\\n\\nTask Code: VUN-20260416-101\\nWe are processing your urgent transfer of KES 15,000 to your mother in Kisumu.\\nStatus: Pending\\n\\nThank you,\\nVunoh Global', 'VUN-20260416-101: KES15k to Mum (Kisumu) - processing now'),

('VUN-20260416-102', 'verify_document', '{"document_type":"land title deed","location":"Karen"}', 85, 'In Progress', '2026-04-16 10:30:00', 'Legal', '["Request scanned copy", "Contact lands registry", "Physical verification", "Prepare report"]', 'Your land title in Karen is now being verified 📄\\nTask: VUN-20260416-102', 'Dear Customer,\\n\\nTask Code: VUN-20260416-102\\nWe have started verification of your land title deed in Karen.\\nTeam: Legal\\nStatus: In Progress', 'VUN-20260416-102: Land title (Karen) - verification started'),

('VUN-20260416-103', 'hire_service', '{"service_type":"cleaner","location":"Westlands","urgency":"this Friday"}', 45, 'Completed', '2026-04-16 11:45:00', 'Operations', '["Match with cleaner", "Schedule Friday 10am", "Confirm payment", "Get completion sign-off"]', 'Cleaner successfully booked for your Westlands apartment this Friday 🧹\\nTask: VUN-20260416-103', 'Dear Customer,\\n\\nTask Code: VUN-20260416-103\\nWe have hired a cleaner for your Westlands apartment on Friday.\\nStatus: Completed', 'VUN-20260416-103: Cleaner Westlands Friday - completed'),

('VUN-20260416-104', 'get_airport_transfer', '{"location":"JKIA","urgency":"tomorrow morning"}', 55, 'Pending', '2026-04-16 14:20:00', 'Operations', '["Assign driver", "Confirm pickup time", "Send vehicle details", "Live tracking"]', 'Airport transfer to JKIA tomorrow morning is confirmed 🚕\\nTask: VUN-20260416-104', 'Dear Customer,\\n\\nTask Code: VUN-20260416-104\\nYour airport transfer request has been received.\\nStatus: Pending', 'VUN-20260416-104: Airport transfer JKIA tomorrow'),

('VUN-20260416-105', 'check_status', '{"task_code":"VUN-20260416-101"}', 20, 'Pending', '2026-04-16 16:00:00', 'Customer Service', '["Lookup task", "Update status", "Notify customer"]', 'Your task VUN-20260416-101 is still Pending 👍', 'Dear Customer,\\n\\nTask Code: VUN-20260416-101\\nCurrent status: Pending\\nWe will notify you of any updates.', 'VUN-20260416-101 status: Still Pending');
""")

conn.commit()
conn.close()
