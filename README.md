# Digital Signature System

A hands-on cybersecurity project that brings digital signature verification to life using Flask, RSA cryptography, SHA-256 hashing, and MySQL. 

---

## What It Does

This system lets you sign messages, verify their integrity, and even watch what happens when an attacker tries to tamper with them. It supports three modes — Assignment, Code, and Email — so you can test it across different real-world scenarios.

**Core features include:**
- RSA digital signature generation and verification
- SHA-256 hashing for message integrity
- Simulated cyber attacks (message modification, malicious injection, data deletion)
- A live security dashboard tracking everything in real time
- SQL-based logging and downloadable security reports

---

## How It Works Under the Hood

The project is built with a straightforward stack:

- **Backend:** Python (Flask)
- **Frontend:** HTML5 + CSS3
- **Database:** MySQL
- **Cryptography:** RSA + SHA-256

---

## Attack Simulation

One of the more interesting parts of this project is the attack simulator. It demonstrates how digital signatures catch tampering by letting you simulate three types of attacks — modifying a message, injecting malicious content, or deleting data entirely. It's a great way to see cryptographic integrity verification in action rather than just in theory.

---

## Getting Started

Before running the project, import `database.sql` into MySQL, then:

```bash
pip install -r requirements.txt
python app.py
```

---

## Screenshots
See the screenshots folder for complete documentation.

---

