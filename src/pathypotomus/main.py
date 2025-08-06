"""Main application entry point for Pathypotomus."""
import argparse
import logging
import sys
from pathlib import Path

from .config import load_config


def setup_logging(log_level: str, enable_debug: bool = False) -> None:
    """
    Set up application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_debug: Whether to enable debug mode with detailed formatting
    """
    level = getattr(logging, log_level.upper())
    
    if enable_debug:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    else:
        format_string = "%(asctime)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Pathypotomus - LLM-Powered Route Planner"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (.env format)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Pathypotomus 1.0.0-dev"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(env_file=args.config)
        
        # Set up logging
        setup_logging(config.log_level, config.enable_debug_mode)
        logger = logging.getLogger(__name__)
        
        logger.info("Starting Pathypotomus Route Planner")
        logger.info(f"Origin: {config.origin_addr}")
        logger.info(f"Destination: {config.dest_addr}")
        logger.info(f"OSRM URL: {config.osrm_url}")
        logger.info(f"Output path: {config.output_path}")
        
        # TODO: Implement main application logic
        # 1. Geocode addresses to coordinates
        # 2. Query OSRM for route alternatives
        # 3. Generate AI descriptions for routes
        # 4. Create HTML visualization
        
        logger.info("Application setup complete - ready for implementation")
        return 0
        
    except Exception as e:
        # Set up basic logging for error reporting
        logging.basicConfig(level=logging.ERROR)
        logger = logging.getLogger(__name__)
        
        logger.error(f"Application failed to start: {e}")
        if "--debug" in sys.argv or "-v" in sys.argv:
            logger.exception("Full error details:")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())