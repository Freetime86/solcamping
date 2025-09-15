import random
import time

import datetime
from user_agent import generate_user_agent
import httpx
import mangsang_data as md
import mangsang_message as mm
import mangsang_utils as mu
import logging
import sys
import threading
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from httpx import HTTPTransport
import copy

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # ← 여기가 datefmt!
)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.handlers = []  # 기존 핸들러 제거
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger()

lock = threading.Lock()
shared_data = {'LIMIT': 0,
               'POST_ID': ''}

global limit


# ✅ 공통 세션 확보 (로그인 완료 후 쿠키 포함)
def get_logged_in_session(DATASET):
    USER_INFO = DATASET['USER_INFO']
    proxies = get_proxy()
    login_url = 'https://www.campingkorea.or.kr/login/ND_loginAction.do'
    DATASET['SESSION_LIST'] = []
    DATASET['ACTIVE_USER_LIST'] = []
    # 커넥션 풀 제한 설정
    limits = httpx.Limits(
        max_connections=200,
        max_keepalive_connections=100
    )
    for user in USER_INFO:
        if USER_INFO[user]['active']:
            if DATASET['PROXY']:
                #proxy = ''
                #while True:
                #    try:
                #        proxy = random.choice(proxies)
                #        transport = HTTPTransport(proxy=proxy, verify=False)
                #        with httpx.Client(transport=transport, timeout=3) as client:
                #            r = client.get("https://httpbin.org/ip")
                #            if r.status_code == 200:
                #                break
                #    except Exception as e:
                #        print(f"[프록시 실패] {proxy} → {e}")
                #        continue
                #transport = HTTPTransport(proxy=proxy, verify=False)
                proxy = random.choice(proxies)
                transport = HTTPTransport(proxy=proxy, verify=False)
                session = httpx.Client(
                    transport=transport,
                    limits=limits,
                    verify=False
                )
            else:
                session = httpx.Client(
                    limits=limits,
                    verify=False,
                    timeout=200
                )
            data = {
                'userId': USER_INFO[user]['rid'],
                'userPassword': mu.op_encrypt(USER_INFO[user]['rpwd']),
                'returnUrl': 'https://www.campingkorea.or.kr/index.do'
            }
            session.post(login_url, data=data)
            DATASET['SESSION_LIST'].append(session)
            DATASET['ACTIVE_USER_LIST'].append(USER_INFO[user])
    logger.info('ACTIVE USER NUMBER (' + str(len(DATASET['SESSION_LIST'])) + ')개 활성화')
    return DATASET


def get_proxy():
    file_path = os.path.join(os.path.expanduser("~"), "Desktop", "proxy.txt")

    proxies = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            proxy_addr = line.strip()
            if proxy_addr:  # 빈 줄 무시
                proxy = f"http://{proxy_addr}"
                proxies.append(proxy)
    return proxies


def cancellation(DATASET, session, bot_name, user):
    try:
        BOT_DATASET = copy.deepcopy(DATASET)
        url = "https://www.campingkorea.or.kr/user/myPage/BD_reservationReserveInfo.do?trrsrtCode=&resveSttusCode=&q_currPage=1"
        while True:
            response = session.get(url, timeout=100)
            if response.is_success:
                html = response.text  # 또는 html 문자열 직접 사용
                soup = BeautifulSoup(html, 'html.parser')
                tbody = soup.find_all("tbody")[0]  # 첫 번째 tbody
                rows = tbody.find_all("tr")  # tbody 안의 모든 tr

                # 예약번호들을 담을 리스트
                reservation_numbers = []

                for row in rows:
                    cells = row.find_all("td")
                    values = [cell.get_text(strip=True) for cell in cells]
                    if '데이터가' not in values[0] and values[2] in DATASET['RESERVATION_NO_LIST']:
                        reservation_numbers.append(str(values[2]))
                if len(reservation_numbers) > 0:
                    mm.message(BOT_DATASET, 'reservation_numbers = > ' + str(reservation_numbers))
                if cancellation_final(user, session, bot_name, reservation_numbers):
                    time.sleep(1)
                    break
            else:
                mm.message9(BOT_DATASET, user['rid'] + '/' + user['user_name'] + f"[{bot_name}] 실패 - 임시 점유 이상")
    except Exception as e:
        print(f"[{bot_name}] 예외 발생: {e}")
        pass


