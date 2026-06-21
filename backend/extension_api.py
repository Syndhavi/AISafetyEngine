from flask import Flask, request, jsonify
from flask_cors import CORS

from src.inference_engine import process_message
from src.context_agent import ContextAgent
from src.intervention_agent import InterventionAgent

import time
import smtplib
from email.mime.text import MIMEText
from threading import Lock
import atexit

app = Flask(__name__)

# ✅ Allow extension safely
CORS(app)

# ==============================
# 🔒 GLOBAL LOCK SYSTEM
# ==============================
lock_status = {
    "locked": False,
    "type": None,
    "unlock_time": None,
    "email_sent": False
}

# ==============================
# 🔐 LLM LOCK (CRITICAL FIX)
# ==============================
llm_lock = Lock()

# ==============================
# 🤖 AGENTS (LOAD ONCE)
# ==============================
context_agent = ContextAgent()

intervention_agent = InterventionAgent(
    model_path="D:/AISafetyEngine_v2_chrome_ex/backend/models/phi-2.Q4_K_M.gguf"
)

# ==============================
# 📊 ANALYZE API (FIXED)
# ==============================
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        messages = data.get("messages", [])

        results = []
        current_time = time.time()

        # 🔥 Process ONLY LAST MESSAGE (prevents overload)
        if messages:
            messages = [messages[-1]]

        for msg in messages:

            # ==============================
            # 🔒 HANDLE LOCK STATE
            # ==============================
            if lock_status["locked"]:

                if lock_status["type"] == "BLOCK":
                    if current_time > lock_status["unlock_time"]:
                        lock_status["locked"] = False
                        lock_status["type"] = None
                        lock_status["unlock_time"] = None
                    else:
                        results.append({
                            "message": msg,
                            "action": "BLOCK"
                        })
                        continue

                elif lock_status["type"] == "ALERT":
                    results.append({
                        "message": msg,
                        "action": "ALERT_GUARDIAN"
                    })
                    continue

            # ==============================
            # 🧠 DETECTION PIPELINE
            # ==============================
            threat_score = process_message(msg)
            risk_score = context_agent.update(threat_score)

            # 🔐 CRITICAL: PROTECT LLM CALL
            with llm_lock:
                action = intervention_agent.decide(
                    message=msg,
                    threat_score=threat_score,
                    risk_score=risk_score,
                    history=messages
                )

            # ==============================
            # 🔒 UPDATE LOCK STATE
            # ==============================
            if action == "BLOCK":
                lock_status["locked"] = True
                lock_status["type"] = "BLOCK"

                # ✅ FIX: seconds, not milliseconds
                lock_status["unlock_time"] = time.time() + (2 * 60)

            if action == "ALERT_GUARDIAN":
                lock_status["locked"] = True
                lock_status["type"] = "ALERT"
                lock_status["unlock_time"] = None

            results.append({
                "message": msg,
                "threat_score": threat_score,
                "risk_score": risk_score,
                "action": action
            })

        return jsonify({"results": results})

    except Exception as e:
        print("❌ ERROR in /analyze:", e)
        return jsonify({
            "error": str(e),
            "results": []
        }), 500


# ==============================
# 📧 ALERT EMAIL API
# ==============================
@app.route('/alert', methods=['POST'])
def alert():

    data = request.json
    user_email = data.get("user_email")
    guardian_email = data.get("guardian_email")

    sender = "manjushreerajendiran@gmail.com"
    password = "ookpxawswhlhvkyt"

    unlock_link = f"http://127.0.0.1:5001/unlock?user={user_email}"

    msg = MIMEText(f"""
🚨 ALERT: Dangerous activity detected!

User: {user_email}

🔒 System is LOCKED.

👉 Click below to UNLOCK:
{unlock_link}
""")

    msg['Subject'] = "🚨 Guardian Alert - Action Required"
    msg['From'] = sender
    msg['To'] = guardian_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully")

    except Exception as e:
        print("❌ Email failed:", e)

    return jsonify({"status": "alert sent"})


# ==============================
# 🔓 UNLOCK API
# ==============================
@app.route('/unlock', methods=['GET'])
def unlock():

    user_email = request.args.get("user")

    if not lock_status["locked"]:
        return "Already unlocked"

    if user_email:
        lock_status["locked"] = False
        lock_status["type"] = None
        lock_status["unlock_time"] = None
        lock_status["email_sent"] = False

        return f"""
        <h2>✅ Chat Unlocked Successfully</h2>
        <p>User: {user_email}</p>
        """

    return "Invalid request"


# ==============================
# 📡 STATUS API (FIXED)
# ==============================
@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "locked": lock_status["locked"],
        "type": lock_status["type"]
    })


# ==============================
# 🚀 RUN SERVER
# ==============================
if __name__ == "__main__":
    app.run(port=5001, debug=True, threaded=True)


# ==============================
# 🧹 CLEANUP
# ==============================
def cleanup():
    try:
        intervention_agent.close()
    except:
        pass

atexit.register(cleanup)