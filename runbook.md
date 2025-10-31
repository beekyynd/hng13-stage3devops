# Blue-Green Deployment Runbook

## Overview
This runbook provides clear operational guidance for responding to alerts in the **Blue-Green Deployment with Auto Failover** system.  
The environment continuously monitors **Nginx access logs** and posts alerts to Slack when:

- A **Failover** occurs (pool switches between Blue ↔ Green)
- A **High Error Rate** is detected (>2% of 5xx responses over the last 200 requests)

---

## Alert Types

### 1. 🔄 Failover Detected

**Meaning:**
- The active application pool switched from `blue` → `green` or vice versa.
- This occurs when one pool becomes unhealthy and Nginx reroutes requests to the healthy pool.

**Example Slack Message:**
🔄 Failover Detected
Pool switched: blue → green

Details:
• Release: green-v1.0.1
• Upstream Addr: 172.18.0.2:3000
• Request Time: 0.002s
• Upstream Response Time: 0.002s


**Operator Actions:**
1. **Check which pool is active:**
   ```bash
   curl -i http://<server-ip>:8080/version
   docker compose ps
   docker compose logs app_blue | tail -n 50
   docker compose restart app_blue
⚠️ High Error Rate Detected

Meaning:

More than 2% of requests within the last 200 produced 5xx errors.

This may happen before or after a failover event.

**Example Slack Message:**

⚠️ *High Error Rate Detected*
Error Rate: 8.00% (threshold: 2.00%)
Errors: 16/200 requests

**Operator Actions:**

Check Nginx access logs for 5xx responses:

docker compose exec nginx tail -n 50 /var/log/nginx/access.log

Inspect application logs for errors:

docker compose logs app_green | tail -n 100

If error rate persists:

Enable maintenance mode if supported.

Roll back to a previous stable release.

Restart the affected pool container.

Re-run curl -i http://<server-ip>:8080/version to confirm recovery.

🧰 Supporting Tools

**View Current Active Pool**
curl -i http://<server-ip>:8080/version

Trigger Chaos Mode:
curl -X POST http://<server-ip>:8081/chaos/start?mode=error

Stop Chaos Mode:
curl -X POST http://<server-ip>:8081/chaos/stop

**Important Notes**

Failover alerts and error-rate alerts each have a 5-minute cooldown.

When MAINTENANCE_MODE=true, failover alerts are skipped.

All real-time monitoring is handled by watcher.py, which tails the Nginx access log.

The system automatically appends each response’s status (upstream_status) to the monitoring queue.

