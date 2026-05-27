"""
Wozway Dashboard - Web UI for Policy Management
Real-time monitoring and policy configuration
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import os
from datetime import datetime
import re
from collections import deque

app = FastAPI(title="Wozway Dashboard")

# Configuration
APISIX_ADMIN_URL = os.getenv("APISIX_ADMIN_URL", "http://wauzeway:9180")
APISIX_API_KEY = os.getenv("APISIX_API_KEY")
if not APISIX_API_KEY:
    raise RuntimeError("APISIX_API_KEY environment variable is required")

templates = Jinja2Templates(directory="templates")

# In-memory storage for activity (last 100 requests)
activity_log = deque(maxlen=100)

# Models
class PolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    plugin_type: str  # "local_policy" or "semantic_policy"
    enabled: bool = True
    priority: int = 10
    uri: str = "/openai/v1/chat/completions"
    config: Dict[str, Any] = {}

class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

# Helper functions
async def get_apisix_routes():
    """Fetch all routes from APISIX"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{APISIX_ADMIN_URL}/apisix/admin/routes",
            headers={"X-API-KEY": APISIX_API_KEY}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("list", [])
        return []

async def get_apisix_route(route_id: str):
    """Fetch specific route from APISIX"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{APISIX_ADMIN_URL}/apisix/admin/routes/{route_id}",
            headers={"X-API-KEY": APISIX_API_KEY}
        )
        if response.status_code == 200:
            return response.json()
        return None

async def create_apisix_route(route_id: str, route_config: dict):
    """Create or update route in APISIX"""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{APISIX_ADMIN_URL}/apisix/admin/routes/{route_id}",
            headers={"X-API-KEY": APISIX_API_KEY},
            json=route_config
        )
        return response.status_code == 200 or response.status_code == 201

async def delete_apisix_route(route_id: str):
    """Delete route from APISIX"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{APISIX_ADMIN_URL}/apisix/admin/routes/{route_id}",
            headers={"X-API-KEY": APISIX_API_KEY}
        )
        return response.status_code == 200

# Dashboard Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    routes = await get_apisix_routes()
    
    # Extract policy information
    policies = []
    for route in routes:
        route_value = route.get("value", {})
        plugins = route_value.get("plugins", {})
        
        policy_info = {
            "id": route.get("key", "").split("/")[-1],
            "name": route_value.get("name", "Unnamed"),
            "uri": route_value.get("uri", ""),
            "enabled": True,
            "plugins": []
        }
        
        # Check for policy plugins
        if "local_policy" in plugins:
            policy_info["plugins"].append({
                "type": "local_policy",
                "config": plugins["local_policy"]
            })
        
        if "semantic_policy" in plugins:
            policy_info["plugins"].append({
                "type": "semantic_policy",
                "config": plugins["semantic_policy"]
            })
        
        policies.append(policy_info)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "policies": policies,
        "total_policies": len(policies),
        "active_policies": len([p for p in policies if p["enabled"]])
    })

@app.get("/api/policies")
async def list_policies():
    """API endpoint to list all policies"""
    routes = await get_apisix_routes()
    
    policies = []
    for route in routes:
        route_value = route.get("value", {})
        plugins = route_value.get("plugins", {})
        
        # Only include routes with policy plugins
        if "local_policy" in plugins or "semantic_policy" in plugins:
            policies.append({
                "id": route.get("key", "").split("/")[-1],
                "name": route_value.get("name", "Unnamed"),
                "uri": route_value.get("uri", ""),
                "priority": route_value.get("priority", 0),
                "plugins": plugins,
                "upstream": route_value.get("upstream", {})
            })
    
    return {"policies": policies, "count": len(policies)}

@app.get("/api/policies/{policy_id}")
async def get_policy(policy_id: str):
    """Get specific policy details"""
    route = await get_apisix_route(policy_id)
    if not route:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return route

