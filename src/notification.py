from datetime import datetime
from typing import Any

from requests import post

from .json import dumps


def notify(data: Any):
    post(
        "https://ntfy.sixtyfive.me/bmw-driving-center",
        data=dumps(data, indent=2).encode("utf-8"),
        headers={
            "Title": f"Available programs on {datetime.now().date().isoformat()}",
            "priority": '3',
        },
    )
