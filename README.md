# Secure IoT-Based Medical Device Monitoring System

A full-stack Django + MongoDB web application for real-time monitoring of hospital IoT devices with built-in cybersecurity mechanisms.

---

## Features

| Feature | Implementation |
|---|---|
| **AES-256-CBC Encryption** | All device→server payloads are encrypted |
| **HMAC Device Authentication** | Each device carries a unique HMAC-SHA256 token |
| **SHA-256 Integrity Hashing** | Every reading is hash-verified before storage |
| **Anomaly Detection** | Out-of-range vitals trigger automatic alerts |
| **Audit Logging** | Every login, device event, and alert is logged |
| **Real-time Dashboard** | Live Chart.js charts polling every 5 seconds |
| **MongoDB Storage** | Patient readings, devices, alerts, audit logs |
| **In-memory Fallback** | Runs without MongoDB for quick demos |

---

## Project Structure

```
iot_medical/
├── iot_medical/            # Django project config
│   ├── settings.py         # Configuration (DB, encryption keys)
│   ├── urls.py             # Root URL routing
│   └── wsgi.py
│
├── monitor/                # Main Django app
│   ├── db.py               # MongoDB connection + in-memory fallback
│   ├── security.py         # Encryption, hashing, auth, anomaly detection
│   ├── views.py            # All HTTP views + REST API endpoints
│   ├── urls.py             # App URL routing
│   └── templates/monitor/
│       ├── base.html       # Sidebar layout, CSS design system
│       ├── login.html      # Authentication page
│       ├── dashboard.html  # Live charts + stats
│       ├── devices.html    # Device registry
│       ├── alerts.html     # Security alerts
│       └── audit_log.html  # Audit trail
│
├── iot_simulator/
│   └── simulator.py        # Simulates 5 IoT devices sending live data
│
├── manage.py
├── setup.py                # One-time setup script
└── requirements.txt
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run setup (creates DB, admin user, sample data)

```bash
python setup.py
```

### 3. Start the Django server

```bash
python manage.py runserver
```

Open **http://localhost:8000** — log in with `admin` / `admin123`.

### 4. Start the IoT Simulator (separate terminal)

```bash
python iot_simulator/simulator.py
```

The simulator will:
- Register 5 virtual devices (DEV-001 through DEV-005)
- Send encrypted, authenticated, hashed vitals every 5 seconds
- Randomly generate anomalous readings (~15% chance per device)
- Attempt a rogue/spoofed device connection every 5 rounds (to test auth rejection)

---

## Security Architecture

```
IoT Device (Simulator)
        │
        │  1. Generate patient vitals
        │  2. Encrypt payload (AES-256-CBC)
        │  3. Compute SHA-256 hash
        │  4. Attach HMAC device token
        │
        ▼
   POST /api/receive-data/
        │
        │  5. Verify HMAC token         → reject if invalid (401)
        │  6. Decrypt AES payload       → reject if corrupt (400)
        │  7. Verify SHA-256 hash       → reject if tampered (400)
        │  8. Run anomaly detection     → create alert if triggered
        │  9. Store in MongoDB
        │ 10. Update device status
        │
        ▼
   Dashboard (polling every 5s)
```

### Encryption Key Setup (Production)

Set environment variables instead of using the defaults:

```bash
export ENCRYPTION_KEY="your-32-byte-secret-key-here!!!!"
export DEVICE_SECRET="your-device-hmac-secret"
```

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| `POST` | `/api/register-device/` | Register a new IoT device |
| `POST` | `/api/receive-data/` | Ingest encrypted device reading |
| `GET`  | `/api/readings/` | Fetch recent readings (JSON) |
| `GET`  | `/api/device-status/` | Current device statuses |
| `GET`  | `/api/stats/` | Dashboard summary stats |
| `GET`  | `/api/resolve-alert/<id>/` | Mark alert as resolved |

---

## Anomaly Detection Thresholds

| Vital | Normal Range | Alert Triggered Outside |
|---|---|---|
| Heart Rate | 40–180 bpm | < 40 or > 180 |
| Temperature | 35.0–40.0 °C | < 35 or > 40 |
| BP Systolic | 80–180 mmHg | < 80 or > 180 |
| BP Diastolic | 40–120 mmHg | < 40 or > 120 |
| SpO₂ | 90–100 % | < 90 |
| Respiratory Rate | 8–30 breaths/min | < 8 or > 30 |
| Glucose | 50–400 mg/dL | < 50 or > 400 |

---

## MongoDB Collections

| Collection | Contents |
|---|---|
| `devices` | Registered device profiles and status |
| `readings` | All patient vital readings with hash + anomaly flag |
| `alerts` | Security and anomaly alerts |
| `audit_logs` | Full audit trail of system events |

---

## Tech Stack

- **Backend**: Python 3.10+, Django 4.2
- **Database**: MongoDB (PyMongo) with SQLite for Django auth
- **Security**: PyCryptodome (AES-256), HMAC-SHA256, SHA-256
- **Frontend**: HTML5, CSS3 (dark theme), Chart.js 4
- **Simulator**: Pure Python with `requests`
