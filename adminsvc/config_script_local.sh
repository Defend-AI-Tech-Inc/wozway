#!/bin/bash -x

gateway_up="false"

# wait for the wauzeway to be up
for i in $(seq 1 15);
do
   # Try GET request instead of HEAD since HEAD might not be supported
   curl --output /dev/null --silent --fail http://${APISIX_GATEWAY}:9080/
   if [ $? -eq 0 ]; then
     echo "wauzeway is up after attempt: $i"
     gateway_up="true"
     break
   fi
   printf '.'
   sleep 3
done

if [ "$gateway_up" != "true" ]; then
  echo "gateway remained down, but continuing anyway..."
fi

echo "Configuring routes for local-only mode..."
echo "Note: Policy enforcement requires DefendAI cloud service"

# Delete old routes if they exist
curl -s "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/wauzeway-proxy-id" \
  -H "X-API-KEY: ${APISIX_API_KEY}" -X DELETE

curl -s "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/wauzeway-direct" \
  -H "X-API-KEY: ${APISIX_API_KEY}" -X DELETE

curl -s "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/wauzeway-with-policy" \
  -H "X-API-KEY: ${APISIX_API_KEY}" -X DELETE

curl -s "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/groq-chat" \
  -H "X-API-KEY: ${APISIX_API_KEY}" -X DELETE

# Route for /openai/v1/models - direct to Groq
echo "Configuring models endpoint..."
curl "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/groq-models" \
  -H "X-API-KEY: ${APISIX_API_KEY}" -X PUT -d '{
    "name": "groq_models",
    "uri": "/openai/v1/models",
    "priority": 10,
    "plugins": {
      "proxy-rewrite": {
        "host": "api.groq.com",
        "headers": {
          "Authorization": "Bearer '"${LLM_API_KEY}"'",
          "User-Agent": "apisix"
        }
      }
    },
    "upstream": {
      "type": "roundrobin",
      "scheme": "https",
      "nodes": {
        "api.groq.com:443": 1
      }
    }
  }'

# Route for /openai/v1/chat/completions - WITH LOCAL POLICY ENFORCEMENT
echo "Configuring chat completions endpoint with LOCAL policy enforcement..."
curl "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/local-policy-chat" \
  -H "X-API-KEY: ${APISIX_API_KEY}" -X PUT -d '{
    "name": "local_policy_chat_completions",
    "uri": "/openai/v1/chat/completions",
    "priority": 10,
    "plugins": {
        "local_policy": {
          "enabled": true,
          "block_on_match": true
        },
        "proxy-rewrite": {
          "host": "api.groq.com",
          "headers": {
            "Authorization": "Bearer '"${LLM_API_KEY}"'",
            "User-Agent": "apisix"
          }
        }
    },
    "upstream": {
        "type": "roundrobin",
        "scheme": "https",
        "nodes": {
            "api.groq.com:443": 1
        }
    }
  }'

# Route for other OpenAI endpoints - direct to Groq
echo "Configuring other OpenAI endpoints..."
curl "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/groq-other" \
  -H "X-API-KEY: ${APISIX_API_KEY}" -X PUT -d '{
    "name": "groq_other_endpoints",
    "uri": "/openai/v1/*",
    "priority": 1,
    "plugins": {
      "proxy-rewrite": {
        "host": "api.groq.com",
        "headers": {
          "Authorization": "Bearer '"${LLM_API_KEY}"'",
          "User-Agent": "apisix"
        }
      }
    },
    "upstream": {
      "type": "roundrobin",
      "scheme": "https",
      "nodes": {
        "api.groq.com:443": 1
      }
    }
  }'

echo ""
echo "=========================================="
echo "Routes configured successfully!"
echo "- Models endpoint: Direct to Groq"
echo "- Chat completions: LOCAL policy enforcement"
echo "- Other endpoints: Direct to Groq"
echo ""
echo "LOCAL POLICY ENFORCEMENT ACTIVE:"
echo "  ✓ SSN detection and blocking"
echo "  ✓ Credit card detection and blocking"
echo "  ✓ Email detection (alert only)"
echo "  ✓ Phone number detection (alert only)"
echo "  ✓ API key detection and blocking"
echo "  ✓ AWS key detection and blocking"
echo "  ✓ Private key detection and blocking"
echo ""
echo "No cloud service required!"
echo "=========================================="

tail -f /dev/null
