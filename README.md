# 🔐 Password Attack Simulation System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Security](https://img.shields.io/badge/Security-Advanced-success?style=for-the-badge&logo=security)
![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)

A modern, comprehensive web application designed to evaluate and analyze password strength against advanced attack vectors. This system simulates a variety of cracking methodologies for educational and auditing purposes without storing user passwords, providing deeply insightful metrics such as entropy calculation, crack time estimation, and actionable security suggestions.

---

## ✨ Features

- **🚀 Real-time Analysis:** Instant evaluation of passwords via a debounced backend API.
- **📊 Precise Entropy Calculation:** Uses mathematically robust formulas to gauge true cryptographic strength.
- **⏱️ Crack Time Estimation:** Calculates comprehensive cracking attempt times ranging from seconds to centuries.
- **🛡️ Advanced Threat Detection:** Evaluates inputs against many sophisticated and common attack models.
- **💡 Smart Suggestions:** Context-aware recommendations for actionable user security improvement.
- **🎨 Sleek Cyberpunk UI:** A responsive, terminal-inspired frontend design built natively without heavy frameworks.

---

## 🎯 Simulated Attack Types

The system actively evaluates passwords against the following sophisticated metrics:
- 📖 **Dictionary Attack:** Checks against a predefined list of vulnerable words.
- 🧬 **Hybrid Attack:** Identifies dictionary words fused with numeric/symbol endings or prefixes.
- ⌨️ **Keyboard Pattern:** Spots sequential keystrokes (e.g., `qwerty`, `asdf`).
- 🔢 **Sequential Pattern:** Detects ascending/descending chains (e.g., `1234`, `abcd`).
- ⏪ **Reverse Sequence:** Catches backwards typing algorithms (e.g., `9876`).
- 🔄 **Repeated Characters:** Identifies duplicate string sequences.
- 1️⃣3️⃣3️⃣7️⃣ **Leetspeak Vulnerability:** Normalizes and detects `$ecr3t` dictionary substitutions.
- 📅 **Date-Based Pattern:** Flags common birthday or calendar year formats (YYYYMMDD / DDMMYYYY).
- 🧱 **Repeated Block Pattern:** Assesses structural block loops (e.g., `abcabc`).

---

## 📸 Screenshots

*(Replace this section with actual images of your application once deployed)*

| Cybersecurity Dashboard | Analysis Metrics Grid |
| ----------------------- | ------------- |
| ![Dashboard Placeholder](https://via.placeholder.com/400x250.png?text=Dashboard+UI) | ![Grid Placeholder](https://via.placeholder.com/400x250.png?text=Metrics+Grid) |

---

## ⚙️ Installation & Usage

1. **Clone the repository:**
   ```bash
   'git clone https://github.com/sri-saraneswar/password-str.git'
   'cd password-str'

   ```

2. **Install requirements:**
   ```bash
   pip install flask flask-cors flask-limiter
   ```
   *(Or alternatively via `pip install -r requirements.txt`)*

3. **Populate Dictionary Details (Optional but Recommended):**
   Create or edit the `weak_passwords.txt` file in the root directory:
   ```bash
   touch weak_passwords.txt
   # Add common weak passwords like 'password', 'admin', 'qwerty', etc.
   ```

4. **Launch the API Server:**
   ```bash
   python app.py
   ```
   *The Flask backend will start on port `5001`.*

5. **Start Frontend:**
   Simply double-click or open `index.html` in your favorite modern web browser!

---

## 📡 API Documentation

### **Endpoint:** `POST /analyze`
**Rate Limit:** 30 requests per minute (per IP)

**Example Request:**
```json
{
  "password": "hunter2password"
}
```

**Example Response:**
```json
{
  "attack_summary": {
    "date_based": false,
    "dictionary": true,
    "hybrid": false,
    "keyboard": false,
    "leetspeak": false,
    "repeated": false,
    "repeated_block": false,
    "reverse": false,
    "sequential": false
  },
  "character_set_size": 26,
  "dictionary_attack_result": true,
  "entropy_bits": 70.51,
  "estimated_crack_time_readable": "1 years",
  "estimated_crack_time_seconds": 64610818.89,
  "password_length": 15,
  "pattern_warning": false,
  "score": 45,
  "strength_level": "Moderate",
  "suggestions": [
    "Avoid using common dictionary words."
  ],
  "total_combinations": 6.46e+20,
  "vulnerability_types": [
    "Dictionary Attack Vulnerability"
  ]
}
```

### Response Field Guide:
| Field | Type | Description |
|-------|------|-------------|
| `score` | Integer | Calculated overall security rating (0-100). |
| `strength_level` | String | Classification text (`Weak`, `Moderate`, `Strong`, `Very Strong`). |
| `entropy_bits` | Float | Calculated cryptographic bit strength of the exact input. |
| `estimated_crack_time_readable` | String | Duration mapped to human formats (e.g., `Centuries`, `2 hours`). |
| `suggestions` | Array | Contextual list of user-facing password improvements. |
| `vulnerability_types` | Array | Human-readable string components of triggered attack vulnerabilities. |
| `attack_summary` | Object | Detailed boolean map indicating exactly which simulated attacks succeeded. |
| `pattern_warning` | Boolean | True if generic systemic patterns were widely noted. |

---

## 🛠️ Tech Stack

**Backend System:**
- Python 3.x
- Flask
- Flask-CORS
- Flask-Limiter

**Client System:**
- Vanilla HTML5
- Native CSS3 / CSS Variables 
- Vanilla JavaScript (ES6+ / Fetch API)

---

## 🚀 Future Improvements

- [ ] Connect database checking securely against expansive dictionaries (like HaveIBeenPwned API parameters).
- [ ] Incorporate comprehensive machine-learning models for localized typo-tolerance detection on standard languages.
- [ ] Expand localization and i18n support.
- [ ] Package standalone desktop equivalents utilizing cross-platform desktop UI layers.

---

## 📝 License

This project is licensed under the **MIT License**.

> **Disclaimer:** This software is explicitly developed for educational purposes, auditing, and defensive mechanism learning. Please do not apply these analysis methodologies for unauthorized testing.
