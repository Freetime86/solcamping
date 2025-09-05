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
               'POST_ID': '',
               'RESERVATION_LOG': True,
               'AVAILABLE_ROOMS': []}

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
    user_keys = list(USER_INFO.keys())
    #random.shuffle(user_keys)

    for user_key in user_keys:
        user_data = USER_INFO[user_key]
        if user_data['active']:
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
                'userId': user_data['rid'],
                'userPassword': mu.op_encrypt(user_data['rpwd']),
                'returnUrl': 'https://www.campingkorea.or.kr/index.do'
            }
            session.post(login_url, data=data)
            DATASET['SESSION_LIST'].append(session)
            DATASET['ACTIVE_USER_LIST'].append(user_data)
            if DATASET['SHOW_RESERVATION']:
                delete_occ(session)
    if not DATASET['SHOW_RESERVATION']:
        logger.info('ACTIVE USER NUMBER (' + str(len(DATASET['SESSION_LIST'])) + ')개 활성화')
    else:
        logger.info('적용일자 기준 예약 가능한 대상 탐색 중....')
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


# ✅ 예약 요청을 보내는 함수
def reserve_site(DATASET, session, dict_data, bot_name, user):
    try:
        BOT_DATASET = copy.deepcopy(DATASET)
        start_time = time.time()
        run_cnt = 0
        while True:
            if not DATASET['SHOW_RESERVATION']:
                elapsed_time = time.time() - start_time  # 경과된 시간 계산
                if elapsed_time >= 3600 * run_cnt:  # 3600초 == 1시간
                    BOT_DATASET = mm.message(BOT_DATASET,
                                             f"{bot_name.ljust(12)} {dict_data['resveBeginDe']} ~ {dict_data['resveEndDe']} 예약 진행 중 / "
                                             f"경과 시간 : {str(run_cnt).ljust(2)}시간 => 유저정보: "
                                             f"아이디={user['rid'].ljust(10)} "
                                             f"비밀번호={user['rpwd'].ljust(18)} "
                                             f"이름={user['user_name']}")
            url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
            #BOT_DATASET = mm.message(BOT_DATASET, bot_name + ' 예약 요청 중 ' + dict_data['resveBeginDe'] + ' ~ ' + dict_data['resveEndDe'])
            response = session.post(url, data=dict_data, timeout=100)
            if response.is_success and 'json' in response.headers.get('Content-Type', ''):
                result = response.json()
                if result['preocpcEndDt'] is not None:
                    if DATASET['SHOW_RESERVATION']:
                        if str(result['fcltyFullNm']) not in shared_data['AVAILABLE_ROOMS']:
                            shared_data['AVAILABLE_ROOMS'].append(str(result['fcltyFullNm']) + '/' + bot_name.split()[-1])
                            logger.info(str(result['fcltyFullNm']) + '/' + bot_name.split()[-1])
                            return
                    else:
                        msg = str(result['fcltyFullNm']) + ' => ' + str(result['fcltyCode']) + ' / ' + str(result['resveBeginDe']) + ' ~ ' + str(result['resveEndDe'])
                        mm.message4(BOT_DATASET,f"{bot_name.ljust(12)} 임시 점유 완료 {msg.ljust(10)} => 유저정보: "
                                        f"아이디=({user['rid'].ljust(10)}) "
                                        f"비밀번호=({user['rpwd'].ljust(18)}) "
                                        f"이름=({user['user_name']})")
                        mm.message7(BOT_DATASET,  f"{bot_name.ljust(12)} 임시 점유 시간 {msg.ljust(10)} "
                                        f"{str(result['preocpcBeginDt'])} ~ {str(result['preocpcEndDt'])} "
                                        f"=> 유저정보: 아이디=({user['rid'].ljust(10)}) "
                                        f"비밀번호=({user['rpwd'].ljust(18)}) "
                                        f"이름=({user['user_name']})")
                        #live_time = datetime.now() + timedelta(days=30)
                        #open_time = datetime.strptime((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d") + " 10:59:57", "%Y-%m-%d %H:%M:%S")
                        #reserve_time = datetime.strptime(result['resveBeginDe'] + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                        if reserve_final(BOT_DATASET, user, session, bot_name, result):
                            break
            else:
                mm.message9(BOT_DATASET, user['rid'] + '/' + user['user_name'] + f"[{bot_name}] 실패 - 임시 점유 이상")
    except Exception as e:
        pass
        #print(f"[{bot_name}] 예외 발생: {e}")


