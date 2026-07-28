import logging
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

from browsercontrol.browser import browser
from browsercontrol.config import config

logger = logging.getLogger(__name__)

# Recording state
_recording_path: Path | None = None
_recording_active: bool = False


def register_recording_tools(mcp: FastMCP) -> None:
    """Register session recording tools with the MCP server."""

    @mcp.tool()
    async def start_recording(name: str = "") -> str:
        """
        Start recording the browser session as a Playwright trace.
        The trace will be saved when stop_recording is called.

        Args:
            name: Optional name for the recording (default: timestamp)

        Returns:
            Status message
        """
        global _recording_path, _recording_active

        await browser.ensure_started()

        if _recording_active:
            return "Recording already in progress. Call stop_recording() first."

        # Create recordings directory
        recordings_dir = config.recordings_dir
        recordings_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")

        _recording_path = recordings_dir / f"{name}.zip"

        # Start tracing on the context
        await browser.page.context.tracing.start(screenshots=True, snapshots=True, sources=True)

        _recording_active = True
        logger.info(f"Started recording: {_recording_path}")

        return f"Recording started: {_recording_path.name}\nCall stop_recording() when done."

    @mcp.tool()
    async def stop_recording() -> str:
        """
        Stop recording and save the session trace.

        Returns:
            Path to saved recording
        """
        global _recording_path, _recording_active

        await browser.ensure_started()

        if not _recording_active:
            return "No recording in progress. Call start_recording() first."

        await browser.page.context.tracing.stop(path=str(_recording_path))
        result_path = _recording_path

        _recording_active = False
        _recording_path = None

        logger.info(f"Recording saved: {result_path}")

        return f"Recording saved: {result_path}\nView with: npx playwright show-trace {result_path}"

    @mcp.tool()
    async def take_snapshot(name: str = "") -> str:
        """
        Take a named snapshot (screenshot + HTML) for later reference.

        Args:
            name: Optional name for the snapshot (default: timestamp)

        Returns:
            Paths to saved snapshot files
        """
        try:
            await browser.ensure_started()

            # Create snapshots directory
            snapshots_dir = config.snapshots_dir
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

            return (
                f"Snapshot saved:\n"
                f"  - {screenshot_path.name}\n"
                f"  - {html_path.name}\n"
                f"  - {url_path.name}"
            )

        except Exception as e:
            logger.error(f"Take snapshot failed: {e}")
            raise RuntimeError(f"Failed to take snapshot: {e}")

    @mcp.tool()
    async def list_recordings() -> str:
        """
        List all saved recordings and snapshots.

        Returns:
            List of recordings
        """
        recordings_dir = config.recordings_dir
        snapshots_dir = config.snapshots_dir

        lines = ["Saved Sessions:\n"]

        # List recordings
        if recordings_dir.exists():
            recordings = list(recordings_dir.glob("*"))
            if recordings:
                lines.append("Recordings:")
                for r in sorted(recordings)[-10:]:  # Last 10
                    size = r.stat().st_size // 1024
                    lines.append(f"  {r.name} ({size}KB)")

        # List snapshots
        if snapshots_dir.exists():
            snapshots = list(snapshots_dir.glob("*.png"))
            if snapshots:
                lines.append("\nSnapshots:")
                for s in sorted(snapshots)[-10:]:  # Last 10
                    lines.append(f"  {s.stem}")

        if len(lines) == 1:
            lines.append("No recordings or snapshots found.")

        return "\n".join(lines)

    logger.debug("Registered recording tools")
