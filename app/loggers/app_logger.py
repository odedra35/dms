import logging
import os.path
import sys


log_name = "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(filename)s:%(lineno)d, Function: %(funcName)s] %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_name),
        logging.StreamHandler(sys.stdout)
        ]
)

__logger = logging.getLogger(__file__)

# Init and clear app.log
if not os.path.isfile(log_name):
    __logger.info(f"Init {log_name!r}...")
    open(log_name).close()

# Init and clear app.log
with open(log_name, "w") as f:
    __logger.info("Clear app.log...")
    f.write("")

def get_app_logger() -> logging.Logger:
    """Supply logger service for other modules."""
    __logger.debug("fetching logger...")
    if __logger:
      return __logger
    return logging.getLogger(__file__)
