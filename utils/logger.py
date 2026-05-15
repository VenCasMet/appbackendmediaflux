import logging
import time
from pathlib import Path

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"compression_{int(time.time())}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)