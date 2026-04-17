import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
import os   # ← make sure this is at the top with other imports

# Use absolute path (fixes Windows Git Bash issue)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath('instance/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ====================== DATABASE MODEL ======================
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_code = db.Column(db.String(20), unique=True, nullable=False)
    intent = db.Column(db.String(50), nullable=False)
    entities = db.Column(db.JSON, nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee_category = db.Column(db.String(50), nullable=False)
    steps = db.Column(db.JSON, nullable=False)
    whatsapp_message = db.Column(db.Text, nullable=False)
    email_message = db.Column(db.Text, nullable=False)
    sms_message = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

# ====================== SYSTEM PROMPT ======================
SYSTEM_PROMPT = """
You are Vunoh AI Assistant for Kenyan diaspora customers.
Return ONLY valid JSON with these exact keys. No extra text.

{
  "intent": "send_money" | "get_airport_transfer" | "hire_service" | "verify_document" | "check_status",
  "entities": {
    "amount": number or null,
    "recipient": string or null,
    "location": string or null,
    "urgency": string or null,
    "document_type": string or null,
    "service_type": string or null,
    "task_code": string or null
  },
  "steps": ["step 1", "step 2", ...],
  "messages": {
    "whatsapp": "conversational text with \\n and maybe 1-2 emojis",
    "email": "formal, structured email with full details and task code",
    "sms": "under 160 characters, only key info + task code"
  },
  "employee_category": "Finance" | "Operations" | "Legal" | "Customer Service"
}

Rules:
- Intent must be exactly one of the five strings.
- Messages must be different in tone and length.
- Never add any explanation outside the JSON.
"""

# ====================== RISK SCORING ======================
def calculate_risk_score(intent, entities):
    score = 30
    if intent == "send_money":
        amount = float(entities.get("amount") or 0)
        if amount > 10000:
            score += 30
        if entities.get("urgency") and "urgent" in str(entities["urgency"]).lower():
            score += 20
    if intent == "verify_document":
        doc = str(entities.get("document_type") or "").lower()
        if "land" in doc or "title" in doc:
            score += 25
    if not entities.get("recipient"):
        score += 15
    if intent in ["get_airport_transfer", "hire_service"]:
        score += 10
    return min(max(score, 0), 100)

# ====================== GROQ CLIENT ======================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(user_message):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # Best performing model on Groq right now
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=1200
    )
    return json.loads(response.choices[0].message.content)

# ====================== HELPER ======================
def generate_task_code():
    return f"VUN-{datetime.now().strftime('%Y%m%d')}-{random.randint(100,999)}"

# ====================== ROUTES ======================
@app.route('/')
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/process', methods=['POST'])
def process():
    user_message = request.json['message']
    
    # Call Groq
    ai_json = call_groq(user_message)   # your existing function
    
    task_code = generate_task_code()
    risk = calculate_risk_score(ai_json["intent"], ai_json["entities"])
    
    # ←←← THIS IS THE IMPORTANT PART
    employee_category = ai_json.get("employee_category", "Support Team")
    
    new_task = Task(
        task_code=task_code,
        intent=ai_json["intent"],
        entities=ai_json["entities"],
        risk_score=risk,
        employee_category=employee_category,        # ← Make sure this line exists
        steps=ai_json["steps"],
        whatsapp_message=ai_json["messages"]["whatsapp"],
        email_message=ai_json["messages"]["email"],
        sms_message=ai_json["messages"]["sms"]
    )
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify({"task": {
        "task_code": task_code,
        "intent": ai_json["intent"],
        "risk_score": risk,
        "employee_category": employee_category,     # ← Send it to frontend
        "status": "Pending",
        "messages": ai_json["messages"]
    }})

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    task = Task.query.filter_by(task_code=data['task_code']).first()
    if task:
        task.status = data['status']
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 404



if __name__ == '__main__':
    app.run(debug=True)