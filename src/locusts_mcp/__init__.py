"""Locusts MCP Server package."""

__version__ = "0.1.0"

def main() -> None:
    """Entry point for the locusts-mcp server."""
    from .server import main as server_main
    import asyncio
    asyncio.run(server_main())
