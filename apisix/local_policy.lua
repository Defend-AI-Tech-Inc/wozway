-- Local policy enforcement plugin for wozway
-- Checks for sensitive data patterns without cloud dependency
local core = require("apisix.core")
local ngx = require("ngx")
local cjson = require("cjson.safe")

local plugin_name = "local_policy"

-- Define sensitive data patterns
local PATTERNS = {
    -- SSN patterns (XXX-XX-XXXX or XXXXXXXXX)
    ssn = {
        pattern = "%d%d%d%-?%d%d%-?%d%d%d%d",
        name = "Social Security Number",
        action = "BLOCK"
    },
    -- Credit card patterns (simplified)
    credit_card = {
        pattern = "%d%d%d%d[%s%-]?%d%d%d%d[%s%-]?%d%d%d%d[%s%-]?%d%d%d%d",
        name = "Credit Card Number",
        action = "BLOCK"
    },
    -- Email addresses
    email = {
        pattern = "[%w%._%%-]+@[%w%._%%-]+%.%w+",
        name = "Email Address",
        action = "ALERT"
    },
    -- Phone numbers (various formats)
    phone = {
        pattern = "%(?%d%d%d%)?[%s%-]?%d%d%d[%s%-]?%d%d%d%d",
        name = "Phone Number",
        action = "ALERT"
    },
    -- API keys (common patterns)
    api_key = {
        pattern = "['\"]?[aA][pP][iI]_?[kK][eE][yY]['\"]?%s*[:=]%s*['\"]?[%w%-_]+['\"]?",
        name = "API Key",
        action = "BLOCK"
    },
    -- AWS Access Keys
    aws_key = {
        pattern = "AKIA[0-9A-Z]{16}",
        name = "AWS Access Key",
        action = "BLOCK"
    },
    -- Private keys
    private_key = {
        pattern = "%-%-%-%-%-BEGIN[%s]+PRIVATE[%s]+KEY%-%-%-%-%-",
        name = "Private Key",
        action = "BLOCK"
    }
}

local _M = {
    version = 1.0,
    priority = 1002,  -- Higher priority than wauzeway_proxy
    name = plugin_name,
    schema = {
        type = "object",
        properties = {
            enabled = {
                type = "boolean",
                default = true
            },
            block_on_match = {
                type = "boolean",
                default = true
            }
        }
    }
}

function _M.check_schema(conf)
    return true
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

-- Check text against all patterns
local function check_patterns(text)
    if not text then
        return nil
    end
    
    local violations = {}
    
    for pattern_name, pattern_info in pairs(PATTERNS) do
        local match = string.match(text, pattern_info.pattern)
        if match then
            table.insert(violations, {
                type = pattern_name,
                name = pattern_info.name,
                action = pattern_info.action,
                matched = match
            })
            core.log.warn("Policy violation detected: ", pattern_info.name, " - ", match)
        end
    end
    
    return #violations > 0 and violations or nil
end

-- Main access function
function _M.access(conf, ctx)
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
    
    core.log.info("Checking prompt for policy violations: ", string.sub(prompt, 1, 100))
    
    -- Check for violations
    local violations = check_patterns(prompt)
    
    if violations then
        -- Log all violations
        for _, violation in ipairs(violations) do
            core.log.error("POLICY VIOLATION: ", violation.name, " detected in prompt")
        end
        
        -- Check if we should block
        local should_block = false
        for _, violation in ipairs(violations) do
            if violation.action == "BLOCK" then
                should_block = true
                break
            end
        end
        
        if should_block and (conf.block_on_match == nil or conf.block_on_match) then
            -- Build violation message
            local violation_types = {}
            for _, v in ipairs(violations) do
                table.insert(violation_types, v.name)
            end
            
            local message = {
                error = "Request blocked by wozway local policy",
                reason = "Sensitive data detected",
                violations = violation_types,
                message = "Your request contains sensitive information that is not allowed. Please remove: " .. table.concat(violation_types, ", ")
            }
            
            ngx.status = ngx.HTTP_FORBIDDEN
            ngx.header["Content-Type"] = "application/json"
            ngx.say(cjson.encode(message))
            return ngx.exit(ngx.HTTP_FORBIDDEN)
        else
            -- Just alert, don't block
            core.log.warn("ALERT: Sensitive data detected but not blocking")
        end
    else
        core.log.info("No policy violations detected")
    end
end

return _M
