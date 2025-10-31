# Stage 3: Operational Visibility & Alerting

Blue/Green deployment system with automatic failover detection and Slack alerting.

## Features

✅ **Custom Nginx logging** with pool, release, upstream status, and latency  
✅ **Real-time log monitoring** with Python watcher service  
✅ **Automatic failover detection** (blue ↔ green pool switches)  
✅ **Error rate alerting** with configurable thresholds and sliding windows  
✅ **Slack integration** with rate limiting and deduplication  
✅ **Maintenance mode** to suppress alerts during planned changes  
✅ **Comprehensive runbook** for operator response  

## Prerequisites

- Docker & Docker Compose
- Slack workspace with incoming webhook
- Stage 2 setup (blue/green pools configured)

## Quick Start

### 1. Setup Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required variables:**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
BLUE_IMAGE=your-app:blue
GREEN_IMAGE=your-app:green
```

### 2. Get Slack Webhook URL

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Enable "Incoming Webhooks"
4. Add webhook to a channel
5. Copy the webhook URL to `.env`

### 3. Launch Services

```bash
# Start all services
docker compose up -d

# Check logs
docker compose logs -f alert_watcher
```

### 4. Generate Test Traffic

```bash
# Normal traffic
for i in {1..50}; do curl -i http://localhost:8080/; sleep 0.1; done

# Initiate chaos
curl -X POST http://localhost:8081/chaos/start?mode=error
```
# Create test trafic to check failover
for i in {1..50}; do curl -i http://localhost:8080/; sleep 0.1; done
(should show green pool as current)

# 4. Failover alert sent to Slack using Webhook
Check slack for failover alert with details

# Stop chaos
curl -X POST http://localhost:8081/chaos/stop

# Confirm pool switched back to blue (default)
for i in {1..50}; do curl -i http://localhost:8080/; sleep 0.1; done


## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│          Nginx (Port 8080)      │
│  - Custom log format            │
│  - Pool routing (blue/green)    │
│  - Automatic failover           │
└────────┬────────────────────────┘
         │
         ├─────────────┬──────────────┐
         ▼             ▼              ▼
    ┌────────┐    ┌────────┐    ┌──────────────┐
    │  Blue  │    │ Green  │    │Alert Watcher │
    │  Pool  │    │  Pool  │    │  (Python)    │
    │ :8081  │    │ :8082  │    │              │
    └────────┘    └────────┘    └──────────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │  Slack   │
                                  └──────────┘
```

## Log Format

Nginx logs include:

```
pool=blue release=v1.0.0 upstream_status=200 upstream_addr=172.18.0.3:3000 request_time=0.012 upstream_response_time=0.010
```

## Alert Types

### Failover Alert
Triggered when traffic switches between pools.

**Example:**
```
⚠️ FAILOVER
Pool failover detected!
• Previous: blue
• Current: green
• Time: 2025-10-31 14:23:45
• Action: Check health of blue pool
```

### Error Rate Alert
Triggered when 5xx error rate exceeds threshold.

**Example:**
```
🚨 ERROR_RATE
High error rate detected!
• Error Rate: 4.50% (threshold: 2%)
• 5xx Errors: 9/200 requests
• Current Pool: blue
• Time: 2025-10-31 14:30:12
• Action: Check upstream logs and consider pool toggle
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | - | Slack webhook (required) |
| `ACTIVE_POOL` | blue | Active pool (blue/green) |
| `ERROR_RATE_THRESHOLD` | 2 | Error % to trigger alert |
| `WINDOW_SIZE` | 200 | Request window for error rate |
| `ALERT_COOLDOWN_SEC` | 300 | Seconds between duplicate alerts |
| `MAINTENANCE_MODE` | false | Suppress failover alerts |

### Adjusting Sensitivity

**Reduce false positives:**
```bash
ERROR_RATE_THRESHOLD=5
WINDOW_SIZE=500
ALERT_COOLDOWN_SEC=600
```

**Increase sensitivity:**
```bash
ERROR_RATE_THRESHOLD=1
WINDOW_SIZE=100
ALERT_COOLDOWN_SEC=180
```

## Testing

```

### Test Error Rate Alert

# 1. Initiate chaos on blue and green image
curl -X POST http://localhost:8081/chaos/start?mode=error
curl -X POST http://localhost:8082/chaos/start?mode=error

# 2. Generate traffic to exceed threshold >2%
for i in {1.50}; do 
  curl -i http://localhost:8080/version > /dev/null
  sleep 0.05
done

# 3. Check Slack for error rate alert

# 4. Stop Chaos for both images
curl -X POST http://localhost:8081/chaos/stop
curl -X POST http://localhost:8082/chaos/stop

## Alternatively

while true; do
  echo "✅ Normal check..."
  curl -i "http://localhost:8080/version"
  sleep 5

  echo "💥 Starting chaos..."
  curl -X POST "http://localhost:8081/chaos/start?mode=error"
  curl -X POST "http://localhost:8082/chaos/start?mode=error"
  sleep 5

  echo "🧹 Stopping chaos..."
  curl -X POST "http://localhost:8081/chaos/stop"
  curl -X POST "http://localhost:8082/chaos/stop"
  sleep 5

  echo "🔁 Checking version after chaos..."
  curl -i "http://$SERVER_IP:8080/version"
  echo ""
  echo "---------------------------------------"
  sleep 5
done

# Expected: Error rate alert if threshold exceeded
```

### Test Maintenance Mode

```bash
# Enable maintenance mode
echo "MAINTENANCE_MODE=true" >> .env
docker-compose restart alert_watcher

# Toggle pool (no failover alert should fire)
ACTIVE_POOL=green docker-compose up -d

# Disable maintenance mode
sed -i 's/MAINTENANCE_MODE=true/MAINTENANCE_MODE=false/' .env
docker-compose restart alert_watcher
```

## Troubleshooting

### No alerts received

1. **Verify Slack webhook:**
   ```bash
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"Test"}' \
     $SLACK_WEBHOOK_URL
   ```

2. **Check watcher logs:**
   ```bash
   docker-compose logs alert_watcher
   ```

3. **Verify Nginx logs:**
   ```bash
   docker-compose exec nginx tail /var/log/nginx/access.log
   ```

### Alerts not triggering

- Check thresholds are appropriate
- Verify enough traffic is being generated
- Check alert cooldown hasn't been triggered
- Ensure maintenance mode is disabled

### Log parsing errors

```bash
# Check log format matches pattern
docker-compose exec nginx tail -1 /var/log/nginx/access.log

# Should contain: pool=X release=Y upstream_status=Z
```

## Project Structure

```
.
├── docker-compose.yml
├── nginx.conf.template
├── .env
├── .env.example
├── runbook.md
├── README.md
└── watcher/
    ├── Dockerfile
    ├── watcher.py
    └── requirements.txt
```

## Operational Notes

- **Alert cooldown** prevents spam (default 5 minutes)
- **Sliding window** provides better error rate accuracy
- **Maintenance mode** only suppresses failover alerts
- **Log volume** is shared between Nginx and watcher
- **Watcher restarts** automatically if it crashes
- 
## Screenshots of Error, Failover and Nginx Log

![failover](https://github.com/user-attachments/assets/27aa8794-e86e-4b3b-a9ac-44e448ad5b51)

![error1](https://github.com/user-attachments/assets/6bc4a2d3-900f-4624-8557-7208b6ee201a)

<img width="1347" height="198" alt="log" src="https://github.com/user-attachments/assets/9d0069b1-ae69-4065-9cb6-d211be21647e" />


## License

MIT
