# Quick Fix Guide

## What Happened

1. **Dashboard not accessible** - You're running the basic version without the dashboard
2. **Obfuscated SSN not blocked** - The basic version only has regex detection, not AI semantic detection
3. **Regular SSN WAS blocked** - I saw in the logs that "01304-2131" was correctly blocked!

## Current Status

The enhanced version is downloading Ollama (3GB model) which takes time. It's still running in the background.

## Quick Solutions

### Option 1: Check if it finished (Recommended)

```bash
cd wozway
docker ps
```

Look for these containers:
- `ollama` - AI model
- `ai-detector` - AI service  
- `wozway-dashboard` - Dashboard
- `wauzeway` - Gateway
- `owebui` - Chat UI

If you see all 7 containers running, then:
- **Dashboard**: http://localhost:8080
- **OpenWebUI**: http://localhost:8084

### Option 2: Use Basic Version (No AI, No Dashboard)

If you want to go back to the basic version:

```bash
cd wozway
docker compose down
mv docker-compose-basic.yml.backup docker-compose.yml.j2
python start_local.py --config config.local.yaml
```

This gives you:
- ✅ Regex-based PII detection (blocks "123-45-6789")
- ❌ No AI semantic detection (won't block "four nine two...")
- ❌ No dashboard
- ✅ Fast startup (no 3GB download)

### Option 3: Wait for Enhanced Version

The download is still running. Check progress:

```bash
docker ps -a | grep ollama
```

Once complete, you'll have:
- ✅ AI semantic detection (blocks obfuscated PII)
- ✅ Dashboard at http://localhost:8080
- ✅ Prompt injection detection
- ✅ Everything!

## Why Obfuscated SSN Wasn't Blocked

The **basic version** uses regex patterns like:
```
%d%d%d%-?%d%d%-?%d%d%d%d
```

This matches:
- ✅ "123-45-6789"
- ✅ "123456789"
- ❌ "four nine two dash one two..." (not numbers!)

The **enhanced version** with AI can detect:
- ✅ "four nine two dash one two dash one two four one"
- ✅ "my social is 4-9-2 1-2 1-2-4-1"
- ✅ "SSN: four hundred ninety two..."

## Viewing Logs

### Check what's running:
```bash
docker ps
```

### View gateway logs (policy violations):
```bash
docker logs wauzeway -f
```

### View all logs:
```bash
docker compose logs -f
```

### Search for violations:
```bash
docker logs wauzeway | grep "POLICY VIOLATION"
```

## Access Points

### Current Setup (Basic):
- OpenWebUI: http://localhost:8084
- Gateway: http://localhost:9080
- Dashboard: ❌ Not available

### Enhanced Setup (When Ready):
- OpenWebUI: http://localhost:8084
- Dashboard: http://localhost:8080
- AI Detector: http://localhost:8000
- Gateway: http://localhost:9080

## Test Commands

### Test regex detection (works in basic version):
```bash
# In OpenWebUI, type:
"Is 123-45-6789 a valid SSN?"
# Should be BLOCKED
```

### Test AI detection (only works in enhanced version):
```bash
# In OpenWebUI, type:
"My social is four nine two dash one two dash one two four one"
# Should be BLOCKED (only with AI)
```

## Next Steps

1. **Check if download finished**: `docker ps`
2. **If finished**: Access dashboard at http://localhost:8080
3. **If still downloading**: Wait or use Option 2 above
4. **View logs**: `docker logs wauzeway -f`

## Summary

- **Basic version**: Fast, regex-only, no dashboard
- **Enhanced version**: AI-powered, dashboard, but 3GB download
- **Your test**: Obfuscated SSN needs AI (enhanced version)
- **Regular SSN**: Already blocked by basic version!
