# How to View Wozway Logs

## Quick Log Commands

### View All Container Logs
```bash
cd wozway
docker compose logs
```

### View Specific Service Logs

**APISIX Gateway (policy enforcement)**:
```bash
docker logs wauzeway
docker logs wauzeway --tail 100  # Last 100 lines
docker logs wauzeway -f          # Follow (live)
```

**OpenWebUI (chat interface)**:
```bash
docker logs owebui
docker logs owebui -f
```

**Admin Service (route configuration)**:
```bash
docker logs adminsvc
```

**AI Detector (when running enhanced version)**:
```bash
docker logs ai-detector
docker logs ai-detector -f
```

**Dashboard (when running enhanced version)**:
```bash
docker logs wozway-dashboard
docker logs wozway-dashboard -f
```

**Ollama (when running enhanced version)**:
```bash
docker logs ollama
```

## What to Look For

### Policy Violations in APISIX Logs
```bash
docker logs wauzeway | grep "POLICY VIOLATION"
```

Example output:
```
[error] POLICY VIOLATION: Social Security Number detected in prompt
[warn] Policy violation detected: Credit Card Number - 4532-1234-5678-9010
```

### AI Detection Logs (Enhanced Version)
```bash
docker logs ai-detector | grep "violation"
```

### Check if Services are Healthy
```bash
docker ps
```

Look for "Up" status and "(healthy)" indicator.

## Log Locations Inside Containers

### APISIX Error Logs
```bash
docker exec wauzeway cat /usr/local/apisix/logs/error.log
```

### APISIX Access Logs
```bash
docker exec wauzeway cat /usr/local/apisix/logs/access.log
```

## Real-Time Monitoring

### Watch All Logs Together
```bash
docker compose logs -f
```

### Watch Only Policy-Related Logs
```bash
docker logs wauzeway -f 2>&1 | grep -i "policy\|violation\|block"
```

## Troubleshooting

### Service Won't Start
```bash
# Check why a service failed
docker logs <container_name>

# Check last 50 lines
docker logs <container_name> --tail 50
```

### High CPU/Memory
```bash
# Check resource usage
docker stats
```

### Network Issues
```bash
# Check if services can communicate
docker exec wauzeway ping ai-detector
docker exec wauzeway curl http://ai-detector:8000/health
```
