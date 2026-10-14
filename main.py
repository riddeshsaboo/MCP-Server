import hashlib
from contextvars import ContextVar

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings


# Configuration
EMAIL = "24f1001102@ds.study.iitm.ac.in"

challenge_header = ContextVar("challenge_header", default=None)


# Middleware to capture the challenge header for each HTTP request
class HeaderCaptureMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        challenge = headers.get(b"x-exam-challenge")

        token = challenge_header.set(
            challenge.decode("ascii") if challenge else None
        )

        try:
            await self.app(scope, receive, send)
        finally:
            challenge_header.reset(token)


# Allow requests from the Render hostname
security = TransportSecuritySettings(
    allowed_hosts=[
        "mcp-server-n8dh.onrender.com",
        "mcp-server-n8dh.onrender.com:*",
    ]
)


# Initialize the MCP server
mcp = FastMCP(
    "Exam Challenge Server",
    stateless_http=True,
    json_response=True,
)


# MCP tool: solve the challenge
@mcp.tool()
def solve_challenge() -> str:
    """Return the first 16 hexadecimal characters of the challenge hash."""

    challenge = challenge_header.get()

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL}"

    return hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()[:16]


# Create the HTTP application
app = HeaderCaptureMiddleware(
    mcp.streamable_http_app(
        transport_security=security
    )
)