import logging
import sys

class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "N/A"
        return True
    

def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - [CID: %(correlation_id)s] - %(levelname)s - %(message)s"
    )

    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter())

    if not logger.handlers:
        logger.addHandler(handler)

    return logger