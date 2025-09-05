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
    proxies = {}
    if DATASET['PROXY']:
        proxies = get_proxy()
    login_url = 'https://www.campingkorea.or.kr/login/ND_loginAction.do'
    # 커넥션 풀 제한 설정
    limits = httpx.Limits(
        max_connections=200,
        max_keepalive_connections=100
    )
    customer = DATASET['CUSTOMER']
    holder = DATASET['HOLDER']
    user = {}

    for i in range(1):
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

        #customer
        if i == 0:
            user = USER_INFO[customer]
        #holder
        elif i == 1:
            user = USER_INFO[holder]

        data = {
            'userId': user['rid'],
            'userPassword': mu.op_encrypt(user['rpwd']),
            'returnUrl': 'https://www.campingkorea.or.kr/index.do'
        }
        # create session
        session.post(login_url, data=data)

        # customer
        if i == 0:
            DATASET['CUSTOMER_SESSION'] = session
            DATASET['CUSTOMER'] = user
            logger.info('구매자 : ID => ' + user['rid'] + ' 이름 => ' + user['user_name'])
        # holder
        elif i == 1:
            DATASET['HOLDER_SESSION'] = session
            DATASET['HOLDER'] = user
            logger.info('취소자 : ID => ' + user['rid'] + ' 이름 => ' + user['user_name'])

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
            if user['rid'] != shared_data['POST_ID'] or len(user) == 1:
                shared_data['POST_ID'] = user['rid']
                url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
                BOT_DATASET = mm.message(BOT_DATASET, bot_name + ' 예약 요청 중 ' + dict_data['resveBeginDe'] + ' ~ ' + dict_data['resveEndDe'])
                response = session.post(url, data=dict_data, timeout=100)
                if response.is_success and 'json' in response.headers.get('Content-Type', ''):
                    dict_meta = {'status_code': response.status_code, 'ok': response.is_success,
                                 'encoding': response.encoding,
                                 'Content-Type': response.headers['Content-Type'],
                                 'cookies': response.cookies}
                    result = {**dict_meta, **response.json()}
                    if result['preocpcEndDt'] is not None:
                        msg = str(result['fcltyFullNm']) + ' => ' + str(result['fcltyCode']) + ' / ' + str(result['resveBeginDe']) + ' ~ ' + str(result['resveEndDe'])
                        mm.message4(BOT_DATASET, bot_name + ' ' + '임시 점유 완료 ' + msg + ' => 유저정보: 아이디=(' + user['rid'] + ') 비밀번호=(' + user['rpwd'] + ') 이름=(' + user['user_name'] + ')')
                        mm.message7(BOT_DATASET, bot_name + ' ' + '임시 점유 시간 ' + msg + ' ' + str(result['preocpcBeginDt']) + ' ~ ' + str(result['preocpcEndDt']))
                        #live_time = datetime.now() + timedelta(days=30)
                        #open_time = datetime.strptime((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d") + " 10:59:57", "%Y-%m-%d %H:%M:%S")
                        reserve_time = datetime.strptime(result['resveBeginDe'] + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                        if reserve_final(BOT_DATASET, user, session, bot_name, result):
                            break
                else:
                    mm.message9(BOT_DATASET, user['rid'] + '/' + user['user_name'] + f"[{bot_name}] 실패 - 임시 점유 이상")
            elapsed_time = time.time() - start_time  # 경과된 시간 계산
            if elapsed_time >= 3600 * run_cnt:  # 3600초 == 1시간
                BOT_DATASET = mm.message8(BOT_DATASET, bot_name + ' 예약 진행 중.. / 경과 시간 : ' + str(run_cnt) + '시간')
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


def cancellation(DATASET, session, dict_data, bot_name, user):
    try:
        BOT_DATASET = copy.deepcopy(DATASET)
        start_time = time.time()
        run_cnt = 0
        while True:
            url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
            BOT_DATASET = mm.message(BOT_DATASET, bot_name + ' 예약 요청 중 ' + dict_data['resveBeginDe'] + ' ~ ' + dict_data['resveEndDe'])
            response = session.post(url, data=dict_data, timeout=100)
            if response.is_success and 'json' in response.headers.get('Content-Type', ''):
                dict_meta = {'status_code': response.status_code, 'ok': response.is_success,
                             'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'],
                             'cookies': response.cookies}
                result = {**dict_meta, **response.json()}
                if result['preocpcEndDt'] is not None:
                    msg = str(result['fcltyFullNm']) + ' => ' + str(result['fcltyCode']) + ' / ' + str(result['resveBeginDe']) + ' ~ ' + str(result['resveEndDe'])
                    mm.message4(BOT_DATASET, bot_name + ' ' + '임시 점유 완료 ' + msg + ' => 유저정보: 아이디=(' + user['rid'] + ') 비밀번호=(' + user['rpwd'] + ') 이름=(' + user['user_name'] + ')')
                    mm.message7(BOT_DATASET, bot_name + ' ' + '임시 점유 시간 ' + msg + ' ' + str(result['preocpcBeginDt']) + ' ~ ' + str(result['preocpcEndDt']))
                    #live_time = datetime.now() + timedelta(days=30)
                    #open_time = datetime.strptime((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d") + " 10:59:57", "%Y-%m-%d %H:%M:%S")
                    reserve_time = datetime.strptime(result['resveBeginDe'] + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                    if reserve_final(BOT_DATASET, user, session, bot_name, result):
                        break
            else:
                BOT_DATASET = mm.message9(BOT_DATASET, user['rid'] + '/' + user['user_name'] + f"[{bot_name}] 실패 - 임시 점유 이상")
            elapsed_time = time.time() - start_time  # 경과된 시간 계산
            if elapsed_time >= 3600 * run_cnt:  # 3600초 == 1시간
                BOT_DATASET = mm.message8(BOT_DATASET, bot_name + ' 예약 진행 중.. / 경과 시간 : ' + str(run_cnt) + '시간')
    except Exception as e:
        pass
        #print(f"[{bot_name}] 예외 발생: {e}")


# ✅ 실행 부분
def run_reservation_bot(DATASET):
    BOT_DATASET = copy.deepcopy(DATASET)
    DATASET = get_logged_in_session(DATASET)
    customer_session = DATASET['CUSTOMER_SESSION']
    #holder_session = DATASET['HOLDER_SESSION']
    target_data = DATASET['TARGET_DATA']    #무조건 하나로 강제함.
    worker_cnt = int(DATASET['BOT_NUMBER']) * 1 + 1 #1은 HOLDER 용

    # ThreadPoolExecutor 사용
    with ThreadPoolExecutor(max_workers=worker_cnt) as executor:
        futures = []

        for i in range(worker_cnt):
            # 첫 bot은 취소자
            if i == 0:
                #session = holder_session
                user = DATASET['HOLDER']
                bot_name = 'HOLDER_BOT'
                #futures.append(
                #    executor.submit(reserve_site, BOT_DATASET, session, target_data, bot_name, user)
                #)
            else:
                session = customer_session
                user = DATASET['CUSTOMER']
                bot_name = 'CUSTOMER_BOT' + str(i + 1)
                futures.append(
                    executor.submit(reserve_site, BOT_DATASET, session, target_data, bot_name, user)
                )
        for future in futures:
            future.result()  # 예외 발생 시 처리
        time.sleep(0.1)


# ✅ 테스트 데이터 예시
def worker(DATASET):
    DATASET = md.convert(DATASET)
    TARGET_DATA = {}
    for target_type_list in DATASET['TARGET_LIST']:
        for type_no in target_type_list['TARGET_NO']:
            if (type_no in DATASET['ROOM_WANTS'] or DATASET['ROOM_WANTS'][0] == 'ALL') and type_no not in DATASET['ROOM_EXPT']:
                for begin_date in DATASET['SELECT_DATE']:
                    for PERIOD in DATASET['PERIOD']:
                        end_date = (datetime.strptime(begin_date, '%Y-%m-%d') + timedelta(days=int(PERIOD))).strftime("%Y-%m-%d")
                        TARGET_DATA = {
                            'trrsrtCode': str(target_type_list['trrsrtCode']),
                            'fcltyCode': str(type_no),
                            'resveNoCode': str(target_type_list['resveNoCode']),
                            'resveBeginDe': str(begin_date),
                            'resveEndDe': str(end_date)
                        }
                        break
    DATASET['TARGET_DATA'] = TARGET_DATA
    run_reservation_bot(DATASET)
