import logging
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

now_cet = datetime.now(ZoneInfo("Europe/Warsaw"))


LOG_PATH = (
    Path(__file__).parent.parent / "app_logs" / f"app_{now_cet.strftime('%Y-%m-%d_%H-%M-%S')}.log"
)

LOG_PATH.parent.mkdir(
    parents=True, exist_ok=True
)  # creates a new folder  if its not there; if there, no action


def setup_logging(level: int = logging.INFO):
    """
    Its enough for this method to be fired at the beginning of the process.
    Python does  save the  root logger config in global mmeory through the whole life of the process.
    Each module later does this : logger = logging.getLogger(__name__)
    and ingerith this config from root logger, without any import
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s",
        force=True,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_PATH),
        ],
    )
