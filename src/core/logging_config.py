import logging
import sentry_sdk
import os
from dotenv import load_dotenv

load_dotenv()


def setup_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
    )
    return logging.getLogger(name)
