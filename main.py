import hashlib

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request

EMAIL = "24f1001102@ds.study.iitm.ac.in"

mcp = FastMCP(
    "Exam Challenge Server",
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def solve_challenge() -> str:
    """Calculate the response using the current HTTP request's challenge header."""
    request = mcp.get_context().request_context.request

    challenge = request.headers.get("x-exam-challenge")

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL}"
    return hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]


app = mcp.streamable_http_app()