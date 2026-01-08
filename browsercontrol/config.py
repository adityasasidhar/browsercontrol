"""
Configuration for Browser Control MCP server.

Settings can be configured via environment variables.
"""

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    """Browser control configuration."""
    
    # Browser settings
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000
    
    # Paths
    user_data_dir: Path = Path.home() / ".browsercontrol" / "user_data"
    extension_path: Path | None = None
    
    # Logging
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()
        
        # Browser settings
        if os.getenv("BROWSER_HEADLESS"):
            config.headless = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        
        if os.getenv("BROWSER_VIEWPORT_WIDTH"):
            config.viewport_width = int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1280"))
        
        if os.getenv("BROWSER_VIEWPORT_HEIGHT"):
            config.viewport_height = int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "720"))
        
        if os.getenv("BROWSER_TIMEOUT"):
            config.timeout_ms = int(os.getenv("BROWSER_TIMEOUT", "30000"))
        
        # Paths
        if os.getenv("BROWSER_USER_DATA_DIR"):
            config.user_data_dir = Path(os.getenv("BROWSER_USER_DATA_DIR"))
        
        if os.getenv("BROWSER_EXTENSION_PATH"):
            config.extension_path = Path(os.getenv("BROWSER_EXTENSION_PATH"))
        
        # Logging
        config.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        return config


# Global configuration instance
config = Config.from_env()
