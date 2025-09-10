"""
Startup script for Nexora AI Agent API server.
Runs the FastAPI application with all services.
"""

import uvicorn
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nexora_api.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Run the Nexora AI Agent API server."""
    logger.info("Starting Nexora AI Agent API server...")
    
    try:
        # Run the FastAPI application
        uvicorn.run(
            "src.api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload for development
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
