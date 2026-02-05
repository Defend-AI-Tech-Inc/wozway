-- Semantic policy enforcement plugin for wozway
-- Integrates with AI detection service for advanced threat detection
local core = require("apisix.core")
local http = require("resty.http")
local cjson = require("cjson.safe")

local plugin_name = "semantic_policy"

local _M = {
    version = 1.0,
    priority = 1003,  -- Higher than local_policy (1002)
    name = plugin_name,
    schema = {
        type = "object",
        properties = {
            enabled = {
                type = "boolean",
                default = true
            },
            ai_service_url = {
                type = "string",
                default = "http://ai-detector:8000"
            },
            detection_types = {
                type = "array",
                items = {
                    type = "string",
                    enum = {"pii", "prompt_injection", "toxicity"}
                },
                default = {"pii", "prompt_injection"}
            },
            threshold = {
                type = "number",
                default = 0.7,
                minimum = 0,
                maximum = 1
            },
            timeout_ms = {
                type = "integer",
                default = 200
            },
            fallback_on_error = {
                type = "boolean",
                default = true,
                description = "Allow request if AI service fails"
            },
            use_tiered_detection = {
                type = "boolean",
                default = true,
                description = "Use fast regex first, AI only for uncertain cases"
            }
        }
    }
}

function _M.check_schema(conf)
    return true
end

-- Fast heuristic checks to avoid AI calls for obvious cases
local function quick_heuristic_check(text)
    if not text or #text < 10 then
        return {suspicious = false, score = 0}
    end
    
    local score = 0
    local reasons = {}
    
    -- Check for common injection keywords
    local injection_keywords = {
        "ignore", "disregard", "forget", "override",
        "system:", "assistant:", "user:",
        "jailbreak", "DAN mode", "pretend"
    }
    
    for _, keyword in ipairs(injection_keywords) do
        if string.find(string.lower(text), keyword, 1, true) then
            score = score + 0.3
            table.insert(reasons, "injection_keyword:" .. keyword)
        end
    end
    
    -- Check for excessive special characters (possible obfuscation)
    local special_char_count = select(2, string.gsub(text, "[^%w%s]", ""))
    if special_char_count > #text * 0.3 then
        score = score + 0.2
        table.insert(reasons, "high_special_chars")
    end
    
    -- Check for number patterns (possible PII)
    local number_groups = select(2, string.gsub(text, "%d+", ""))
    if number_groups >= 3 then
        score = score + 0.2
        table.insert(reasons, "multiple_number_groups")
    end
    
    return {
        suspicious = score > 0.3,
        score = math.min(score, 1.0),
        reasons = reasons
    }
end

-- Call AI detection service
local function call_ai_detector(text, conf)
    local httpc = http.new()
    httpc:set_timeout(conf.timeout_ms)
    
    local request_body = {
        text = text,
        checks = conf.detection_types,
        threshold = conf.threshold
    }
    
    core.log.info("Calling AI detector for semantic analysis")
    
    local res, err = httpc:request_uri(conf.ai_service_url .. "/analyze", {
        method = "POST",
        body = cjson.encode(request_body),
        headers = {
            ["Content-Type"] = "application/json",
        }
    })
    
    if not res then
        core.log.error("AI detector request failed: ", err)
        return nil, err
    end
    
    if res.status ~= 200 then
        core.log.error("AI detector returned status: ", res.status)
        return nil, "non-200 status"
    end
    
    local result, decode_err = cjson.decode(res.body)
    if not result then
        core.log.error("Failed to decode AI detector response: ", decode_err)
        return nil, decode_err
    end
    
    core.log.info("AI detector processing time: ", result.processing_time_ms, "ms")
    
    return result, nil
end

-- Extract prompt from request body
local function get_prompt_from_body(body)
    if not body then
        return nil
    end
    
    local ok, data = pcall(cjson.decode, body)
    if not ok then
        return nil
    end
    
    -- Check for direct prompt field
    if data.prompt then
        return data.prompt
    end
    
    -- Check for messages array (chat format)
    if data.messages and type(data.messages) == "table" then
        local prompts = {}
        for _, msg in ipairs(data.messages) do
            if msg.content then
                table.insert(prompts, msg.content)
            end
        end
        return table.concat(prompts, " ")
    end
    
    return nil
end

-- Main access function
function _M.access(conf, ctx)
    if not conf.enabled then
        return
    end
    
    -- Only check POST requests
    if ngx.req.get_method() ~= "POST" then
        return
    end
    
    -- Get request body
    local body, err = core.request.get_body()
    if not body then
        core.log.warn("Failed to get request body: ", err)
        return
    end
    
    -- Extract prompt
    local prompt = get_prompt_from_body(body)
    if not prompt then
        core.log.warn("No prompt found in request body")
        return
    end
    
    core.log.info("Semantic policy check for prompt (", #prompt, " chars)")
    
    -- Tiered detection approach
    if conf.use_tiered_detection then
        -- Quick heuristic check first
        local heuristic = quick_heuristic_check(prompt)
        
        if not heuristic.suspicious then
            core.log.info("Heuristic check passed, skipping AI analysis")
            return
        end
        
        core.log.info("Heuristic suspicious (score: ", heuristic.score, "), calling AI detector")
    end
    
    -- Call AI detection service
    local ai_result, ai_err = call_ai_detector(prompt, conf)
    
    if ai_err then
        if conf.fallback_on_error then
            core.log.warn("AI detector failed, allowing request (fallback mode)")
            return
        else
            core.log.error("AI detector failed, blocking request (strict mode)")
            ngx.status = ngx.HTTP_SERVICE_UNAVAILABLE
            ngx.header["Content-Type"] = "application/json"
            ngx.say(cjson.encode({
                error = "Security check unavailable",
                message = "Unable to verify request safety"
            }))
            return ngx.exit(ngx.HTTP_SERVICE_UNAVAILABLE)
        end
    end
    
    -- Check for violations
    if ai_result.violation and #ai_result.violations > 0 then
        -- Log all violations
        for _, violation in ipairs(ai_result.violations) do
            core.log.error("SEMANTIC VIOLATION: ", violation.type, 
                          " (confidence: ", violation.confidence, ")")
        end
        
        -- Build response
        local violation_types = {}
        local explanations = {}
        for _, v in ipairs(ai_result.violations) do
            table.insert(violation_types, v.type)
            table.insert(explanations, v.explanation)
        end
        
        -- Log to dashboard
        local log_body = cjson.encode({
            timestamp = ngx.now(),
            method = ngx.req.get_method(),
            uri = ngx.var.uri,
            status = "blocked",
            reason = table.concat(violation_types, ", "),
            policy_type = "semantic_policy",
            client_ip = ngx.var.remote_addr
        })
        
        -- Send async log to dashboard (fire and forget)
        ngx.timer.at(0, function()
            local httpc = http.new()
            httpc:set_timeout(1000)
            httpc:request_uri("http://dashboard:8080/api/activity/log", {
                method = "POST",
                body = log_body,
                headers = {["Content-Type"] = "application/json"}
            })
        end)
        
        local message = {
            error = "Request blocked by wozway semantic policy",
            reason = "AI-detected security violation",
            violations = violation_types,
            explanations = explanations,
            message = "Your request was flagged by our AI security system. Violations: " .. 
                     table.concat(violation_types, ", ")
        }
        
        ngx.status = ngx.HTTP_FORBIDDEN
        ngx.header["Content-Type"] = "application/json"
        ngx.say(cjson.encode(message))
        return ngx.exit(ngx.HTTP_FORBIDDEN)
    else
        core.log.info("Semantic policy check passed")
    end
end

return _M
