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


def searching(DATASET, session, bot_name, user):
    try:
        BOT_DATASET = copy.deepcopy(DATASET)
        while True:
            url = "https://www.campingkorea.or.kr/user/myPage/BD_reservationReserveInfo.do?trrsrtCode=&resveSttusCode=&q_currPage=1"
            #BOT_DATASET = mm.message(BOT_DATASET, bot_name + ' 예약 요청 중 ' + dict_data['resveBeginDe'] + ' ~ ' + dict_data['resveEndDe'])
            response = session.get(url, timeout=100)
            if response.is_success:
                html = response.text  # 또는 html 문자열 직접 사용
                soup = BeautifulSoup(html, 'html.parser')

                # 예약번호들을 담을 리스트
                tbody = soup.find_all("tbody")[0]  # 첫 번째 tbody
                rows = tbody.find_all("tr")  # tbody 안의 모든 tr

                for row in rows:
                    cells = row.find_all("td")
                    values = [cell.get_text(strip=True) for cell in cells]
                    if '데이터가' not in values[0]:
                        BOT_DATASET = mm.message8(BOT_DATASET,
                                    '유저정보: 아이디:' + user['rid'].ljust(12) + ' 비밀번호:' + user['rpwd'].ljust(12) + ' 이름=' + user[
                                        'user_name'].ljust(4) + ' 예약 리스트 => 대상:' + str(values[5].ljust(27)) + ' 예약기간:' + str(values[4]) + '   예약시점:' + str(values[3]) + ' 상태:' + str(values[8]) + ' 예약번호:[' + str(values[2]) + ']')
                break
            else:
                mm.message9(BOT_DATASET, user['rid'] + '/' + user['user_name'] + f"[{bot_name}] 실패 - 임시 점유 이상")
    except Exception as e:
        pass
        #print(f"[{bot_name}] 예외 발생: {e}")



# ✅ 실행 부분
def run_reservation_bot(DATASET):
    BOT_DATASET = copy.deepcopy(DATASET)
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
                executor.submit(searching, BOT_DATASET, session, bot_name, user)
            )

        for future in futures:
            future.result()  # 예외 발생 시 처리
        time.sleep(0.1)


# ✅ 테스트 데이터 예시
def worker(DATASET):
    DATASET = md.convert(DATASET)
    DATASET['TARGET_DATA'] = []
    run_reservation_bot(DATASET)