@app.post("/api/policies")
async def create_policy(policy: PolicyCreate):
    """Create a new policy"""
    route_id = policy.name.lower().replace(" ", "-")
    
    # Build plugin configuration
    plugins = {}
    if policy.plugin_type == "local_policy":
        plugins["local_policy"] = {
            "enabled": policy.enabled,
            "block_on_match": policy.config.get("block_on_match", True)
        }
    elif policy.plugin_type == "semantic_policy":
        plugins["semantic_policy"] = {
            "enabled": policy.enabled,
            "detection_types": policy.config.get("detection_types", ["pii", "prompt_injection"]),
            "threshold": policy.config.get("threshold", 0.7),
            "use_tiered_detection": policy.config.get("use_tiered_detection", True)
        }
    
    # Build route configuration
    route_config = {
        "name": policy.name,
        "desc": policy.description or "",
        "uri": policy.uri,
        "priority": policy.priority,
        "plugins": plugins,
        "upstream": {
            "type": "roundrobin",
            "scheme": "https",
            "nodes": {
                "api.groq.com:443": 1
            }
        }
    }
    
    success = await create_apisix_route(route_id, route_config)
    
    if success:
        return {"message": "Policy created successfully", "id": route_id}
    else:
        raise HTTPException(status_code=500, detail="Failed to create policy")

@app.put("/api/policies/{policy_id}")
async def update_policy(policy_id: str, policy: PolicyUpdate):
    """Update existing policy"""
    # Get current route
    current_route = await get_apisix_route(policy_id)
    if not current_route:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    route_value = current_route.get("value", {})
    
    # Update fields
    if policy.name:
        route_value["name"] = policy.name
    if policy.enabled is not None:
        # Update plugin enabled status
        for plugin_name in ["local_policy", "semantic_policy"]:
            if plugin_name in route_value.get("plugins", {}):
                route_value["plugins"][plugin_name]["enabled"] = policy.enabled
    if policy.config:
        # Merge config
        for plugin_name in ["local_policy", "semantic_policy"]:
            if plugin_name in route_value.get("plugins", {}):
                route_value["plugins"][plugin_name].update(policy.config)
    
    success = await create_apisix_route(policy_id, route_value)
    
    if success:
        return {"message": "Policy updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update policy")

@app.delete("/api/policies/{policy_id}")
async def delete_policy(policy_id: str):
    """Delete a policy"""
    success = await delete_apisix_route(policy_id)
    
    if success:
        return {"message": "Policy deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Policy not found")

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    routes = await get_apisix_routes()
    
    total_routes = len(routes)
    policy_routes = 0
    
    for route in routes:
        plugins = route.get("value", {}).get("plugins", {})
        if "local_policy" in plugins or "semantic_policy" in plugins:
            policy_routes += 1
    
    blocked_count = len([a for a in activity_log if a.get("status") == "blocked"])
    
    return {
        "total_routes": total_routes,
        "policy_routes": policy_routes,
        "total_requests": len(activity_log),
        "blocked_requests": blocked_count,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/activity")
async def get_activity():
    """Get all activity (blocked and allowed requests)"""
    return {
        "activity": list(reversed(activity_log)),  # Most recent first
        "count": len(activity_log)
    }

@app.post("/api/activity/log")
async def log_activity(request: Request):
    """Log a request activity (called by external systems or manually)"""
    data = await request.json()
    
    activity_log.append({
        "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
        "method": data.get("method", "POST"),
        "uri": data.get("uri", "/openai/v1/chat/completions"),
        "status": data.get("status", "allowed"),  # "allowed" or "blocked"
        "reason": data.get("reason", ""),
        "policy_type": data.get("policy_type", ""),
        "client_ip": data.get("client_ip", "")
    })
    
    return {"message": "Activity logged"}

@app.post("/api/activity/test")
async def test_activity():
    """Add test activity for demonstration"""
    # Add some test blocked requests
    test_activities = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "method": "POST",
            "uri": "/openai/v1/chat/completions",
            "status": "blocked",
            "reason": "Social Security Number detected",
            "policy_type": "local_policy",
            "client_ip": "172.18.0.8"
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "method": "POST",
            "uri": "/openai/v1/chat/completions",
            "status": "allowed",
            "reason": "",
            "policy_type": "",
            "client_ip": "172.18.0.8"
        }
    ]
    
    for activity in test_activities:
        activity_log.append(activity)
    
    return {"message": "Test activity added", "count": len(test_activities)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
