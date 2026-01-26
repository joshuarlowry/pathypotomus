"""Main application entry point for Pathypotomus."""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

import aiohttp

from .config import load_config
from .services import GeocodingService, OSRMService, LLMService, MapRenderer


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


async def async_main(config, logger) -> int:
    """Async orchestration of services."""
    try:
        # 1. Geocode addresses
        logger.info("Geocoding addresses...")
        geocoder = GeocodingService()
        origin_coords = geocoder.geocode(config.origin_addr)
        dest_coords = geocoder.geocode(config.dest_addr)
        
        logger.info(f"Origin coordinates: {origin_coords}")
        logger.info(f"Destination coordinates: {dest_coords}")
        
        # 2. Query OSRM
        logger.info("Fetching routes from OSRM...")
        async with aiohttp.ClientSession() as session:
            osrm_service = OSRMService(base_url=config.osrm_url, session=session)
            routes = await osrm_service.get_routes(
                origin=origin_coords,
                destination=dest_coords,
                alternatives=True,
                max_alternatives=config.max_routes
            )
        
        logger.info(f"Found {len(routes)} routes")
        
        # 3. Generate AI descriptions
        logger.info("Generating AI descriptions...")
        llm_service = LLMService(
            api_key=config.llm_api_key,
            base_url=config.llm_base_url,
            model=config.llm_model,
            provider=config.llm_provider,
            cache_dir=config.cache_dir
        )
        
        processed_routes = []
        for route in routes:
            processed_routes.append(llm_service.generate_route_description(route))
            
        # 4. Create Visualization
        logger.info("Generating map visualization...")
        renderer = MapRenderer()
        output_file = renderer.render(
            origin=origin_coords,
            destination=dest_coords,
            routes=processed_routes,
            output_path=config.output_path,
            title=config.output_title
        )
        
        logger.info(f"Success! Map generated at: {output_file}")
        return 0

    except Exception as e:
        logger.exception(f"An error occurred during processing: {e}")
        return 1


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
        
        # Run async main loop
        return asyncio.run(async_main(config, logger))
        
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
