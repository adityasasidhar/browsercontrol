"""Session recording tools for browser control."""

import logging
import os
from pathlib import Path
from datetime import datetime

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from browsercontrol.browser import browser
from browsercontrol.config import config

logger = logging.getLogger(__name__)

# Recording state
_recording_path: Path | None = None
_recording_active: bool = False


def register_recording_tools(mcp: FastMCP) -> None:
    """Register session recording tools with the MCP server."""
    
    @mcp.tool()
    async def start_recording(name: str = "") -> tuple[str, Image]:
        """
        Start recording the browser session as a video.
        The video will be saved when stop_recording is called.
        
        Args:
            name: Optional name for the recording (default: timestamp)
            
        Returns:
            Status message and screenshot
        """
        global _recording_path, _recording_active
        
        try:
            await browser.ensure_started()
            
            if _recording_active:
                screenshot_bytes, elem_map = await browser.screenshot_with_som()
                image = Image(data=screenshot_bytes, format="png")
                return "Recording already in progress. Call stop_recording() first.", image
            
            # Create recordings directory
            recordings_dir = config.user_data_dir.parent / "recordings"
            recordings_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            if not name:
                name = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            _recording_path = recordings_dir / f"{name}.webm"
            
            # Start video recording via CDP
            cdp = await browser.page.context.new_cdp_session(browser.page)
            await cdp.send("Page.startScreencast", {
                "format": "png",
                "quality": 80,
                "everyNthFrame": 2
            })
            
            _recording_active = True
            logger.info(f"Started recording: {_recording_path}")
            
            screenshot_bytes, elem_map = await browser.screenshot_with_som()
            image = Image(data=screenshot_bytes, format="png")
            return f"🔴 Recording started: {_recording_path.name}\n\nCall stop_recording() when done.", image
            
        except Exception as e:
            logger.error(f"Start recording failed: {e}")
            # Fallback: use Playwright's built-in tracing
            try:
                await browser.page.context.tracing.start(screenshots=True, snapshots=True)
                _recording_active = True
                
                screenshot_bytes, elem_map = await browser.screenshot_with_som()
                image = Image(data=screenshot_bytes, format="png")
                return f"🔴 Recording started (trace mode)\n\nCall stop_recording() when done.", image
            except Exception as e2:
                raise RuntimeError(f"Failed to start recording: {e2}")
    
    @mcp.tool()
    async def stop_recording() -> tuple[str, Image]:
        """
        Stop recording and save the session.
        
        Returns:
            Path to saved recording and screenshot
        """
        global _recording_path, _recording_active
        
        try:
            await browser.ensure_started()
            
            if not _recording_active:
                screenshot_bytes, elem_map = await browser.screenshot_with_som()
                image = Image(data=screenshot_bytes, format="png")
                return "No recording in progress. Call start_recording() first.", image
            
            # Stop tracing and save
            recordings_dir = config.user_data_dir.parent / "recordings"
            recordings_dir.mkdir(parents=True, exist_ok=True)
            
            if _recording_path is None:
                _recording_path = recordings_dir / f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            trace_path = _recording_path.with_suffix(".zip")
            
            try:
                await browser.page.context.tracing.stop(path=str(trace_path))
                logger.info(f"Recording saved: {trace_path}")
                result_path = trace_path
            except Exception:
                # If tracing wasn't active, just note it
                result_path = _recording_path
            
            _recording_active = False
            _recording_path = None
            
            screenshot_bytes, elem_map = await browser.screenshot_with_som()
            image = Image(data=screenshot_bytes, format="png")
            return f"⏹️ Recording saved: {result_path}\n\nView with: npx playwright show-trace {result_path}", image
            
        except Exception as e:
            _recording_active = False
            logger.error(f"Stop recording failed: {e}")
            raise RuntimeError(f"Failed to stop recording: {e}")
    
    @mcp.tool()
    async def take_snapshot(name: str = "") -> tuple[str, Image]:
        """
        Take a named snapshot (screenshot + HTML) for later reference.
        
        Args:
            name: Optional name for the snapshot (default: timestamp)
            
        Returns:
            Path to saved snapshot and screenshot
        """
        try:
            await browser.ensure_started()
            
            # Create snapshots directory
            snapshots_dir = config.user_data_dir.parent / "snapshots"
            snapshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            if not name:
                name = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save screenshot
            screenshot_path = snapshots_dir / f"{name}.png"
            await browser.page.screenshot(path=str(screenshot_path))
            
            # Save HTML
            html_path = snapshots_dir / f"{name}.html"
            html_content = await browser.page.content()
            html_path.write_text(html_content)
            
            # Save URL
            url_path = snapshots_dir / f"{name}.url"
            url_path.write_text(browser.page.url)
            
            logger.info(f"Snapshot saved: {screenshot_path}")
            
            screenshot_bytes, elem_map = await browser.screenshot_with_som()
            image = Image(data=screenshot_bytes, format="png")
            return f"📸 Snapshot saved:\n  - {screenshot_path.name}\n  - {html_path.name}\n  - {url_path.name}", image
            
        except Exception as e:
            logger.error(f"Take snapshot failed: {e}")
            raise RuntimeError(f"Failed to take snapshot: {e}")
    
    @mcp.tool()
    async def list_recordings() -> tuple[str, Image]:
        """
        List all saved recordings and snapshots.
        
        Returns:
            List of recordings and screenshot
        """
        try:
            await browser.ensure_started()
            
            base_dir = config.user_data_dir.parent
            recordings_dir = base_dir / "recordings"
            snapshots_dir = base_dir / "snapshots"
            
            lines = ["📁 Saved Sessions:\n"]
            
            # List recordings
            if recordings_dir.exists():
                recordings = list(recordings_dir.glob("*"))
                if recordings:
                    lines.append("Recordings:")
                    for r in sorted(recordings)[-10:]:  # Last 10
                        size = r.stat().st_size // 1024
                        lines.append(f"  📹 {r.name} ({size}KB)")
            
            # List snapshots
            if snapshots_dir.exists():
                snapshots = list(snapshots_dir.glob("*.png"))
                if snapshots:
                    lines.append("\nSnapshots:")
                    for s in sorted(snapshots)[-10:]:  # Last 10
                        lines.append(f"  📸 {s.stem}")
            
            if len(lines) == 1:
                lines.append("No recordings or snapshots found.")
            
            screenshot_bytes, elem_map = await browser.screenshot_with_som()
            image = Image(data=screenshot_bytes, format="png")
            return "\n".join(lines), image
            
        except Exception as e:
            logger.error(f"List recordings failed: {e}")
            raise RuntimeError(f"Failed to list recordings: {e}")
    
    logger.debug("Registered recording tools")
