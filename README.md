# Vunoh Global — AI Diaspora Assistant

An AI-powered web application that helps Kenyans living abroad initiate and track core services back home: sending money, hiring local services, verifying documents, and booking airport transfers.

Built with **Flask**, **SQLite**, **Groq (LLaMA 3.3 70B)**, and **Vanilla JavaScript** — no frontend frameworks.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Setup Instructions](#setup-instructions)
5. [How It Works](#how-it-works)
6. [Risk Scoring Logic](#risk-scoring-logic)
7. [System Prompt Design](#system-prompt-design)
8. [Database Schema](#database-schema)
9. [Decisions I Made and Why](#decisions-i-made-and-why)

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **User Input** | Plain-English text input — customers describe what they need naturally |
| 2 | **AI Intent Extraction** | LLM extracts intent and entities as structured JSON |
| 3 | **Risk Scoring** | Custom scoring logic grounded in Kenyan diaspora context |
| 4 | **Task Creation** | Every request creates a unique task record with a `VUN-` prefixed code |
| 5 | **Step Generation** | AI generates intent-specific action steps for each task |
| 6 | **Three-Format Messages** | WhatsApp, Email, and SMS confirmations — all saved to the database |
| 7 | **Employee Assignment** | Tasks are routed to Finance, Legal, Operations, or Customer Service |
| 8 | **Task Dashboard** | Full table view with live status updates (Pending / In Progress / Completed) |
| 9 | **Database Persistence** | Everything is saved — entities, steps, messages, risk scores, and status history |

---

## Tech Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Backend | Python / Flask | Matches Vunoh's internal stack; Flask is lightweight and well-suited for a focused API |
| Frontend | HTML + CSS + Vanilla JS | As specified — no frameworks |
| Database | SQLite (via Flask-SQLAlchemy) | Zero-config local persistence; schema is included for easy migration to PostgreSQL |
| AI Brain | Groq API — LLaMA 3.3 70B Versatile | Free tier, fast inference, reliable JSON output at low temperature |
| Env Config | python-dotenv | Keeps secrets out of source code |

---

## Project Structure

```
vunoh-project/
├── app.py                  # Flask app: routes, AI call, risk scoring, DB model
├── schema.sql              # Raw SQL schema (SQLite compatible)
├── dump.sql                # 5 sample tasks with complete data
├── load_samples.py         # Script to seed the database from dump.sql
├── requirements.txt        # Python dependencies
├── .env                    # API key (not committed — see setup below)
├── instance/
│   └── database.db         # SQLite database (auto-created on first run)
├── static/
│   ├── style.css           # All styling
│   └── js/
│       └── app.js          # Vanilla JS — particle background, status updates, toasts
└── templates/
    └── index.html          # Jinja2 template — input form + dashboard table
```

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repository

```bash
git https://github.com/stellamundia/vunoh-project.git
cd vunoh-project
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your environment

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the app

```bash
python app.py
```
or 
```bash
flask run
```

Open your browser at `http://127.0.0.1:5000`

### 6. (Optional) Load sample data

To pre-populate the database with the five sample tasks from `dump.sql`:

```bash
python load_samples.py
```

Or run the SQL directly against the SQLite database:

```bash
sqlite3 instance/database.db < dump.sql
```

---

## How It Works

### Request Flow

```
User types a request
       ↓
Flask /process route receives JSON body
       ↓
Task code generated (VUN-YYYYMMDD-XXX)
       ↓
Groq LLaMA 3.3 70B called with system prompt + user message + task code
       ↓
AI returns structured JSON: intent, entities, steps, messages, employee_category
       ↓
calculate_risk_score() applies rule-based scoring on top of AI output
       ↓
sync_task_code() ensures task code appears in all three messages
       ↓
validate_assignment() guards against unexpected employee category values
       ↓
Task saved to SQLite via SQLAlchemy
       ↓
Response returned to frontend — dashboard updates on next page load
```

### Supported Intents

| Intent | Triggers | Assigned Team |
|--------|----------|---------------|
| `send_money` | Amount, recipient, location | Finance |
| `verify_document` | Document type, land, ID, certificate | Legal |
| `hire_service` | Cleaner, lawyer, errand runner | Operations |
| `get_airport_transfer` | JKIA, airport, pickup | Operations |
| `check_status` | Task code lookup, status query | Customer Service |

### Message Format Examples

**WhatsApp** (conversational, line breaks, 1–2 emojis):
```
Hi! Your KES 15,000 to Mum in Kisumu is being processed urgently 🚀
Task: VUN-20260416-101
```

**Email** (formal, full details, structured):
```
Dear Customer,

Task Code: VUN-20260416-101
We are processing your urgent transfer of KES 15,000 to your mother in Kisumu.
Status: Pending

Thank you,
Vunoh Global
```

**SMS** (under 160 characters, task code and key action):
```
VUN-20260416-101: KES15k to Mum (Kisumu) - processing now
```

---

## Risk Scoring Logic

Risk scoring is calculated in Python **after** the AI responds, using rule-based logic grounded in real diaspora risk patterns. The AI is not trusted to score risk — this decision is kept deterministic and explainable.

### Scoring Rules

| Rule | Score Change | Reasoning |
|------|-------------|-----------|
| Base score | +30 | Every task starts with a baseline risk |
| Money transfer > KES 10,000 | +30 | Large transfers are more likely to be fraudulent or misdirected |
| Urgency flagged on a transfer | +20 | "Urgent" is a classic social engineering pressure tactic |
| Document type is land or title | +25 | Land fraud is the most common form of property crime in Kenya |
| No recipient identified | +15 | Unverified recipient is a major fraud signal |
| Service hire or airport transfer | +10 | Moderate risk — scheduling and vetting required |
| Returning customer (per prior task) | −2 per task | Repeat customers with a clean history are lower risk |
| Minimum score | 40 | Even known customers carry baseline operational risk |
| Maximum score | 100 | Hard ceiling |

### Score Interpretation

| Range | Interpretation |
|-------|---------------|
| 40–54 | Low risk — standard processing |
| 55–69 | Medium risk — additional verification recommended |
| 70–84 | High risk — manual review required |
| 85–100 | Critical risk — escalate immediately |

The `check_status` intent carries only the base score (40 minimum) since it is a read operation with no financial or legal consequence.

---

## System Prompt Design

The system prompt is strict and minimal by design. It does three things:

1. **Defines the output contract** — an exact JSON schema with every key named and typed. The model is told to return nothing outside the JSON. This prevents markdown wrapping, preambles, or explanatory text that would break `json.loads()`.

2. **Constrains intent to an enum** — the five intent strings are listed explicitly. Open-ended intent classification produced inconsistent labels in testing (e.g. "transfer_money" vs "send_money"), so the allowed values are hardcoded in the prompt.

3. **Enforces message distinctiveness** — the prompt specifies the tone and length requirements for each of the three message formats. Without this, the model tended to generate three near-identical confirmations at low temperature.

The task code is injected into the user-facing prompt (not the system prompt) so it can vary per request without modifying the system prompt. The model is instructed to embed the exact code in all three messages. A `sync_task_code()` helper runs afterward as a fallback in case the model omits it.

**Temperature is set to 0.3** — low enough for consistent JSON structure, but not zero, which would make the generated steps and messages repetitive across similar requests.

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS task (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    task_code         TEXT UNIQUE NOT NULL,        -- e.g. VUN-20260416-101
    intent            TEXT NOT NULL,               -- one of the five intent strings
    entities          TEXT NOT NULL,               -- JSON blob: amount, recipient, location, etc.
    risk_score        INTEGER NOT NULL,            -- calculated by Python, not the AI
    status            TEXT DEFAULT 'Pending',      -- Pending | In Progress | Completed
    created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
    employee_category TEXT NOT NULL,               -- Finance | Legal | Operations | Customer Service
    steps             TEXT NOT NULL,               -- JSON array of step strings
    whatsapp_message  TEXT NOT NULL,
    email_message     TEXT NOT NULL,
    sms_message       TEXT NOT NULL
);
```

The `entities` and `steps` columns store JSON. Flask-SQLAlchemy maps these to Python dicts/lists using its `JSON` column type. The raw schema uses `TEXT` for SQLite compatibility.

---

## Decisions I Made and Why

### AI tools used

I used **Claude** (Anthropic) as a thinking partner throughout the project — to reason through the risk scoring model, to sanity-check the system prompt design, and to review edge cases in the JSON parsing logic. I used **Groq** as the inference backend because it offers a genuinely free tier with fast response times on LLaMA 3.3 70B, which handled JSON-mode outputs reliably.

I did not use Copilot or autocomplete for the core logic files. The routes, the scoring function, and the system prompt were written by hand so I could reason through each line in an interview.

### System prompt design

The most important decision was making the system prompt output-schema-first rather than instruction-first. Earlier drafts started with "You are a helpful assistant..." and layered on instructions. The model often added explanatory text before the JSON, which broke parsing. Switching to a prompt that leads with the exact JSON structure and ends with "Never add any explanation outside the JSON" solved this almost immediately.

I excluded few-shot examples from the system prompt because the schema is explicit enough that examples added length without improving reliability. At temperature 0.3, the model follows the schema consistently.

### One decision where I overrode the AI

When I first tested the prompt, the AI was calculating a risk score inside the JSON response. The score it returned was reasonable but not explainable — it was a number with no audit trail. I removed the `risk_score` key from the JSON schema entirely and moved all scoring into `calculate_risk_score()` in Python. This means the score is deterministic, testable, and easy to explain. The AI should generate language and structure; risk decisions should be owned by code I control.

### One thing that did not work as expected

The task code consistency was a real problem. I passed the task code in the system prompt initially, but it was the same for every request (the example value I used during testing). When I moved the task code into the user-facing prompt as a variable, the model embedded it correctly about 80% of the time but missed it occasionally in the SMS message, which has a tight character budget. The `sync_task_code()` helper was added as a deterministic fallback: it checks all three messages after the AI responds and appends the task code to any message that is missing it. This is the kind of defensive layer that matters in production — you cannot rely on the model to be 100% consistent on formatting constraints.

---

## Sample Tasks

Five sample tasks are included in `dump.sql` covering all five intents. Each record contains the full extracted entities, steps, all three messages, a calculated risk score, and an employee assignment. Load them with:

```bash
sqlite3 instance/database.db < dump.sql
```

---

## Deployment (Optional)

The app can be deployed to [Railway](https://railway.app) or [Render](https://render.com) with minimal configuration. Both platforms detect Flask apps automatically. Set the `GROQ_API_KEY` environment variable in the platform's dashboard. For production, replace the SQLite URI with a PostgreSQL connection string — the SQLAlchemy model requires no changes.

---

*Vunoh Global — AI Internship 2026*