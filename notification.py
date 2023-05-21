import functools
from typing import Any

import simplejson
from requests import post

loads = simplejson.loads
dumps = functools.partial(simplejson.dumps, for_json=True)


def notify(data: Any, program: str):
    post(
        "https://ntfy.sixtyfive.me/bmw-driving-center",
        data=dumps(data, indent=2).encode("utf-8"),
        headers={
            "Title": f"{program}: {len(data)}",
            "priority": '3' if data else '2',
        },
    )
