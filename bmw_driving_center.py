import os
from datetime import datetime
from pprint import PrettyPrinter
from typing import Literal

import dotenv
import holidays
import requests
from urllib3.exceptions import InsecureRequestWarning

dotenv.load_dotenv()

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


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
        assert resp.status_code == 302

        self.sess.get("https://www.bmw-driving-center.co.kr/kr/index.do")
        self.sess.get("https://www.bmw-driving-center.co.kr/kr/program/reserve.do")
        self.sess.get("https://www.bmw-driving-center.co.kr/kr/program/reserve1.do")

        return

    def search_for(self, program: Literal["M Drift I", "M Core"]):
        resp = self.sess.post(
            "https://www.bmw-driving-center.co.kr/kr/api/program/getPrograms.do",
        )

        raw_program_info = next(
            it for it in resp.json()["item"] if program in it["ProgCodeName"]
        )

        result = []
        for course in raw_program_info["course"]:
            payload = {
                k: v for k, v in raw_program_info.items() if k in {"extYN", "level"}
            } | {
                k: v
                for k, v in course.items()
                if k in {"PlaySeq", "ProgName", "PlaceCode", "GoodsCode", "Course"}
            }

            resp = self.sess.post(
                "https://www.bmw-driving-center.co.kr/kr/api/getProgramUseYn.do",
                data={"progName": payload["Course"]},
            )

            resp = self.sess.post(
                "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramPlayDate.do",  # noqa: E501
                data=payload,
            )
            available_date_list = resp.json()["item"]

            remaining_seat = [
                it
                for dt in available_date_list
                if (
                    it := self.sess.post(
                        "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramTime.do",  # noqa: E501
                        data={
                            **payload,
                            "PlayDate": dt.replace("-", ""),
                            "SeatCnt": "0",
                        },
                    ).json()["item"][0]
                )["RemainSeatCnt"]
                > 0
            ]
            result.extend(remaining_seat)

        self._convert_to_iso_format(result)

        return result

    def _convert_to_iso_format(self, entry_list: list[dict]):
        for it in entry_list:
            it["PlayDate"] = (
                datetime.strptime(it["PlayDate"], "%Y%m%d").date().isoformat()
            )

        return


def korea_holidays():
    year = datetime.now().year
    return {
        it.isoformat() for it in holidays.SouthKorea(years={year, year + 1}).keys()
    } | {"2023-05-29"}


def main():
    username = os.environ["BMW_ID"]
    password = os.environ["BMW_PW"]
    resp = BmwDrivingCenter(username, password).search_for("M Drift I")

    holiday_only = [it for it in resp if it["PlayDate"] in korea_holidays()]
    PrettyPrinter().pprint(holiday_only)


if __name__ == "__main__":
    main()
