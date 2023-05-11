import os
from pprint import PrettyPrinter
from typing import Literal
import requests
from urllib3.exceptions import InsecureRequestWarning

import dotenv

dotenv.load_dotenv()

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def print(*args):
    PrettyPrinter().pprint(args)


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
        print(raw_program_info)
        '''
                {'ProgCodeName': 'M Drift I',
          'ProgName': '10034',
          'course': [{'Course': '34001',
                      'GoodsCode': '14000326',
                      'OpTime': '0900',
                      'PlaceCode': '14000035',
                      'PlayDate': '20230512',
                      'PlaySeq': 'V38',
                      'ProgName': '10034',
                      'RemainSeatCnt': 0,
                      'SeatGrade': '1',
                      'SeatGradeName': 'M Drift I - M Drift'},
                     {'Course': '34002',
                      'GoodsCode': '14000326',
                      'OpTime': '1340',
                      'PlaceCode': '14000035',
                      'PlayDate': '20230514',
                      'PlaySeq': 'V40',
                      'ProgName': '10034',
                      'RemainSeatCnt': 0,
                      'SeatGrade': '8',
                      'SeatGradeName': 'M Drift I - Voucher'}],
          'extYN': 'N',
          'level': '2',
          'pgType': 'T',
          'sort': '5'}
        '''

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
                "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramPlayDate.do",
                data=payload,
            )
            available_date_list = resp.json()["item"]

            remaining_seat = [
                it
                for dt in available_date_list
                if (
                    it := self.sess.post(
                        "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramTime.do",
                        data={
                            **payload,
                            "PlayDate": dt.replace("-", ""),
                            "SeatCnt": "0",
                        },
                    ).json()["item"][0]
                )["RemainSeatCnt"]
            ]
            result.extend(remaining_seat)

        return result


def main():
    username = os.environ["BMW_ID"]
    password = os.environ["BMW_PW"]
    assert username and password

    resp = BmwDrivingCenter(username, password).search_for("M Drift I")

    print(resp)


if __name__ == "__main__":
    main()
