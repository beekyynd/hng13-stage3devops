#!/usr/bin/env python3
import os
import re
import time
import subprocess
import requests
from collections import deque

# === CONFIG ===
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
ERROR_RATE_THRESHOLD = float(os.getenv('ERROR_RATE_THRESHOLD', 2))
WINDOW_SIZE = int(os.getenv('WINDOW_SIZE', 200))
ALERT_COOLDOWN_SEC = int(os.getenv('ALERT_COOLDOWN_SEC', 300))
MAINTENANCE_MODE = os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'
LOG_FILE = '/var/log/nginx/access.log'

# === STATE ===
last_pool = None
last_alert_pool = None
request_window = deque(maxlen=WINDOW_SIZE)
last_alert_time = {'failover': 0, 'error_rate': 0}

# Matches pool, release, upstream_status, upstream_addr, request_time, upstream_response_time
LOG_PATTERN = re.compile(
    r'pool=([^ ]+).*?release=([^ ]+).*?upstream_status=([^ ]+).*?upstream_addr=([^ ]+).*?request_time=([\d\.]+).*?upstream_response_time=([\d\.,]+)'
)


def send_slack(message, alert_type):
    """Send alert to Slack or print locally."""
    global last_alert_time
    if not SLACK_WEBHOOK_URL:
        print(f"[ALERT] {message}")
        return
    
    if MAINTENANCE_MODE and alert_type == 'failover':
        return

    now = time.time()
    if now - last_alert_time.get(alert_type, 0) < ALERT_COOLDOWN_SEC:
        print(f"[SKIP] Cooldown active for {alert_type}")
        return

    try:
        requests.post(SLACK_WEBHOOK_URL, json={'text': message}, timeout=5)
        last_alert_time[alert_type] = now
        print(f"[SLACK] Sent {alert_type}: {message[:80]}...")
    except Exception as e:
        print(f"[ERROR] Slack send failed: {e}")


def check_failover(pool, release, upstream_status, upstream_addr, request_time, upstream_response_time):
    """Detect and alert on blue-green switch."""
    global last_pool, last_alert_pool

    if not pool:
        return

    if last_pool is None:
        last_pool = pool
        print(f"[INIT] Initial pool: {pool}")
        return

    if pool == last_pool:
        return  # same pool → ignore

    # Build message
    msg = (
        f"🔄 *Failover Detected*\n"
        f"Pool switched: `{last_pool}` → `{pool}`\n\n"
        f"*Details:*\n"
        f"• Release: `{release}`\n"
        f"• Upstream Addr: `{upstream_addr}`\n"
        f"• Request Time: `{request_time}s`\n"
        f"• Upstream Response Time: `{upstream_response_time}`"
    )

    if pool != last_alert_pool:
        send_slack(msg, 'failover')
        print(f"[INFO] Failover alert sent: {last_pool} → {pool}")
        last_alert_pool = pool
    else:
        print(f"[SKIP] Duplicate failover alert suppressed for pool {pool}")

    last_pool = pool


def check_error_rate():
    """Monitor recent window for excessive 5xx errors."""
    if len(request_window) < 50:
        return

    errors = sum(1 for s in request_window if s >= 500)
    rate = (errors / len(request_window)) * 100

    if rate > ERROR_RATE_THRESHOLD:
        msg = (
            f"⚠️ *High Error Rate Detected*\n"
            f"Error Rate: `{rate:.2f}%` (threshold: {ERROR_RATE_THRESHOLD}%)\n"
            f"Errors: {errors}/{len(request_window)} requests"
        )
        send_slack(msg, 'error_rate')


print("[START] Log watcher starting...")
print(f"[CONFIG] Threshold={ERROR_RATE_THRESHOLD}%, Window={WINDOW_SIZE}, Cooldown={ALERT_COOLDOWN_SEC}s")

while not os.path.exists(LOG_FILE):
    print(f"[WAIT] Waiting for {LOG_FILE}...")
    time.sleep(2)

print(f"[READY] Tailing {LOG_FILE}")

process = subprocess.Popen(['tail', '-f', '-n', '0', LOG_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

try:
    for line in iter(process.stdout.readline, b''):
        line = line.decode('utf-8').strip()
        if not line:
            continue

        match = LOG_PATTERN.search(line)
        if not match:
            continue

        pool, release, upstream_status, upstream_addr, request_time, upstream_response_time = match.groups()

        # Take the last status code for error rate
        try:
            status = int(upstream_status.split(',')[-1].strip())
        except ValueError:
            status = 0

        request_window.append(status)
        check_failover(pool, release, upstream_status, upstream_addr, request_time, upstream_response_time)
        check_error_rate()

except KeyboardInterrupt:
    process.kill()
    print("\n[STOP] Watcher stopped")
