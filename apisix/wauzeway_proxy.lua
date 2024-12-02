-- custom lua plugin for vauzeway integration
local core     = require("apisix.core")
local io       = require("io")
local ngx      = require("ngx")
local http     = require("resty.http")
local cjson    = require("cjson.safe")
local json     = require("apisix.core.json")

-- Deine variables based on env
local UPSTREAM_URI = os.getenv("APISIX_UPSTREAM_URI") or "/wauzeway"

-- IDs for multi-tenancy
local CLIENT_API_KEY = os.getenv("DEFENDAI_API_KEY") or "f64a2d8a-d746-4d01-8059-82981016b6e6"
local TENANT_ID = os.getenv("DEFENDAI_TENANT_ID") or "synergy"
math.randomseed(5000000)

-- LLM provider and its API key
local LLM_PROVIDER = os.getenv("LLM_PROVIDER") or "groq"
local LLM_APIKEY = os.getenv("LLM_API_KEY") or "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"

-- Declare the plugin's name
local plugin_name = "wauzeway_proxy"

-- Define the plugin schema format
local plugin_schema = {
    type = "object",
    properties = {
        --required_payload = {
        --    type = "string" -- prompt in post request
        --},
    },
    --required = {"required_payload"} -- The required_payload is a required field
}

-- Define the plugin with its version, priority, name, and schema
local _M = {
    version = 1.0,
    priority = 1001,
    name = plugin_name,
    schema = plugin_schema
}

-- Function to check if the plugin configuration is correct
function _M.check_schema(conf)
  -- Validate the configuration against the schema
  local ok, err = core.schema.check(plugin_schema, conf)
  -- If validation fails, return false and the error
  if not ok then
      return false, err
  end

  -- Initialize using environment variables
  if conf.config then
    UPSTREAM_URI = conf.config.us_uri
    TENANT_ID = conf.config.tenant_id
    CLIENT_API_KEY = conf.config.api_key
    LLM_PROVIDER = conf.config.llm_provider
    LLM_APIKEY = conf.config.llm_api_key

    ngx.log(ngx.WARN,
    "Config variables from admin api: groq_api_key: ", LLM_APIKEY,
    " us_uri: ", UPSTREAM_URI,
    " llm_provider: ", LLM_PROVIDER,
    " llm_api_key: ", LLM_APIKEY,
    " api_key: ", CLIENT_API_KEY,
    " tenant_id: ", TENANT_ID)
  end

  -- Since validation succeeded, return true
  return true
end

local function get_api_key (body, hdrs, uri_args)
    local api_key = nil
    for key, value in pairs(hdrs) do
        if type(value) == "table" then
            value = table.concat(value, ", ")
        end
        core.log.warn("Header: ", key, ": ", value)
    end

    if body then
        local pbody_cjson = cjson.new()
        local pbody_data = pbody_cjson.decode(body)
        api_key = pbody_data["api_key"]
        if not api_key then
            core.log.error("Missing api key in body; will look for it in headers.")
            api_key = hdrs["api-key"]
            if not api_key then
                core.log.error("Missing api key in headers; will look for it in uri args.")
                api_key = uri_args["API-KEY"]
                if not api_key then
                    core.log.error("Unable to find api_key; falling back to using default api_key.")
                    api_key = CLIENT_API_KEY
                    --ngx.status = ngx.HTTP_UNAUTHORIZED
                    --ngx.say("Missing api_key in body, header, or uri.")
                    --return ngx.exit(ngx.HTTP_UNAUTHORIZED)
                end
            end
        end
    end
    return api_key
end

-- Helper function to sanitize the prompt
local function sanitize_prompt(prompt)
    -- Remove non-printable characters (e.g., control characters)
    -- This pattern allows printable ASCII characters and most common UTF-8 characters
    return prompt:gsub("[^%g%s]", "") -- Remove non-printable characters but keep spaces (%s)
end

-- Extract prompt and model name from request body
local function get_prompt_and_model(body)
    local model_name = nil
    local prompt_cont = nil
    local pbody_cjson = cjson.new()
    local pbody_data = pbody_cjson.decode(body)
    model_name = pbody_data["model"]
    core.log.warn("Found model name: ", model_name)
    prompt_cont = pbody_data['prompt']
    if not prompt_cont then
        core.log.error("Missing prompt field in generate format; will look for it in chat")
        local messages = pbody_data["messages"]
        if not messages then
            core.log.error("Messages field is missing in the request body; giving up.")
            return prompt_cont, model_name
        end
        -- messages found; extract the content of last one
        for i = #messages, 1, -1 do
            if messages[i]["role"] == "user" then
                prompt_cont = messages[i]["content"]
                break
            end
        end
        core.log.warn("Found prompt content in messages: ", prompt_cont)
    end

    -- sanitize prompt_cont
    return sanitize_prompt(prompt_cont), model_name
end

