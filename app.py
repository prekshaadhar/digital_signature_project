from flask import Flask, render_template, request, redirect, url_for, send_file
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
from datetime import datetime
import mysql.connector
import os
import random

app = Flask(__name__)

# ----------------- DB -----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="#Shinchan1947",
    database="cyber_lab"
)
cursor = db.cursor(dictionary=True)

# ----------------- KEYS -----------------
key = RSA.generate(2048)
private_key = key
public_key = key.publickey()

# ----------------- GLOBAL -----------------
last_message = ""
last_signature = None
last_mode = "Assignment"

# ----------------- HOME -----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    global last_message, last_signature, last_mode

    if request.method == 'POST':
        message = request.form['message']
        mode = request.form['mode']

        last_message = message
        last_mode = mode

        h = SHA256.new(message.encode())
        message_hash = h.hexdigest()
        signature = pkcs1_15.new(private_key).sign(h)
        last_signature = signature

        cursor.execute(
            "INSERT INTO messages (message, hash, signature, mode, result) VALUES (%s,%s,%s,%s,%s)",
            (message, message_hash, base64.b64encode(signature).decode(), mode, f"SIGNED ({mode})")
        )
        db.commit()

        stats, logs = fetch_stats_logs()

        return render_template('index.html',
                               signature=base64.b64encode(signature).decode(),
                               original_hash=message_hash,
                               logs=logs,
                               stats=stats,
                               mode=mode,
                               last_action="Message Signed Securely")

    stats, logs = fetch_stats_logs()
    return render_template('index.html',
                           logs=logs,
                           stats=stats,
                           last_action="System Ready")


# ----------------- VERIFY -----------------
@app.route('/verify', methods=['POST'])
def verify():
    global last_signature, last_mode

    message = request.form.get('message', "")
    mode = request.form.get('mode', last_mode)

    h = SHA256.new(message.encode())
    new_hash = h.hexdigest()

    if not last_signature:
        result = "NO SIGNATURE ❌"
        alert = "⚠️ Sign a message first!"
        color = "red"
    else:
        try:
            pkcs1_15.new(public_key).verify(h, last_signature)
            result = "VALID ✅"
            alert = "🟢 Integrity Verified"
            color = "green"
        except:
            result = "INVALID ❌"
            alert = "🚨 ALERT: Data Tampered!"
            color = "red"

    cursor.execute(
        "INSERT INTO messages (message, hash, signature, mode, result) VALUES (%s,%s,%s,%s,%s)",
        (message, new_hash,
         base64.b64encode(last_signature).decode() if last_signature else "",
         mode, result)
    )
    db.commit()

    stats, logs = fetch_stats_logs()

    return render_template('index.html',
                           result=result,
                           alert=alert,
                           color=color,
                           logs=logs,
                           stats=stats,
                           original_hash=new_hash,
                           new_hash=new_hash,
                           mode=mode,
                           last_action="Verification Complete")


# ----------------- ATTACK -----------------
@app.route('/attack', methods=['POST'])
def attack():
    global last_message

    attack_type = request.form.get('attack_type')

    # ✅ FIX: prevent crash
    if not attack_type:
        return redirect(url_for('index'))

    if not last_message:
        tampered = "No original message!"
        explanation = "⚠️ Sign a message first"
    else:
        if attack_type == "modify":
            words = last_message.split()
            if words:
                words[random.randint(0, len(words)-1)] = "HACKED"
            tampered = " ".join(words)
            explanation = "Message modified (Integrity attack)"

        elif attack_type == "inject":
            tampered = last_message + " <script>alert('Hacked')</script>"
            explanation = "Malicious script injected (XSS attack)"

        elif attack_type == "delete":
            tampered = last_message[:len(last_message)//2]
            explanation = "Partial data deletion"

        else:
            tampered = last_message
            explanation = "Unknown attack"

        cursor.execute(
            "INSERT INTO attacks (message, attack_type, explanation, result) VALUES (%s,%s,%s,%s)",
            (tampered, attack_type, explanation, f"ATTACKED ({attack_type})")
        )
        db.commit()

    stats, logs = fetch_stats_logs()

    return render_template('index.html',
                           tampered=tampered,
                           explanation=explanation,
                           logs=logs,
                           stats=stats,
                           last_action="Attack Simulation Executed")


# ----------------- DOWNLOAD -----------------
@app.route('/download')
def download():
    report_path = os.path.join(os.getcwd(), "report.txt")

    cursor.execute("SELECT * FROM messages ORDER BY timestamp ASC")
    messages = cursor.fetchall()

    cursor.execute("SELECT * FROM attacks ORDER BY timestamp ASC")
    attacks = cursor.fetchall()

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== Messages ===\n")
        for m in messages:
            f.write(str(m) + "\n")

        f.write("\n=== Attacks ===\n")
        for a in attacks:
            f.write(str(a) + "\n")

    return send_file(report_path, as_attachment=True)


# ----------------- CLEAR LOGS -----------------
@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM attacks")
    db.commit()
    return redirect(url_for('index'))


# ----------------- STATS -----------------
def fetch_stats_logs():
    cursor.execute("SELECT COUNT(*) as signed FROM messages")
    signed = cursor.fetchone()['signed']

    cursor.execute("SELECT COUNT(*) as valid FROM messages WHERE result LIKE 'VALID%'")
    valid = cursor.fetchone()['valid']

    cursor.execute("SELECT COUNT(*) as invalid FROM messages WHERE result LIKE 'INVALID%'")
    invalid = cursor.fetchone()['invalid']

    cursor.execute("SELECT COUNT(*) as attacks FROM attacks")
    attacks_count = cursor.fetchone()['attacks']

    stats = {
        "signed": signed,
        "valid": valid,
        "invalid": invalid,
        "attacks": attacks_count
    }

    cursor.execute("SELECT *, 'Message' as log_type FROM messages")
    m_logs = cursor.fetchall()

    cursor.execute("SELECT *, 'Attack' as log_type FROM attacks")
    a_logs = cursor.fetchall()

    logs = m_logs + a_logs
    logs.sort(key=lambda x: x['timestamp'])

    for log in logs:
        log['time'] = log['timestamp'].strftime("%H:%M:%S")

    return stats, logs


# ----------------- RUN -----------------
if __name__ == '__main__':
    app.run(debug=True)