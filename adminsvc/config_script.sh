#!/bin/bash -x

gateway_up:=false

# wait for the wauzeway to be up
for i in $(seq 1 10);
do
   curl --output /dev/null --silent --head --fail http://${APISIX_GATEWAY}:9080
   if [ $? -eq 0 ]; then
     echo "wauzeway is up after attempt: $i"
     gateway_up=true
     break
   fi
   printf '.'
   sleep 5
done
if [ gateway_up ]; then
  echo "gateway up"
else
  echo "gateway remained down"
fi

# openai model list
curl "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/catchall-3"  -H "X-API-KEY: ${APISIX_API_KEY}"  -X PUT -d '{ "name": "catch_groq_models", "uri": "/openai/v1/models", "plugins":{"proxy-rewrite": {"host": "api.groq.com","headers": {"Authorization": "Bearer '"${GROQ_API_KEY}"'", "User-Agent": "apisix"}}}, "upstream": {"type": "roundrobin", "scheme":"https", "nodes": {"api.groq.com:443":1}}}'

# wauzeway route
curl "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/wauzeway-proxy-id" \
-H "X-API-KEY: ${APISIX_API_KEY}" -X PUT -d '
{
    "uri": "/openai/v1/*",
    "plugins": {
        "wauzeway_proxy": {
          "type": "lua",
          "description": "Custom plugin to proxy for wauzeway",
          "config": {
            "script": "/opt/apisix/plugins/wauzeway_proxy.lua",
            "priority": 1001,
            "us_uri": "/wauzeway",
            "tenant_id": "'"${DEFENDAI_TENANT_ID}"'",
            "api_key": "'"${DEFENDAI_API_KEY}"'",
            "llm_provider": "'"${LLM_PROVIDER}"'",
            "llm_api_key": "'"${LLM_API_KEY}"'",
            "groq_api_key": "'"${GROQ_API_KEY}"'"
            },
          "rejected_msg": "customize reject message: unsafe prompt"
        }
    },
    "upstream": {
        "type": "roundrobin",
        "scheme": "https",
        "pass_host": "rewrite",
        "upstream_host": "wauzeway.defendai.tech",
        "nodes": {
            "wauzeway.defendai.tech:443": 1
        }
    }
}'
curl "http://${APISIX_GATEWAY}:9180/apisix/admin/routes/wauzeway-direct" \
  -H "X-API-KEY: ${APISIX_API_KEY}" \
  -X PUT -d '{
    "uri": "/wauzeway",
    "methods": ["POST"],
    "upstream": {
      "type": "roundrobin",
      "scheme": "https",
      "pass_host": "rewrite",
      "upstream_host": "wauzeway.defendai.tech",
      "nodes": {
        "wauzeway.defendai.tech:443": 1
      }
    }
  }'


tail -f /dev/null
