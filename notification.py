import functools
from typing import Any

import simplejson
from requests import post

loads = simplejson.loads
dumps = functools.partial(simplejson.dumps, for_json=True, ensure_ascii=False)


def notify(data: Any, program: str):
    post(
        "https://ntfy.sixtyfive.me/bmw-driving-center",
        data=dumps(data, indent=2),
        headers={
            "Title": f"{program}".encode(),
            "priority": '3' if any(data.values()) else '2',
        },
    )