def cancellation_final(user, session, bot_name, reservation_numbers):
    try:
        for num in reservation_numbers:
            dict_data = {
                'resveNo': num
            }
            url = "https://www.campingkorea.or.kr/user/myPage/ND_updateCancleResve.do"
            response = session.post(url, data=dict_data, timeout=30, headers={
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host': 'www.campingkorea.or.kr',
                'Origin': 'https://www.campingkorea.or.kr',
                'Referer': 'https://www.campingkorea.or.kr/user/myPage/BD_reservationReserveInfo.do?trrsrtCode=&resveSttusCode=&q_currPage=1',
                'Sec-Ch-Ua': '"Google Chrome";v="138", "Chromium";v="138", "Not-A.Brand";v="8"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': str(generate_user_agent(os='win', device_type='desktop')),
                'X-Requested-With': 'XMLHttpRequest'})
            if response.is_success and 'json' in response.headers.get('Content-Type', ''):
                dict_meta = {'status_code': response.status_code, 'ok': response.is_success,
                             'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'],
                             'cookies': response.cookies}
                result = {**dict_meta, **response.json()}
                if result['status_code'] == 200:
                    if 'message' in result:
                        mm.message({'MESSAGE', ''}, '[' + str(num) + ']' + ' => 예약 내역 삭제 완료 / 유저정보: 아이디=(' + user['rid'] + ') 비밀번호=(' + user[
                            'rpwd'] + ') 이름=(' + user['user_name'] + ')')
                else:
                    mm.message({'MESSAGE', ''},'[' + str(num) + ']' + ' => 예약 내역 삭제 실패 / 유저정보: 아이디=(' + user['rid'] + ') 비밀번호=(' + user[
                            'rpwd'] + ') 이름=(' + user['user_name'] + ')')
            else:
                print(user['rid'] + '/' + user['user_name'] + f"[{bot_name}] 예약 취소 실패, response error")
            time.sleep(1)
        return True
    except Exception as e:
        pass
        #print(f"[{bot_name}] 예외 발생: {e}")


# ✅ 실행 부분
def run_cancellation_bot(DATASET):
    BOT_DATASET = copy.deepcopy(DATASET)
    if DATASET['CANCEL']:
        DATASET = get_logged_in_session(DATASET)
    DATASET['CONTINUE'] = True
    session_list = DATASET['SESSION_LIST']
    active_user_list = DATASET['ACTIVE_USER_LIST']
    target_data = DATASET['TARGET_DATA']

    session_len = len(session_list)
    target_len = len(target_data)
    max_len = max(session_len, target_len)
    # ThreadPoolExecutor 사용
    with ThreadPoolExecutor(max_workers=max_len) as executor:
        futures = []

        for i in range(session_len):
            session = session_list[i]
            user = active_user_list[i]
            bot_name = 'ID' + str(user['rid']) + ' 이름 : ' + str(user['user_name'])
            futures.append(
                executor.submit(cancellation, BOT_DATASET, session, bot_name, user)
            )

        for future in futures:
            future.result()  # 예외 발생 시 처리
        time.sleep(0.1)


def run_canceler(DATASET, session_list):
    BOT_DATASET = copy.deepcopy(DATASET)
    DATASET['CONTINUE'] = True
    active_user_list = DATASET['ACTIVE_USER_LIST']
    target_data = DATASET['TARGET_DATA']

    session_len = len(session_list)
    target_len = len(target_data)
    max_len = max(session_len, target_len)
    # ThreadPoolExecutor 사용
    with ThreadPoolExecutor(max_workers=max_len) as executor:
        futures = []

        for i in range(session_len):
            session = session_list[i]
            user = active_user_list[i]
            bot_name = 'ID' + str(user['rid']) + ' 이름 : ' + str(user['user_name'])
            futures.append(
                executor.submit(cancellation, BOT_DATASET, session, bot_name, user)
            )

        for future in futures:
            future.result()  # 예외 발생 시 처리
        time.sleep(0.1)


# ✅ 테스트 데이터 예시
def worker(DATASET):
    DATASET = md.convert(DATASET)
    DATASET['TARGET_DATA'] = []
    run_cancellation_bot(DATASET)
