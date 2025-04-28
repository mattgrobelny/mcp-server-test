"""
FastMCP Screenshot Example

Give Claude a tool to capture and view screenshots.
"""

import io

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image

# Create server
mcp = FastMCP("Screenshot Demo", dependencies=["pyautogui", "Pillow"])


import time
resource_registry = {}
import os
SCREENSHOT_SAVE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "FastMCPScreenshots")
@mcp.tool()
def list_resources() -> list:
    return [
        {"uri": uri, "mimeType": entry["mimeType"], "filepath": entry["filepath"]}
        for uri, entry in resource_registry.items()
    ]

@mcp.tool()
def get_resource(uri: str) -> dict:
    entry = resource_registry.get(uri)
    if not entry:
        raise Exception("Resource not found")
    # You might want to return data in the embedded resource MCP format
    return {
        "type": "resource",
        "resource": {
            "uri": uri,
            "mimeType": entry["mimeType"],
            "bytes": entry["bytes"]
        }
    }

@mcp.tool()
def take_screenshot() -> dict:
    import pyautogui
    import uuid
    import os

    buffer = io.BytesIO()
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    image_bytes = buffer.getvalue()

    filename = f"screenshot_{int(time.time())}_{uuid.uuid4().hex}.jpeg"
    filepath = os.path.join(SCREENSHOT_SAVE_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    # Register as a resource using an MCP-compliant URI
    resource_uri = f"resource://screenshot/{filename}"
    resource_registry[resource_uri] = {
        "filepath": filepath,
        "mimeType": "image/jpeg",
        "bytes": image_bytes,
    }
    return {
        "image": Image(data=image_bytes, format="jpeg"),
        "resource_uri": resource_uri
    }

@mcp.tool()
def view_screenshot(resource_uri: str) -> dict:
    entry = resource_registry.get(resource_uri)
    if not entry:
        raise Exception("Resource not found")
    return Image(data=entry["bytes"], format="jpeg")


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')