-- Function to be called during the access phase
function _M.access(conf, ctx)
    -- Check if the request method is POST and URI is one of expected
    if (ngx.req.get_method() == "POST")              and
       (ngx.var.uri == "/wauzeway"                   or
        ngx.var.uri == "/v1/chat/completions"        or
        ngx.var.uri == "/chat/completions"           or
        ngx.var.uri == "/api/chat"                   or
        ngx.var.uri == "/api/v1/chats"               or
        ngx.var.uri == "/openai/v1/chat/completions" or
        ngx.var.uri == "/v1/api/chat") then

        -- Extract request body
        local req_body, err = core.request.get_body()
        if not req_body then
            ngx.log(ngx.ERR, "Failed to get request body: ", err)
            return 500, {message = "Failed to get request body"}
        end

        ngx.log(ngx.WARN, "Incomign request uri: ", ngx.var.request_uri)
        ngx.log(ngx.WARN, "req_body: ", req_body)
        local api_key = get_api_key(req_body, ngx.req.get_headers(), ngx.req.get_uri_args())
        local session_id = math.random(1000000, 9000000)
        local prompt, model_name = get_prompt_and_model(req_body)
        if not prompt then
            ngx.status = ngx.HTTP_BAD_REQUEST
            ngx.say("Messages field is missing in the request body")
            return ngx.exit(ngx.HTTP_BAD_REQUEST)
        end
        local llm_type = LLM_PROVIDER
        if ngx.var.uri == "/api/generate" then
            llm_type = "ollama"
        end
        if not model_name then
            model_name = "llama-3.1-8b-instant"
        end

        -- Construct the new JSON body
        local new_body = {
            llm_type = llm_type,
            api_key = api_key,
            llm_api_key = LLM_APIKEY,
            tenant_id = TENANT_ID,
            meta = {
                model_name = model_name
            },
            prompt = prompt
        }

        -- Debugging: Log the constructed table before encoding it to JSON
        core.log.warn("New body table: ", core.json.delay_encode(new_body, true))

        -- Convert the new body table to JSON
        local new_body_json, json_err = cjson.encode(new_body)

        if not new_body_json then
            ngx.status = ngx.HTTP_INTERNAL_SERVER_ERROR
            core.log.error("failed to encode new request body as JSON: ", json_err)
            return ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
        end

        -- Set the modified body back to the request
        ngx.log(ngx.WARN, "Transformed request body: ", new_body_json)
        ngx.req.set_body_data(new_body_json)

        -- update uri
        ngx.req.set_uri("/wauzeway")
        core.log.warn("modified uri: ", ngx.var.uri)

        -- Ensure the content-type header is set to application/json
        core.request.set_header("Content-Type", "application/json")
        
        core.log.warn("Request body transformed successfully")
        return
    end
end

-- Table to store response bodies temporarily
local response_bodies = {}

function _M.body_filter(conf, ctx)
    -- Accumulate the response body
    local chunk, eof = ngx.arg[1], ngx.arg[2]

    if not response_bodies[ctx] then
        response_bodies[ctx] = ""
    end

    if chunk then
        response_bodies[ctx] = response_bodies[ctx] .. chunk
    end

    if eof then
        ngx.log(ngx.WARN, "response eof reached; response_bodies for the ctx: ",
                tostring(response_bodies[ctx]))
        ngx.arg[1] = nil  -- Prevent further transmission of the body until verdict is made
    end
end

function _M.header_filter(conf, ctx)
    local response_body = response_bodies[ctx]

    if not response_body then
        ngx.log(ngx.WARN, "empty response_body; returning")
        return
    end

    -- Extract response from response body
    local response = get_response(response_body)
    if not response then
        ngx.log(ngx.WARN, "Response not found in response_body: ", tostring(response_body))
        ngx.status = ngx.HTTP_BAD_REQUEST
        ngx.say("Messages field is missing in the response body")
        return ngx.exit(ngx.HTTP_BAD_REQUEST)
    end
    ngx.log(ngx.WARN, "Response: ", response, " found in response_body: ", tostring(response_body))

    -- Consult verdict service about response
    local vs_res, vs_err = get_response_verdict(response, api_key, TENANT_ID, session_id)
    ngx.log(ngx.WARN, "vs_res: ", tostring(vs_res.message))
    if vs_err==500 then
        ngx.status = ngx.HTTP_INTERNAL_SERVER_ERROR
        local vs_err_msg = "Failed to interact with verdictservice: response: " ..
                            tostring(response) .. " vs_res: " .. tostring(vs_res)
        ngx.log(ngx.ERR, "vs_err_msg: ", vs_err_msg)
        ngx.say(vs_err_msg)
        return ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
    end
    if vs_err==403 then
        ngx.log(ngx.WARN, "Response blocked by verdictservice")
        ngx.arg[1] = "Response blocked by aigateway"
        ngx.arg[2] = true
        return
    end
    if vs_err==210 then
        -- modify the response with anaonymized
        ngx.log(ngx.WARN, "case 210: original response: ", response)
        ngx.log(ngx.WARN, "vs_res: ", tostring(vs_res.message))
        local an_res_body = set_response(response, tostring(vs_res.message), res_body)
        if not an_res_body then
            ngx.log(ngx.ERR, "Response anonymization failed")
            ngx.arg[1] = "Response ananymization failed"
            ngx.arg[2] = true
            return
        end
        ngx.log(ngx.WARN, "Anonymized response body: ", tostring(an_res_body))
        ngx.arg[1] = an_res_body
        ngx.arg[2] = true
        return
    end
    ngx.log(ngx.WARN, "Response is allowed to pass through aigateway")
    ngx.arg[1] = response_body
    ngx.arg[2] = true
    return
end

-- Function to be called during the log phase
function _M.log(conf, ctx)
    -- Clean up the stored response body after processing
    response_bodies[ctx] = nil
end

-- Return the plugin so it can be used by APISIX
return _M
