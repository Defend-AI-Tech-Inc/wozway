# Local-Only Setup for wozway

This branch provides a simplified setup that runs APISIX and OpenWebUI locally without requiring DefendAI API registration.

## Quick Start

### Option 1: Interactive Setup (Recommended)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the interactive setup**
   ```bash
   python start_local.py
   ```
   
   The script will:
   - Ask you to choose between Groq or OpenAI (OpenAI coming soon)
   - Prompt for your API key
   - Validate the API key format
   - Save the configuration
   - Start all services
   - Test the gateway connection
   - Open OpenWebUI in your browser

### Option 2: Using Existing Config

If you already have a `config.local.yaml` file:

```bash
python start_local.py --config config.local.yaml
```

## Configuration

The script creates a `config.local.yaml` file:

```yaml
tenant:
  name: local
  api_key: local-api-key

llm_providers:
  groq:
    api_key: YOUR_GROQ_API_KEY_HERE
```

## Local Policy Enforcement

**✅ FULLY LOCAL POLICY ENFORCEMENT - NO CLOUD REQUIRED!**

This setup includes a custom local policy enforcement plugin that checks for sensitive data patterns directly in the gateway, without requiring any cloud service.

### What's Protected:

**BLOCKED (Request will be rejected):**
- ✅ Social Security Numbers (SSN) - Format: XXX-XX-XXXX or XXXXXXXXX
- ✅ Credit Card Numbers - Format: XXXX-XXXX-XXXX-XXXX
- ✅ API Keys - Patterns like `api_key="xxx"` or `API_KEY=xxx`
- ✅ AWS Access Keys - Format: AKIAXXXXXXXXXXXXXXXX
- ✅ Private Keys - Detects `-----BEGIN PRIVATE KEY-----`

**ALERTED (Logged but not blocked):**
- ⚠️ Email Addresses
- ⚠️ Phone Numbers

### How It Works:

1. Request comes in → Local Policy Plugin checks for patterns
2. If sensitive data detected → Request blocked with clear error message
3. If clean → Request forwarded to Groq API

### Example Blocked Request:

```bash
curl http://localhost:9080/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "is 492-12-1241 a valid ssn?"}]
  }'
```

**Response:**
```json
{
  "error": "Request blocked by wozway local policy",
  "reason": "Sensitive data detected",
  "violations": ["Social Security Number"],
  "message": "Your request contains sensitive information that is not allowed. Please remove: Social Security Number"
}
```

### Customizing Policies:

To add or modify patterns, edit `apisix/local_policy.lua` and restart services.

- **OpenWebUI** (port 8084): Web interface for interacting with LLMs
  - Base URL configured to: `http://wauzeway:9080/openai/v1`
  - Authentication disabled for local use
- **APISIX/Wauzeway** (port 9080): API gateway for routing requests
  - Routes requests through the gateway to Groq API
  - Provides proxy and security features
- **etcd** (port 2379): Configuration storage for APISIX
- **adminsvc**: Admin service that configures APISIX routes

## Gateway Testing

The script automatically tests the gateway by calling:
```
http://localhost:9080/openai/v1/models
```

If successful, you'll see:
```
✓ Gateway is responding correctly!
✓ Found X available models
```

If the test fails with 401 Unauthorized:
- Your API key may be invalid or expired
- Get a new API key from https://console.groq.com/keys

## Accessing OpenWebUI

After successful startup:
1. Browser opens automatically to http://localhost:8084
2. No login required (authentication disabled for local use)
3. Start chatting with your selected LLM models

## Stopping Services

```bash
docker compose down
```

To also remove volumes:
```bash
docker compose down -v
```

## Command Line Options

```bash
python start_local.py --help
```

Options:
- `--config PATH`: Use existing config file (skips interactive setup)
- `--skip-test`: Skip gateway connection test

## Troubleshooting

**Docker not running:**
```
ERROR - Docker Engine is not running. Please start Docker and try again.
```
Solution: Start Docker Desktop

**Gateway test fails:**
```
✗ Gateway returned 401 Unauthorized
```
Solution: 
1. Verify your API key at https://console.groq.com/keys
2. Update `config.local.yaml` with a valid key
3. Restart: `docker compose down && python start_local.py --config config.local.yaml`

**Port already in use:**
If port 8084 is already in use, you can modify the port in `docker-compose.yml.j2`:
```yaml
ports:
  - 8085:3082  # Change 8084 to 8085
```

**Models not showing in OpenWebUI:**
1. Check gateway is working: `curl http://localhost:9080/openai/v1/models`
2. Check OpenWebUI logs: `docker logs owebui`
3. Restart OpenWebUI: `docker restart owebui`

## Differences from Main Branch

- ✅ No DefendAI API registration required
- ✅ No email verification
- ✅ No cloud connectivity
- ✅ Interactive setup with API key validation
- ✅ Automatic gateway testing
- ✅ Local-only configuration
- ✅ Simplified startup process
