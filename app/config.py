# app/config.py
import logging
import os
import json
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.logging import LoggingIntegration
from dotenv import load_dotenv

load_dotenv()

SENTRY_DSN = os.getenv("SENTRY_DSN")  # Lägg till i .env

# Setup logging
def setup_logging():
    logger = logging.getLogger("merinfo_scraper")
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger

logger = setup_logging()

# Load selectors from selectors.json
selectors_config = {}
try:
    with open('app/selectors.json', 'r', encoding='utf-8') as f:
        selectors_config = json.load(f)
    logger.info("Selectors loaded successfully.")
except Exception as e:
    logger.error(f"Error loading selectors: {e}")

# Initialize Sentry
if SENTRY_DSN:
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    sentry_init(
        dsn=SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=1.0
    )
    logger.info("Sentry initialized.")
else:
    logger.warning("SENTRY_DSN not set. Sentry not initialized.")