def reserve_final(BOT_DATASET, user, session, bot_name, result):
    try:
        msg = str(result['fcltyFullNm']) + ' => ' + str(result['fcltyCode']) + ' / ' + str(result['resveBeginDe']) + ' ~ ' + str(result['resveEndDe'])
        dict_data = {
            'trrsrtCode': str(result['trrsrtCode']),
            'fcltyCode': str(result['fcltyCode']),
            'fcltyTyCode': str(result['fcltyTyCode']),
            'preocpcFcltyCode': str(result['fcltyCode']),
            'resveNoCode': '',
            'resveBeginDe': str(result['resveBeginDe']),
            'resveEndDe': str(result['resveEndDe']),
            'resveNo': str(result['resveNo']),
            'registerId': str(user['rid']),
            'rsvctmNm': str(user['user_name']),
            'rsvctmEncptMbtlnum': str(user['rphone']),
            'encptEmgncCttpc': str(user['rphone']),
            'rsvctmArea': str(user['area_code']),
            'entrceDelayCode': '1004',
            'dspsnFcltyUseAt': 'N'
        }

        BOT_DATASET = mm.message5(BOT_DATASET, bot_name + ' ' + '확정 예약 중 ' + msg + ' => 유저정보: 아이디=(' + user['rid'] + ') 비밀번호=(' + user['rpwd'] + ') 이름=(' + user['user_name'] + ')')

        url = "https://www.campingkorea.or.kr/user/reservation/ND_insertresve.do"
        response = session.post(url, data=dict_data, timeout=5, headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Host': 'www.campingkorea.or.kr',
                    'Origin': 'https://www.campingkorea.or.kr',
                    'Referer': 'https://www.campingkorea.or.kr/user/reservation/BD_reservationInfo.do',
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
                    RESULT_TXT = result['message']
                    if RESULT_TXT == '예약신청이 정상적으로 완료되었습니다.':
                        mm.message6(BOT_DATASET, bot_name + ' ' + msg + ' => ' + ' 예약이 완료되었습니다. => 유저정보: 아이디=(' + user['rid'] + ') 비밀번호=(' + user['rpwd'] + ') 이름=(' + user['user_name'] + ')')
                        return True
                    else:
                        if '일시적인 장애로' in result['message']:
                            mm.message6(BOT_DATASET, bot_name + ' ' + msg +
                                        ' ' + '(' + result[
                                            'message'] + ') 다음과 같은 사유로 임시 점유를 다시 시도합니다.')
                        elif '예약이 불가능한' in result['message']:
                            mm.message6(BOT_DATASET, bot_name + ' ' + msg +
                                        ' ' + '(' + result[
                                            'message'] + ') 다음과 같은 사유로 임시 점유를 다시 시도합니다.')
                        elif '비정상적인 접근' in result['message']:
                            mm.message6(BOT_DATASET, bot_name + ' ' + msg +
                                        ' ' + '(' + result[
                                            'message'] + ') 다음과 같은 사유로 임시 점유를 다시 시도합니다.')
                        else:
                            mm.message6(BOT_DATASET, bot_name + ' ' + msg +' ' + result['message'])
        else:
            mm.message9(BOT_DATASET, user['rid'] + '/' + user['user_name'] + f"[{bot_name}] 실패 - 확정 예약 이상")
        return False
    except Exception as e:
        pass
        #print(f"[{bot_name}] 예외 발생: {e}")


def delete_occ(session):
    try:
        url = "https://www.campingkorea.or.kr/user/reservation/ND_deletePreOcpcInfo.do"
        session.post(url, timeout=100)
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

        for i in range(max_len):
            session_idx = i % session_len
            target_idx = i % target_len

            session = session_list[session_idx]
            user = active_user_list[session_idx]
            target = target_data[target_idx].copy()
            bot_name = f"{(target['fcltyCode'] + '_' + str(i + 1)).ljust(9)} {target['max_cnt'].rjust(3)}인실"
            del target['max_cnt']
            futures.append(
                executor.submit(reserve_site, BOT_DATASET, session, target, bot_name, user)
            )

        for future in futures:
            future.result()  # 예외 발생 시 처리
        time.sleep(0.1)


# ✅ 테스트 데이터 예시
def worker(DATASET):
    DATASET = md.convert(DATASET)
    reservation_targets = []
    for target_type_list in DATASET['TARGET_LIST']:
        idx = 0
        for type_no in target_type_list['TARGET_NO']:
            _max_cnt = target_type_list['TARGET_MAX_CNT'][idx]
            if (type_no in DATASET['ROOM_WANTS'] or DATASET['ROOM_WANTS'][0] == 'ALL') and type_no not in DATASET['ROOM_EXPT']:
                for begin_date in DATASET['SELECT_DATE']:
                    for PERIOD in DATASET['PERIOD']:
                        end_date = (datetime.strptime(begin_date, '%Y-%m-%d') + timedelta(days=int(PERIOD))).strftime(
                            "%Y-%m-%d")

                        TARGET_DATA = {
                            'trrsrtCode': str(target_type_list['trrsrtCode']),
                            'fcltyCode': str(type_no),
                            'resveNoCode': str(target_type_list['resveNoCode']),
                            'resveBeginDe': str(begin_date),
                            'resveEndDe': str(end_date),
                            'max_cnt': str(_max_cnt)
                        }
                        reservation_targets.append(TARGET_DATA)
            idx = idx + 1
        DATASET['TARGET_DATA'] = reservation_targets
    run_reservation_bot(DATASET)
