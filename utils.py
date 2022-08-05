from typing import Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from settings import Settings


def prepare_script_environment(
        settings: Settings
) -> Tuple[requests.Session, Settings]:
    """Prepare environment and create request session with retry strategy."""

    retry_strategy = Retry(
        total=settings.RETRY_COUNT,
        status_forcelist=settings.STATUS_FORCE_LIST,
        allowed_methods=settings.ALLOWED_METHODS
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session, settings
