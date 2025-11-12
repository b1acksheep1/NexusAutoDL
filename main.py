#!/usr/bin/env python3
"""
NexusAutoDL - Automated Nexusmods downloader.
"""
from __future__ import annotations

import sys
from typing import Optional

import click
from loguru import logger

from app import run as run_app
from models import AppConfig, BrowserType
from utils.platform import IS_WINDOWS


def setup_logging(verbose: bool) -> None:
    """
    Configure loguru logging.

    Args:
        verbose: Enable verbose logging
    """
    # Remove default handler
    logger.remove()
    
    # Add file handler
    logger.add(
        "nexus_autodl.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG" if verbose else "INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )
    
    # Add console handler with nice formatting
    if verbose:
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
    else:
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            colorize=True
        )


@click.command()
@click.option(
    '--browser',
    type=click.Choice(['chrome', 'firefox'], case_sensitive=False),
    default=None,
    help='Browser to launch and position (requires --vortex)'
)
@click.option(
    '--vortex',
    is_flag=True,
    default=False,
    help='Enable Vortex mod manager mode'
)
@click.option(
    '--legacy',
    is_flag=True,
    default=False,
    help='Use legacy button assets and dialogs'
)
@click.option(
    '--verbose',
    is_flag=True,
    default=False,
    help='Enable verbose logging'
)
@click.option(
    '--force-primary',
    is_flag=True,
    default=False,
    help='Force scanning on primary monitor only'
)
@click.option(
    '--window-title',
    type=str,
    default=None,
    help='Position window by title substring (e.g., "Wabbajack")'
)

@click.option(
    '--min-matches',
    type=int,
    default=8,
    help='Minimum SIFT matches for detection (default: 8)'
)
@click.option(
    '--ratio',
    type=float,
    default=0.75,
    help='Lowe ratio test threshold (default: 0.75)'
)
@click.option(
    '--click-delay',
    type=float,
    default=2.0,
    help='Delay between scan iterations in seconds (default: 2.0)'
)
@click.option(
    '--simulate',
    is_flag=True,
    default=False,
    help='Run in simulation mode (no Windows required, generates fake data)'
)
@click.option(
    '--debug-frame-dir',
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
    default=None,
    help='Directory to store annotated debug screenshots (optional)'
)
def main(
    browser: Optional[str],
    vortex: bool,
    legacy: bool,
    verbose: bool,
    force_primary: bool,
    window_title: Optional[str],
    min_matches: int,
    ratio: float,
    click_delay: float,
    simulate: bool,
    debug_frame_dir: Optional[str],
) -> None:
    """
    NexusAutoDL - Automated Nexusmods downloader.
    
    Automatically detects and clicks download buttons on Nexusmods.
    Works with Vortex, Wabbajack, and other mod managers.
    
    Use --simulate to test without Windows or actual button detection.
    """
    # Setup logging first
    setup_logging(verbose)
    
    # Validate arguments
    effective_simulation = simulate or not IS_WINDOWS
    host_supports_windows_features = IS_WINDOWS or simulate
    if browser and not vortex and not effective_simulation:
        raise click.UsageError("--browser requires --vortex to be enabled")
    if vortex and not host_supports_windows_features:
        logger.warning(
            "Vortex mode requested, but this platform lacks native win32 APIs. "
            "Falling back to simulator."
        )
    
    # Create configuration
    config = AppConfig(
        browser=BrowserType(browser.lower()) if browser else None,
        vortex=vortex,
        verbose=verbose,
        legacy=legacy,
        debug_frame_dir=debug_frame_dir,
        force_primary=force_primary,
        window_title=window_title,
        min_matches=min_matches,
        ratio_threshold=ratio,
        click_delay=click_delay,
    )
    
    logger.debug(f"Configuration: {config}")
    
    # Run scanner
    logger.info("🚀 Starting NexusAutoDL")
    run_app(config, simulate=effective_simulation)


if __name__ == "__main__":
    main()
