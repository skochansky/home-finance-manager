from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Dict, Any
import logging

# Service URLs
SERVICE_URLS = {
    "transactions": os.getenv("TRANSACTION_SERVICE_URL", "http://localhost:8001"),
    "accounts": os.getenv("ACCOUNT_SERVICE_URL", "http://localhost:8002"),
    "notifications": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8003"),
    "budget": os.getenv("BUDGET_SERVICE_URL", "http://localhost:8004"),
}

app = FastAPI(title="HFM API Gateway", version="0.1.0", description="API Gateway for Home Finance Manager")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def proxy_request(service_url: str, path: str, method: str, request: Request) -> Dict[Any, Any]:
    """Proxy requests to microservices"""
    url = f"{service_url}{path}"
    headers = dict(request.headers)
    
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=dict(request.query_params))
            elif method == "POST":
                body = await request.body()
                response = await client.post(url, headers=headers, content=body)
            elif method == "PUT":
                body = await request.body()
                response = await client.put(url, headers=headers, content=body)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return {
                "status_code": response.status_code,
                "content": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

@app.get("/")
def read_root():
    return {
        "service": "HFM API Gateway",
        "version": "0.1.0",
        "status": "running",
        "services": {
            "transactions": f"{SERVICE_URLS['transactions']}/health",
            "accounts": f"{SERVICE_URLS['accounts']}/health",
            "notifications": f"{SERVICE_URLS['notifications']}/health",
            "budget": f"{SERVICE_URLS['budget']}/health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "gateway": "operational"}

# Transaction Service Routes
@app.api_route("/api/v1/transactions/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def transactions_proxy(path: str, request: Request):
    result = await proxy_request(SERVICE_URLS["transactions"], f"/{path}", request.method, request)
    return result["content"]

# Account Management Service Routes
@app.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/v1/accounts/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def accounts_proxy(path: str, request: Request):
    full_path = f"/{request.url.path.split('/')[-2]}/{path}"
    result = await proxy_request(SERVICE_URLS["accounts"], full_path, request.method, request)
    return result["content"]

# Notification Service Routes
@app.api_route("/api/v1/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/v1/preferences/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def notifications_proxy(path: str, request: Request):
    full_path = f"/{request.url.path.split('/')[-2]}/{path}"
    result = await proxy_request(SERVICE_URLS["notifications"], full_path, request.method, request)
    return result["content"]

# Budget Analysis Service Routes
@app.api_route("/api/v1/budgets/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/api/v1/insights/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def budget_proxy(path: str, request: Request):
    full_path = f"/{request.url.path.split('/')[-2]}/{path}"
    result = await proxy_request(SERVICE_URLS["budget"], full_path, request.method, request)
    return result["content"]

# Authentication endpoints (proxy to account service)
@app.post("/api/v1/auth/register")
async def register(request: Request):
    result = await proxy_request(SERVICE_URLS["accounts"], "/users/register", "POST", request)
    return result["content"]

@app.post("/api/v1/auth/login")
async def login(request: Request):
    result = await proxy_request(SERVICE_URLS["accounts"], "/users/login", "POST", request)
    return result["content"]

@app.get("/api/v1/auth/me")
async def get_current_user(request: Request):
    result = await proxy_request(SERVICE_URLS["accounts"], "/users/me", "GET", request)
    return result["content"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
