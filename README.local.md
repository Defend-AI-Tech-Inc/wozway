# Local-Only Setup for wozway

This branch provides a **fully local** setup that runs APISIX and OpenWebUI with **local policy enforcement** - no DefendAI cloud service or registration required!

## 🚀 Quick Start

### Prerequisites
- **Docker Desktop** installed and running
- **Python 3.7+**
- **Git**

### Step 1: Clone and Switch to Local-Only Branch

```bash
git clone https://github.com/Defend-AI-Tech-Inc/wozway.git
cd wozway
git checkout local-only-setup
```

### Step 2: Create Virtual Environment and Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Run the Interactive Setup

```bash
python start_local.py
```

The script will:
1. ✅ Check if Docker is running
2. ✅ Ask you to choose LLM provider (Groq or OpenAI)
3. ✅ Prompt for your API key
4. ✅ Validate the API key format
5. ✅ Save configuration to `config.local.yaml`
6. ✅ Start all Docker services
7. ✅ Test the gateway connection
8. ✅ Open OpenWebUI in your browser

### Step 4: Get Your API Key

**For Groq (Recommended - Free tier available):**
1. Go to https://console.groq.com/keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `gsk_`)

**For OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

### Step 5: Access OpenWebUI

Once setup completes, your browser will automatically open to:
```
http://localhost:8084
```

Start chatting! The local policy enforcement will automatically block sensitive data.

## 🛡️ Local Policy Enforcement

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

Try asking in OpenWebUI:
```
"Is 492-12-1241 a valid SSN?"
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

To add or modify patterns, edit `apisix/local_policy.lua` and restart services:
```bash
docker compose down
docker compose up -d
```

## 📦 What's Running

- **OpenWebUI** (port 8084): Web interface for interacting with LLMs
  - Base URL: `http://wauzeway:9080/openai/v1`
  - Authentication disabled for local use
- **APISIX/Wauzeway** (port 9080): API gateway with local policy enforcement
  - Routes requests to Groq API
  - Enforces local security policies
- **etcd** (port 2379): Configuration storage for APISIX
- **adminsvc**: Admin service that configures APISIX routes

## 🔧 Advanced Usage

### Using Existing Config

If you already have a `config.local.yaml` file:

```bash
python start_local.py --config config.local.yaml
```

### Skip Gateway Test

To skip the automatic gateway connection test:

```bash
python start_local.py --skip-test
```

### Manual Configuration

Edit `config.local.yaml`:

```yaml
tenant:
  name: local
  api_key: local-api-key

llm_providers:
  groq:
    api_key: YOUR_GROQ_API_KEY_HERE
```

Then run:
```bash
python start_local.py --config config.local.yaml
```

## 🛑 Stopping Services

```bash
docker compose down
```

To also remove volumes and data:
```bash
docker compose down -v
```

## 🐛 Troubleshooting

### Docker not running
```
ERROR - Docker Engine is not running. Please start Docker and try again.
```
**Solution:** Start Docker Desktop

### Invalid API Key
```
✗ Gateway returned 401 Unauthorized
```
**Solution:** 
1. Verify your API key at https://console.groq.com/keys
2. Update `config.local.yaml` with a valid key
3. Restart: `docker compose down && python start_local.py --config config.local.yaml`

### Port already in use
If port 8084 is already in use, edit `docker-compose.yml.j2`:
```yaml
ports:
  - 8085:3082  # Change 8084 to 8085
```

### Models not showing in OpenWebUI
1. Check gateway: `curl http://localhost:9080/openai/v1/models`
2. Check logs: `docker logs owebui`
3. Restart: `docker restart owebui`

### Policy not blocking sensitive data
1. Check logs: `docker logs wauzeway | grep "POLICY VIOLATION"`
2. Verify route: `curl -s http://localhost:9180/apisix/admin/routes/local-policy-chat -H "X-API-KEY: edd1c9f034335f136f87ad84b625c81f"`
3. Restart services: `docker compose down && docker compose up -d`

## 📊 Testing Policy Enforcement

Test SSN blocking:
```bash
curl -s http://localhost:9080/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "is 492-12-1241 a valid ssn?"}]
  }'
```

Test credit card blocking:
```bash
curl -s http://localhost:9080/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "Is 4532-1234-5678-9010 valid?"}]
  }'
```

Test normal request (should work):
```bash
curl -s http://localhost:9080/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b-instant",
    "messages": [{"role": "user", "content": "What is 2+2?"}]
  }'
```

## 🆚 Differences from Main Branch

- ✅ No DefendAI cloud service required
- ✅ No API registration or email verification
- ✅ Fully local policy enforcement
- ✅ Interactive setup with API key validation
- ✅ Automatic gateway testing
- ✅ Pattern-based sensitive data detection
- ✅ Simplified startup process

## 📝 Architecture

```
User Request → APISIX Gateway → Local Policy Plugin
                                      ↓
                              [Check for sensitive patterns]
                                      ↓
                              [BLOCK if SSN/CC/Keys found]
                                      ↓
                              [Forward to Groq if clean]
                                      ↓
                              Response → User
```

## 🤝 Support

For issues or questions:
- Open an issue on [GitHub](https://github.com/Defend-AI-Tech-Inc/wozway/issues)
- Join our [Discord](https://discord.com/invite/NBgaCkmJPR)
- Email: support@defendai.tech

## 📄 License

Apache 2.0 - see [LICENSE](LICENSE) file for details.
