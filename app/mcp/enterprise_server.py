from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import uvicorn

from app.core.config import get_settings
from app.mcp.enterprise import EnterpriseMCPService

settings = get_settings()
mcp = FastMCP("enterprise-business", host=settings.mcp_host, port=settings.mcp_port)
service = EnterpriseMCPService()


@mcp.tool()
async def list_orders(tenant_id: str = "default", user_id: str = "demo-user", status: str | None = None):
    return await service.call_tool(
        "list_orders", {"status": status}, tenant_id=tenant_id, user_id=user_id
    )


@mcp.tool()
async def query_order(order_id: str, tenant_id: str = "default", user_id: str = "demo-user"):
    return await service.call_tool(
        "query_order", {"order_id": order_id}, tenant_id=tenant_id, user_id=user_id
    )


@mcp.tool()
async def query_logistics(order_id: str, tenant_id: str = "default", user_id: str = "demo-user"):
    return await service.call_tool(
        "query_logistics", {"order_id": order_id}, tenant_id=tenant_id, user_id=user_id
    )


@mcp.tool()
async def create_ticket(
    order_id: str,
    reason: str,
    approved: bool = False,
    tenant_id: str = "default",
    user_id: str = "demo-user",
):
    return await service.call_tool(
        "create_ticket",
        {"order_id": order_id, "reason": reason, "approved": approved},
        tenant_id=tenant_id,
        user_id=user_id,
    )


@mcp.resource("customer://profile/{user_id}")
async def customer_profile(user_id: str):
    return await service.read_resource(
        f"customer://profile/{user_id}", tenant_id="default", user_id=user_id
    )


@mcp.resource("order://history/{user_id}")
async def order_history(user_id: str):
    return await service.read_resource(
        f"order://history/{user_id}", tenant_id="default", user_id=user_id
    )


@mcp.resource("policy://company/customer-service")
async def company_policy():
    return await service.read_resource(
        "policy://company/customer-service", tenant_id="default", user_id="demo-user"
    )


@mcp.prompt()
async def customer_service_agent_prompt():
    result = await service.get_prompt("customer_service_agent_prompt")
    return result["data"]["template"]


if __name__ == "__main__":
    if settings.environment.lower() == "production" and not settings.mcp_auth_token:
        raise RuntimeError("MCP_AUTH_TOKEN must be configured in production")
    app = mcp.streamable_http_app()
    if settings.mcp_auth_token:
        class StaticTokenMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                if request.headers.get("authorization") != f"Bearer {settings.mcp_auth_token}":
                    return JSONResponse({"detail": "MCP authorization required"}, status_code=401)
                return await call_next(request)

        app.add_middleware(StaticTokenMiddleware)
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)
