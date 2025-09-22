# src/utils/logging_config.py

import logging

def setup_logging():
    """Sets up a basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )