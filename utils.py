import textwrap

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from settings import Settings


def correct_textwrap_dedent(multiline_message: str) -> str:
    """Correct textwrap dedent."""
    message = "\n".join(
        [
            textwrap.dedent(line_message)
            for line_message in multiline_message.split("\n")
        ]
    )
    return message


def get_session(
        settings: Settings
) -> requests.Session:
    """Get new request session with retry strategy."""

    retry_strategy = Retry(
        total=settings.RETRY_COUNT,
        status_forcelist=settings.STATUS_FORCE_LIST,
        allowed_methods=settings.ALLOWED_METHODS
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
