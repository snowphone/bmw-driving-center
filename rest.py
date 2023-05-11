from pprint import PrettyPrinter
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def print(*args):
    PrettyPrinter().pprint(args)


with requests.Session() as sess:
    sess.verify = False
    sess.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35"


    resp = sess.post(
        "https://www.bmw-driving-center.co.kr/kr/logon.do",
        allow_redirects=False,
        data={
            "u_id": "sixtyfive",
            "u_pw": "!r2xjagjdc",
            "u_save": "Y",
            "callbackUri": "null",
        },
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "DNT": "1",
            "Origin": "https://www.bmw-driving-center.co.kr",
            "Referer": "https://www.bmw-driving-center.co.kr/kr/login.do",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
        },
    )
    # print("log on", resp, resp.request.headers)

    resp = sess.get("https://www.bmw-driving-center.co.kr/kr/index.do")
    resp = sess.get("https://www.bmw-driving-center.co.kr/kr/program/reserve.do")
    resp = sess.get("https://www.bmw-driving-center.co.kr/kr/program/reserve1.do")
    # print("index", resp.headers["set-cookie"])
    jsessionid = resp.cookies.get("JSESSIONID")
    print("JSESSIONID", jsessionid)

    resp = sess.post(
        "https://www.bmw-driving-center.co.kr/kr/api/program/getPrograms.do",
    )
    print("get programs", resp, resp.json())

    resp = sess.post(
       "https://www.bmw-driving-center.co.kr/kr/api/getProgramUseYn.do",
       data={"progName": "10034"},
    )
    #print("worthy..?", resp, resp.headers)

    #sess.cookies.pop("JSESSIONID")

    resp = sess.post(
       "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramPlayDate.do",
       data={
           "Level": "2",
           "extYN": "N",
           "PlaySeq": "V37",
           "ProgName": "10034",
           "PlaceCode": "14000035",
           "GoodsCode": "14000326",
           "Course": "34001",
       },
    )
    print("date", resp.json() )

    resp = sess.post(
       "https://www.bmw-driving-center.co.kr/kr/api/program/getProgramTime.do",
       data={
           "Level": "2",
           "extYN": "N",
           "PlaySeq": "V37",
           "ProgName": "10034",
           "PlaceCode": "14000035",
           "GoodsCode": "14000326",
           "Course": "34001",
           "PlayData": "20230524",
           "SeatCnt": "1",
       },
    )
    print("seat", resp.json())

    pass
