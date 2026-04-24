#!/usr/bin/env python3
"""
setup.py — One-time setup for the IoT Medical Monitoring System.

Run this ONCE before starting the server:
    python setup.py

What it does:
  1. Installs Python dependencies (if pip is available)
  2. Runs Django migrations (creates SQLite DB for auth/sessions)
  3. Creates an 'admin' superuser (password: admin123)
  4. Optionally seeds MongoDB with sample data
"""

import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iot_medical.settings')
sys.path.insert(0, BASE)


def run(cmd, **kwargs):
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"[ERROR] Command failed with exit code {result.returncode}")
    return result.returncode == 0


def main():
    print("=" * 60)
    print("  IoT Medical Monitoring System — Setup")
    print("=" * 60)

    # 1 ── Install dependencies
    print("\n[1/4] Installing Python dependencies…")
    deps = [
        'django>=4.2',
        'pymongo>=4.0',
        'pycryptodome>=3.18',
        'requests>=2.28',
    ]
    run([sys.executable, '-m', 'pip', 'install', '--quiet'] + deps)

    # 2 ── Django migrations
    print("\n[2/4] Running Django migrations…")
    run([sys.executable, 'manage.py', 'migrate', '--run-syncdb'], cwd=BASE)

    # 3 ── Create superuser
    print("\n[3/4] Creating admin superuser (admin / admin123)…")
    import django
    django.setup()
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@hospital.local', 'admin123')
        print("    ✓ Superuser 'admin' created.")
    else:
        print("    ✓ Superuser 'admin' already exists.")

    # 4 ── Seed MongoDB with sample data
    print("\n[4/4] Seeding MongoDB with sample data…")
    try:
        from monitor.db import get_devices_col, get_alerts_col, get_audit_logs_col
        from monitor.security import generate_device_token
        from datetime import datetime, timezone
        import uuid

        sample_devices = [
            {'device_id': 'DEV-001', 'device_type': 'Multi-Parameter Monitor', 'location': 'ICU - Bed 1',    'status': 'online'},
            {'device_id': 'DEV-002', 'device_type': 'Heart Rate Monitor',       'location': 'Ward A - Bed 3', 'status': 'online'},
            {'device_id': 'DEV-003', 'device_type': 'SpO2 Sensor',              'location': 'Ward B - Bed 7', 'status': 'offline'},
        ]
        col = get_devices_col()
        for d in sample_devices:
            d['token'] = generate_device_token(d['device_id'])
            d['registered_at'] = datetime.now(timezone.utc).isoformat()
            d['last_seen'] = datetime.now(timezone.utc).isoformat()
            col.update_one({'device_id': d['device_id']}, {'$set': d}, upsert=True)

        # Sample alert
        get_alerts_col().insert_one({
            'alert_id':  str(uuid.uuid4()),
            'type':      'ANOMALY_DETECTED',
            'message':   'Heart Rate = 178 bpm detected on DEV-002 (normal 40–180)',
            'severity':  'warning',
            'device_id': 'DEV-002',
            'resolved':  False,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        })

        get_audit_logs_col().insert_one({
            'event_type':  'SYSTEM_STARTUP',
            'description': 'IoT Medical Monitoring System initialised',
            'user':        'system',
            'severity':    'info',
            'timestamp':   datetime.now(timezone.utc).isoformat(),
        })

        print("    ✓ Sample data seeded.")
    except Exception as exc:
        print(f"    [WARN] Could not seed MongoDB: {exc}")
        print("    (This is OK — the system uses an in-memory fallback.)")

    print("\n" + "=" * 60)
    print("  Setup complete!")
    print()
    print("  Start the server:")
    print("    python manage.py runserver")
    print()
    print("  Then open: http://localhost:8000")
    print("  Login:     admin / admin123")
    print()
    print("  To simulate IoT devices (in another terminal):")
    print("    python iot_simulator/simulator.py")
    print("=" * 60)


if __name__ == '__main__':
    main()
