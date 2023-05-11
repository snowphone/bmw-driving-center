import logging
import os
import sys
from argparse import (
    ArgumentParser,
    Namespace,
)
from datetime import datetime
from operator import attrgetter
from pprint import PrettyPrinter

import dotenv
import requests
from urllib3.exceptions import InsecureRequestWarning

from holiday import holidays_in_korea
from notification import notify

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)  # type: ignore  # noqa: E501

dotenv.load_dotenv()


log_level = attrgetter(os.environ.get("LOG_LEVEL", "INFO").upper())(logging)


logging.basicConfig(
    stream=sys.stderr,
    level=log_level,
    format=(
        "[%(levelname).1s %(asctime)s.%(msecs)03d+09:00 "
        "%(processName)s:%(filename)s:%(funcName)s:"
        "%(module)s:%(lineno)d]\n"
        "%(message)s"
    ),
    datefmt="%Y-%m-%dT%H:%M:%S",
)

logger = logging.getLogger()


AVAILABLE_PROGRAMS = [
    'Test Drive',
    'Scenic Drive',
    'Night Drive',
    'i Drive',
    'On-Road',
    'Off-Road',
    'Taxi',
    'X Bus',
    'Owners Track Day',
    'Owners Drift Day',
    'Starter Pack',
    'Intensive',
    'M/JCW Intensive',
    'M Core',
    'M Drift I',
    'M Drift II',
    'M Drift Ⅲ',
    'Private Coaching',
]


class BmwDrivingCenter:
    def __init__(self, username: str, password: str) -> None:
        self.sess = requests.Session()
        self.sess.verify = False

        self._login(username, password)
        return

    def _login(self, username: str, password: str):
        self.sess.get("https://www.bmw-driving-center.co.kr/kr/login.do")

        resp = self.sess.post(
            "https://www.bmw-driving-center.co.kr/kr/logon.do",
            allow_redirects=False,
            data={
                "u_id": username,
                "u_pw": password,
                "u_save": "Y",
                "callbackUri": "null",
            },
        )
        logger.info(f"Log in status code: {resp.status_code}")
        assert resp.status_code == 302

        self.sess.get("https://www.bmw-driving-center.co.kr/kr/index.do")
        self.sess.get("https://www.bmw-driving-center.co.kr/kr/program/reserve.do")
        self.sess.get("https://www.bmw-driving-center.co.kr/kr/program/reserve1.do")

        return

    def search_for(self, program: str):
        resp = self.sess.post(
            "https://www.bmw-driving-center.co.kr/kr/api/program/getPrograms.do",
        )
        logger.debug(resp.json())

        raw_program_info = next(
            it for it in resp.json()["item"] if program in it["ProgCodeName"]
        )
        logger.info(f"{program}: {raw_program_info}")

        result = []
        for course in raw_program_info["course"]:
            payload = {
                k: v for k, v in raw_program_info.items() if k in {"extYN", "level"}
            } | {
                k: v
                for k, v in course.items()
                if k in {"PlaySeq", "ProgName", "PlaceCode", "GoodsCode", "Course"}
            }
            logger.info(f"{payload=}")

            resp = self.sess.post(
                "https://www.bmw-driving-center.co.kr/kr/api/getProgramUseYn.do",
                data={"progName": payload["Course"]},
            )

            resp = self.sess.post(
                "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramPlayDate.do",  # noqa: E501
                data=payload,
            )
            available_date_list = resp.json()["item"]
            logger.info(f"{available_date_list=}")

            for dt in available_date_list:
                resp = self.sess.post(
                    "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramTime.do",  # noqa: E501
                    data={
                        **payload,
                        "PlayDate": dt.replace("-", ""),
                        "SeatCnt": "0",
                    },
                ).json()
                logger.info(f"{dt}: {resp}")

                it = resp["item"][0]
                if it["RemainSeatCnt"] == 0:
                    continue
                result.append(it)

        self._convert_to_iso_format(result)

        return result

    def _convert_to_iso_format(self, entry_list: list[dict]):
        for it in entry_list:
            it["PlayDate"] = (
                datetime.strptime(it["PlayDate"], "%Y%m%d").date().isoformat()
            )

        return


def main(args: Namespace):
    logger.info(f"Given arguments: {args}")
    resp = BmwDrivingCenter(args.id, args.pw).search_for(args.program)

    holiday_only = [
        it
        for it in resp
        if it["PlayDate"] in holidays_in_korea()
        and it["PlayDate"] not in set(args.excepts)
    ]
    PrettyPrinter().pprint(holiday_only)

    if args.notify:
        notify(holiday_only)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--id", default=os.environ.get("BMW_ID"))
    parser.add_argument("--pw", default=os.environ.get("BMW_PW"))
    parser.add_argument("--program", choices=AVAILABLE_PROGRAMS, required=True)
    parser.add_argument("--notify", action="store_true")
    parser.add_argument(
        "--excepts", nargs="+", default=[], help="제외시킬 날짜. 포맷: YYYY-MM-DD"
    )

    main(parser.parse_args())
