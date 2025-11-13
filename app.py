"""
Application runner for NexusAutoDL.
"""
from __future__ import annotations

from loguru import logger

from models import AppConfig, Monitor
from utils.platform import IS_WINDOWS


def run(config: AppConfig, simulate: bool) -> None:
    """
    Build and run the appropriate scanner (real vs simulation).

    Args:
        config: Application configuration
        simulate: Force simulation mode even on Windows
    """
    run_in_simulation: bool = simulate or not IS_WINDOWS

    if run_in_simulation:
        from utils.simulator import SimulatedScanner as Scanner, get_simulated_monitors

        monitors: list[Monitor] = get_simulated_monitors()
        logger.warning("⚠️  SIMULATION MODE - No actual clicking will occur")
        logger.info(f"📺 Simulating {len(monitors)} monitor(s)")
        scanner = Scanner(config)
    else:
        from services.window_manager import WindowManager
        from services.scanner import Scanner

        monitors: list[Monitor] = WindowManager.get_all_monitors()
        logger.info(f"📺 Detected {len(monitors)} monitor(s)")
        scanner = Scanner(config, monitors)

    logger.info("🔍 Starting scan loop... (Ctrl+C to stop)")
    logger.info("-" * 60)

    try:
        scanner.scan_loop()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("⏹️  Scan stopped by user")
        logger.success("✅ Total clicks: {}", scanner.status.clicks_count)
    except Exception as exc:
        logger.exception("❌ Scanner error: {}", exc)
        raise
