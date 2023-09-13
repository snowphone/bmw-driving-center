import logging
import os
import random
import sys
from argparse import (
    ArgumentParser,
    Namespace,
)
from collections import defaultdict
from datetime import datetime
from operator import attrgetter
from pprint import pprint

import dotenv
import requests
from dateutil.relativedelta import relativedelta
from urllib3.exceptions import InsecureRequestWarning

from holiday import holidays_in_korea
from notification import notify
from structs import ReturnType

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
        "%(module)s:%(lineno)d] "
        "%(message)s"
    ),
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger()


AVAILABLE_PROGRAMS = [
    "Starter Pack",
    "M Core",
    "M/JCW Intensive",
    "M Drift Ⅰ",
    "M Drift Ⅱ",
    "M Drift Ⅲ",
    "Starter Pack(Eng)",
]


class BmwDrivingCenter:
    def __init__(self, username: str, password: str) -> None:
        self.sess = requests.Session()
        self.sess.verify = False

        return

    @classmethod
    def _rand_10_chars(cls):
        return format(random.randint(0, 36**10), "x")

    def _login(self, username: str, password: str):
        ts = int(datetime.now().timestamp())
        resp = self.sess.get(
            f"https://customer.bmwgroup.com/oneid/oneidconfig/client/dcbmw.json?t={ts}"
        )
        client_id = resp.json()["client"]["client_id"]

        login_payload = dict(
            client_id=client_id,
            response_type="code",
            scope="openid%%20authenticate_user",
            redirect_uri="https%%3A%%2F%%2Fdriving-center.bmw.co.kr%%2Flogin%%2Foauth2%%2Fcode%%2Fgcdm",  # noqa
            state=self._rand_10_chars(),
            nonce="",
            username=username,
            password=password,
            grant_type="authorization_code",
        )
        resp = self.sess.post(
            "https://customer.bmwgroup.com/gcdm/oauth/authenticate",
            data=login_payload,
        )
        assert resp.status_code == 200
        return

    def search_for(self, programs: list[str]) -> ReturnType:
        answer = defaultdict(list)

        for program in programs:
            product_code = self._get_product_code(program)

            months = [
                it.strftime("%Y%m")
                for it in [datetime.now(), (datetime.now() + relativedelta(months=1))]
            ]
            for month in months:
                logger.info(month)
                resp = self.sess.get(
                    f"https://driving-center.bmw.co.kr/api/public/schedule?targetMonth={month}&productMasterCode={product_code}"  # noqa
                )
                data = resp.json()["data"]["turnDateList"]

                for it in data:
                    date = it["turnDate"]
                    resp = self.sess.get(
                        f"https://driving-center.bmw.co.kr/api/public/schedule/{date.replace('-', '')}?productMasterCode={product_code}"  # noqa
                    )
                    answer[program].append(
                        {"date": date, "programs": resp.json()["data"]}
                    )
        return dict(answer)

    def _get_product_code(self, name: str):
        data = self.sess.get(
            "https://driving-center.bmw.co.kr/api/public/categories/2/program"
        ).json()
        programs = data["data"]

        logger.info(name)
        obj = next(it for it in programs if it["productNameEnglish"] == name)
        logger.debug(f"{name}: {obj}")
        return obj["productMasterCode"]

    def _convert_to_iso_format(self, entry_list: list[dict]):
        for it in entry_list:
            it["PlayDate"] = (
                datetime.strptime(it["PlayDate"], "%Y%m%d").date().isoformat()
            )

        return


def main(args: Namespace):
    logger.info(f"Given arguments: {args}")
    resp = BmwDrivingCenter(args.id, args.pw).search_for(args.programs)

    pprint(resp)

    holiday_only = {
        pg: [
            it
            for it in dates
            if it["date"] in holidays_in_korea() and it["date"] not in set(args.excepts)
        ]
        for pg, dates in resp.items()
    }

    pprint(holiday_only)

    if args.notify and holiday_only:
        notify(holiday_only, program=args.program)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--id", default=os.environ.get("BMW_ID"))
    parser.add_argument("--pw", default=os.environ.get("BMW_PW"))
    parser.add_argument("programs", nargs="+", choices=AVAILABLE_PROGRAMS)
    parser.add_argument("--notify", action="store_true")
    parser.add_argument(
        "--excepts", nargs="+", default=[], help="제외시킬 날짜. 포맷: YYYY-MM-DD"
    )

    main(parser.parse_args())


# 카테고리: https://driving-center.bmw.co.kr/api/public/categories  # noqa
# Training 프로그램 목록: https://driving-center.bmw.co.kr/api/public/categories/2/program  # noqa
# 그 달의 열린 프로그램들: https://driving-center.bmw.co.kr/api/public/schedule?targetMonth=202309&productMasterCode=1015  # noqa
# 시간대 및 좌석 수: https://driving-center.bmw.co.kr/api/public/schedule/20230914?productMasterCode=1015  # noqa
