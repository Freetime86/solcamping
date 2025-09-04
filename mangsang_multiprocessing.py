import mangsang_data as md
import mangsang_message as mm
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import threading
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from user_agent import generate_user_agent
import pyautogui as py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
import requests
import time
import urllib3
import logging
import sys



# 시스템 설정
py.FAILSAFE = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
lock = threading.Lock()

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

logger = logging.getLogger()

class Worker(threading.Thread):
    def __init__(self, first):
        self.DATASET = first
        super().__init__()

    def run(self):
        threading.Thread(target=main(self.DATASET))


def main(DATASET):
    BOT_DATASET = DATASET.copy()
    BOT_DATASET['BOT_NAME'] = DATASET['BOT_NAME']
    BOT_DATASET['BOT_ID'] = DATASET['BOT_ID']
    if DATASET['THREAD_FLAG']:
        DATASET['THREAD_FLAG'] = False
        logger.info('SYSTEM LOADING....')
        # 시스템 기본 수행작업 필수
        if not md.check(DATASET):
            exit()
        DATASET = login(DATASET)
        THREAD_FLAG = 'MAIN'
    else:
        THREAD_FLAG = 'SUB'

    if THREAD_FLAG == 'MAIN':
        mm.message(DATASET, '예약자 : ' + str(DATASET['CURRENT_USER']['user_name']) + ' / 유저 NO:' + str(
            DATASET['USER_NO']) + ' (' + str(DATASET['PERIOD']) + ')박')
        mm.message(DATASET,
                   '아이디 : ' + str(DATASET['CURRENT_USER']['rid']) + ' / 패스워드 : ' + str(DATASET['CURRENT_USER']['rpwd']))
        mm.message(DATASET,
                   '지정일자 : ' + str(DATASET['SELECT_DATE']))
        _wants = '지정안함'
        _range = '지정안함'
        if len(DATASET['ROOM_RANGE']) > 0:
            _range = str(DATASET['ROOM_RANGE']) + ' 인실'
        if len(DATASET['ROOM_WANTS']) > 0:
            _wants = str(DATASET['ROOM_WANTS'])
        for target in DATASET['TARGET_LIST']:
            DATASET = mm.message(DATASET,
                                 '입력정보 ' + str(target['site_name']) + ' => 탐색 범위 : ' + str(DATASET['SEARCH_RANGE']))
            if not len(target['TARGET_NO']) == len(target['TARGET_TYPE']):
                print('대상 번호와 코드가 일치하지 않습니다.')
                exit()
        DATASET['RANGE_TARGETS'] = _range
        DATASET['SCAN_TARGETS'] = _wants

    while True:
        if 'COOKIE' in DATASET:
            break

    # 경과 시간 계산
    start_time = time.time()
    run_cnt = 0

    #SESSION 생성
    MY_PROXY = BOT_DATASET["{}_PROXY".format(BOT_DATASET['BOT_NAME'])]
    SESSION = requests.Session()
    SESSION.proxies.update(MY_PROXY)
    SESSION.headers.update({
        "User-Agent": md.random_useragent()
    })

    BOT_DATASET['SESSION'] = SESSION

    while True:
        try:
            if BOT_DATASET['TEMPORARY_HOLD']:
                if BOT_DATASET['BOT_ID'] == DATASET['POOL'][0] and DATASET['POOL_DEFINED'][0] == BOT_DATASET['BOT_NAME']:
                    while not BOT_DATASET['JUST_RESERVED']:
                        if 'preocpcEndDt' in BOT_DATASET['RESULT']:
                            if BOT_DATASET['RESULT']['preocpcEndDt'] is not None:
                                BOT_DATASET = mm.message5(BOT_DATASET, BOT_DATASET['BOT_NAME'] +' ' + BOT_DATASET['site_name'] + ' ' + BOT_DATASET['TARGET_MAX_CNT'] + '인실 ' +
                                                                 '점유 시간 ' + BOT_DATASET['RESULT']['preocpcBeginDt'] + ' ~ ' +
                                                      BOT_DATASET['RESULT']['preocpcEndDt'])
                                CURRENT_TIME_STR = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                CURRENT_TIME = datetime.strptime(CURRENT_TIME_STR, '%Y-%m-%d %H:%M:%S')
                                IN_RESERVED_TIME = datetime.strptime(BOT_DATASET['RESULT']['preocpcEndDt'],
                                                                     '%Y-%m-%d %H:%M:%S') - timedelta(seconds=99999)
                                if CURRENT_TIME >= IN_RESERVED_TIME or BOT_DATASET['STAND_BY_TIME'] is None:
                                    if BOT_DATASET['STAND_BY_TIME'] is None:
                                        BOT_DATASET['RESERVE_TIME'] = datetime.strptime(BOT_DATASET['FINAL_RESVEBEGINDE'],
                                                                                    '%Y-%m-%d')
                                        BOT_DATASET['LIVE_TIME'] = datetime.now() + timedelta(days=30)
                                        if BOT_DATASET['FINAL_RESERVE'] and (BOT_DATASET['LIVE_TIME'] >= BOT_DATASET['OPEN_TIME'] >= BOT_DATASET['RESERVE_TIME'] or BOT_DATASET['RESERVE_TIME'] < BOT_DATASET['LIMIT_TIME']):
                                            if not BOT_DATASET['TRY_RESERVE']:
                                                #if '임시 점유 실패' not in str(BOT_DATASET['MESSAGE']):
                                                BOT_DATASET = mm.message(BOT_DATASET, BOT_DATASET['BOT_NAME'] + ' ' + BOT_DATASET['site_name'] +
                                                                     ' ' +
                                                                     '확정 예약 진행 중... ' + BOT_DATASET[
                                                                         'TARGET_MAX_CNT'] + '인실 ' + str(
                                                                         BOT_DATASET['FINAL_TYPE_NAME']) + ' => ' + str(
                                                                         BOT_DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                                                                         BOT_DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                                                         BOT_DATASET['FINAL_RESVEENDDE']))
                                                BOT_DATASET = final_reservation(DATASET, BOT_DATASET)
                                                if BOT_DATASET['FINAL_RESULT']['status_code'] == 200:
                                                    if 'message' in BOT_DATASET['FINAL_RESULT']:
                                                        RESULT_TXT = BOT_DATASET['FINAL_RESULT']['message']
                                                        if RESULT_TXT == '예약신청이 정상적으로 완료되었습니다.':
                                                            BOT_DATASET = mm.message(BOT_DATASET, BOT_DATASET['BOT_NAME'] +
                                                                     ' ' +
                                                                     '[' + str(
                                                                BOT_DATASET['FINAL_TYPE_NAME']) + '] ' + BOT_DATASET[
                                                                                     'TARGET_MAX_CNT'] + '인실 ' + str(
                                                                BOT_DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                                                                BOT_DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                                                BOT_DATASET[
                                                                    'FINAL_RESVEENDDE']) + ' => ' + ' 예약이 완료되었습니다. ')
                                                            BOT_DATASET['TEMPORARY_HOLD'] = False
                                                            DATASET['TEMPORARY_HOLD'] = False
                                                            BOT_DATASET['JUST_RESERVED'] = True
                                                            DATASET['POOL'].remove(BOT_DATASET['FINAL_FCLTYCODE'])
                                                            DATASET['POOL_DEFINED'].remove(BOT_DATASET['FINAL_FCLTYCODE'])
                                                            delete_occ(DATASET)
                                                            if DATASET['SYSTEM_OFF']:
                                                                exit()
                                                        else:
                                                            if '예약가능 시간은' in BOT_DATASET['FINAL_RESULT']['message']:
                                                                BOT_DATASET['STAND_BY_TIME'] = datetime.strptime(
                                                                    BOT_DATASET['FINAL_RESULT']['message'][26:45],
                                                                    '%Y-%m-%d %H:%M:%S') - timedelta(seconds=2)
                                                                BOT_DATASET = mm.message7(BOT_DATASET, BOT_DATASET['BOT_NAME'] + ' ' + BOT_DATASET['site_name'] + ' ' + BOT_DATASET['FINAL_FCLTYCODE'] +
                                                                     ' ' + BOT_DATASET['FINAL_RESULT'][
                                                                    'message'] + ' 가능 시간까지 대기상태로 진입합니다.')
                                                            elif '일시적인 장애로' in BOT_DATASET['FINAL_RESULT']['message'] :
                                                                BOT_DATASET = mm.message8(BOT_DATASET, BOT_DATASET['BOT_NAME'] + ' ' + BOT_DATASET['site_name'] + ' ' + BOT_DATASET['FINAL_FCLTYCODE'] +
                                                                     ' ' + '(' + BOT_DATASET['FINAL_RESULT'][
                                                                                          'message'] + ') 다음과 같은 사유로 예약시도를 계속 합니다.')
                                                                BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                                                                DATASET['TEMPORARY_HOLD'] = False
                                                            elif '예약이 불가능한' in BOT_DATASET['FINAL_RESULT']['message']:
                                                                BOT_DATASET = mm.message8(BOT_DATASET, BOT_DATASET['BOT_NAME'] + ' ' + BOT_DATASET['site_name'] + ' ' + BOT_DATASET['FINAL_FCLTYCODE'] +
                                                                                          ' ' + '(' +
                                                                                          BOT_DATASET['FINAL_RESULT'][
                                                                                              'message'] + ') 다음과 같은 사유로 재 탐색을 진행 합니다.')
                                                                BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                                                                DATASET['TEMPORARY_HOLD'] = False
                                                            elif '비정상적인 접근' in BOT_DATASET['FINAL_RESULT']['message']:
                                                                BOT_DATASET = mm.message8(BOT_DATASET, BOT_DATASET['BOT_NAME'] + ' ' + BOT_DATASET['site_name'] + ' ' + BOT_DATASET['FINAL_FCLTYCODE'] +
                                                                                          ' ' + '(' +
                                                                                          BOT_DATASET['FINAL_RESULT'][
                                                                                              'message'] + ') 다음과 같은 사유로 임시점유 해제 후 재탐색 합니다.')
                                                                BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                                                                TIME_STR = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                                TIME = datetime.strptime(TIME_STR, '%Y-%m-%d %H:%M:%S')
                                                                DATASET['CHECK_TIME'] = TIME
                                                                if DATASET['DELAY_TIME'] < DATASET['CHECK_TIME']:
                                                                    delete_occ(DATASET)
                                                                DATASET['TEMPORARY_HOLD'] = False
                                                            else:
                                                                DATASET['TEMPORARY_HOLD'] = False
                                                                BOT_DATASET['TEMPORARY_HOLD'] = False
                                                                mm.message(BOT_DATASET, BOT_DATASET['BOT_NAME'] +
                                                                     ' ' + BOT_DATASET['FINAL_RESULT']['message'])
                                                                break
                                                    else:
                                                        BOT_DATASET = final_reservation(DATASET, BOT_DATASET)
                                                else:
                                                    mm.message(BOT_DATASET, BOT_DATASET['BOT_NAME'] + ' ' + BOT_DATASET['FINAL_FCLTYCODE'] + ' Server response failed (취소 딜레이 예약 오류)')
                                                    delete_occ(DATASET)
                                                    BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                                                    DATASET['TEMPORARY_HOLD'] = False
                                        else:
                                            if CURRENT_TIME >= IN_RESERVED_TIME:
                                                BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                                            DATASET['TEMPORARY_HOLD'] = False

                                    else:
                                        if CURRENT_TIME >= IN_RESERVED_TIME:
                                            BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                                        DATASET['TEMPORARY_HOLD'] = False
                                #else:
                                #    if CURRENT_TIME >= BOT_DATASET['STAND_BY_TIME']:
                                #        BOT_DATASET['STAND_BY_TIME'] = None
                            else:
                                BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                                DATASET['TEMPORARY_HOLD'] = False
                        else:
                            BOT_DATASET = get_facility_relay(DATASET, BOT_DATASET)
                            DATASET['TEMPORARY_HOLD'] = False
            else:
                if BOT_DATASET['TARGET_MAX_CNT'] == '0':
                    copy_max_no = '전체이용'
                else:
                    copy_max_no = BOT_DATASET['TARGET_MAX_CNT']
                type_no_txt = BOT_DATASET['BOT_NAME'].split('_')[0]

                for begin_date in DATASET['SELECT_DATE']:
                    for PERIOD in DATASET['PERIOD']:
                        end_date = (datetime.strptime(begin_date, '%Y-%m-%d') + timedelta(days=int(PERIOD))).strftime("%Y-%m-%d")
                        if not BOT_DATASET['TEMPORARY_HOLD']:
                            BOT_DATASET['FCLTYCODE'] = type_no_txt
                            BOT_DATASET['FCLTYTYCODE'] = BOT_DATASET['TARGET_TYPE']
                            BOT_DATASET['TARGET_MAX_CNT'] = copy_max_no
                            BOT_DATASET['FINAL_TYPE_NAME'] = BOT_DATASET['site_name']
                            BOT_DATASET['RESVENOCODE'] = BOT_DATASET['resveNoCode']
                            BOT_DATASET['TRRSRTCODE'] = BOT_DATASET['trrsrtCode']
                            BOT_DATASET['FROM_DATE'] = begin_date
                            BOT_DATASET['TO_DATE'] = end_date

                            BOT_DATASET = get_facility(DATASET, BOT_DATASET)
                            if BOT_DATASET['TEMPORARY_HOLD'] and DATASET['POOL_DEFINED'][0] == BOT_DATASET['BOT_NAME']:
                                BOT_DATASET = mm.message4(BOT_DATASET, BOT_DATASET['BOT_NAME'] +
                                                             ' ' + '임시 점유 완료 ' + BOT_DATASET[
                                    'TARGET_MAX_CNT'] + '인실 ' + BOT_DATASET['site_name'] + ' => ' + str(
                                    BOT_DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                                    BOT_DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                    BOT_DATASET['FINAL_RESVEENDDE']))
                                break
                            else:
                                if not BOT_DATASET['TEMPORARY_HOLD']:
                                    elapsed_time = time.time() - start_time  # 경과된 시간 계산
                                    if elapsed_time >= 3600 * run_cnt:  # 3600초 == 1시간
                                        #BOT_DATASET = mm.message(BOT_DATASET, BOT_DATASET['BOT_NAME'] +
                                        #                         ' ' +
                                        #                  '탐색 지정 대상 ' + BOT_DATASET['site_name'] + ' ' + type_no_txt + ' ' +
                                        #                  BOT_DATASET[
                                        #                      'TARGET_MAX_CNT'] + '인실' + ' / 임시점유 예약을 시도 합니다.. ' + ' / 경과 시간 : ' + str(
                                        #                      run_cnt) + '시간')
                                        run_cnt = run_cnt + 1

                                    #if DATASET['SHOW_WORKS']:
                                    #    #print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' 대상 SCAN 중 ' + BOT_DATASET['TARGET_MAX_CNT'] + ' ' + str(target_type_list['site_name']) + ' => ' + str(BOT_DATASET['FCLTYTYCODE']) + ' / ' + str(BOT_DATASET['FROM_DATE']) + ' ~ ' + str(BOT_DATASET['TO_DATE']))
                                    #    DATASET = mm.message2(DATASET,
                                    #                       str(BOT_DATASET['BOT_NAME']) + ' 대상 SCAN 중 ' + copy_max_no + '인실 ' + BOT_DATASET[
                                    #                           'site_name'] + ' => ' + str(
                                    #                           type_no_txt) + ' / ' + str(
                                    #                           begin_date) + ' ~ ' + str(
                                    #                           end_date) + ' (' + str(PERIOD) + ')박')
                        if BOT_DATASET['TEMPORARY_HOLD']:
                            break
        except Exception as ex:
            print(traceback.format_exc())
            mm.message(BOT_DATASET, ' EXCEPTION!! ====>  ' + str(ex))
            error(BOT_DATASET)
            continue


def get_facility(DATASET, BOT_DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(BOT_DATASET['TRRSRTCODE']),
        'fcltyCode': str(BOT_DATASET['FCLTYCODE']),
        'resveNoCode': str(BOT_DATASET['RESVENOCODE']),
        'resveBeginDe': str(BOT_DATASET['FROM_DATE']),
        'resveEndDe': str(BOT_DATASET['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            if not DATASET['TEMPORARY_HOLD'] and BOT_DATASET['BOT_ID'] not in DATASET['POOL']:
                with lock:
                    response = BOT_DATASET['SESSION'].post(url=url, data=dict_data, cookies=DATASET['COOKIE'],timeout=10)
                if 'Content-Type' in response.headers:
                    dict_meta = {'status_code': response.status_code, 'ok': response.ok,
                                 'encoding': response.encoding,
                                 'Content-Type': response.headers['Content-Type'],
                                 'cookies': response.cookies}
                    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                        BOT_DATASET['RELAY_RESULT'] = {**dict_meta, **response.json()}
                        if BOT_DATASET['RELAY_RESULT']['status_code'] == 200 and BOT_DATASET['RELAY_RESULT']['preocpcEndDt'] is not None and not DATASET['TEMPORARY_HOLD']:
                            DATASET['TEMPORARY_HOLD'] = True
                            BOT_DATASET['TEMPORARY_HOLD'] = True
                            BOT_DATASET['DICT_DATA'] = dict_data
                            BOT_DATASET['registerId'] = BOT_DATASET['CURRENT_USER']['rid']  # 로그인 아이디 초기값 하드코딩
                            BOT_DATASET['rsvctmNm'] = BOT_DATASET['CURRENT_USER']['user_name']  # 사용자 이름 초기값 하드코딩
                            BOT_DATASET['rsvctmEncptMbtlnum'] = BOT_DATASET['CURRENT_USER']['rphone']  # 전화번호
                            BOT_DATASET['encptEmgncCttpc'] = BOT_DATASET['CURRENT_USER']['rphone']  # 긴급전화번호
                            BOT_DATASET['RESULT'] = BOT_DATASET['RELAY_RESULT']
                            #필요 파라메터 맵핑
                            BOT_DATASET['FINAL_TRRSRTCODE'] = BOT_DATASET['RESULT']['trrsrtCode']
                            BOT_DATASET['FINAL_FCLTYCODE'] = BOT_DATASET['RESULT']['fcltyCode']
                            #한옥만 기존 faltycode를 사용한다. 매칭되지 않음. 망상만든 솔루션 쓰레기.
                            if BOT_DATASET['FINAL_TYPE_NAME'] == '전통한옥':
                                BOT_DATASET['FINAL_FCLTYCODE'] = BOT_DATASET['FCLTYCODE']
                            if BOT_DATASET['BOT_ID'] not in DATASET['POOL']:
                                DATASET['POOL'].append(BOT_DATASET['BOT_ID'])
                                DATASET['POOL_DEFINED'].append(BOT_DATASET['BOT_NAME'])
                            BOT_DATASET['FINAL_FCLTYTYCODE'] = BOT_DATASET['RESULT']['fcltyTyCode']
                            BOT_DATASET['FINAL_PREOCPCFCLTYCODE'] = BOT_DATASET['RESULT'][
                                'fcltyCode']  #fcltyCode 랑 같은 데이터로 추정 BOT_DATASET['RESULT']['preocpcFcltyCode']
                            BOT_DATASET['FINAL_RESVENOCODE'] = BOT_DATASET['RESULT']['resveNoCode']
                            BOT_DATASET['FINAL_RESVEBEGINDE'] = BOT_DATASET['RESULT']['resveBeginDe']
                            BOT_DATASET['FINAL_RESVEENDDE'] = BOT_DATASET['RESULT']['resveEndDe']
                            BOT_DATASET['FINAL_RESVENO'] = BOT_DATASET['RESULT']['resveNo']
                            BOT_DATASET['FINAL_REGISTERID'] = BOT_DATASET['registerId']  #로그인 아이디 초기값 하드코딩
                            BOT_DATASET['FINAL_RSVCTMNM'] = BOT_DATASET['rsvctmNm']  #사용자 이름 초기값 하드코딩
                            BOT_DATASET['FINAL_RSVCTMENCPTMBTLNUM'] = BOT_DATASET['rsvctmEncptMbtlnum']  #전화번호
                            BOT_DATASET['FINAL_ENCPTEMGNCCTTPC'] = BOT_DATASET['encptEmgncCttpc']  #긴급전화번호
                            BOT_DATASET['FINAL_RSVCTMAREA'] = '1005'  #거주지역
                            BOT_DATASET['FINAL_ENTRCEDELAYCODE'] = '1004'  #입실시간 해당없음.
                            BOT_DATASET['FINAL_DSPSNFCLTYUSEAT'] = 'N'  #장애인시설 사용여부
                            BOT_DATASET['JUST_RESERVED'] = False
                        else:
                            DATASET['TEMPORARY_HOLD'] = False
                    #else:  # 문자열 형태인 경우
                        #BOT_DATASET['RESULT'] = {**dict_meta, **{'text': response.text}}
                        #return BOT_DATASET
                else:
                    DATASET['TEMPORARY_HOLD'] = False
                    print('error = > ' + str(response))
                    login(DATASET)
            return BOT_DATASET
        except requests.exceptions.RequestException as ex:
            continue


def get_facility_relay(DATASET, BOT_DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    response = ''
    while response == '':
        try:
            if DATASET['RELAY_OUTPUT'] != '':
                DATASET['RELAY_OUTPUT'] = ''
                response = BOT_DATASET['SESSION'].post(url=url, data=BOT_DATASET['DICT_DATA'], cookies=DATASET['COOKIE'], verify=False)
                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    BOT_DATASET['RELAY_RESULT'] = {**dict_meta, **response.json()}
                    if BOT_DATASET['RELAY_RESULT']['status_code'] == 200 and BOT_DATASET['RELAY_RESULT']['preocpcEndDt'] is not None:
                        TIME_STR = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        TIME = datetime.strptime(TIME_STR, '%Y-%m-%d %H:%M:%S')
                        DATASET['DELAY_TIME'] = TIME + timedelta(seconds=1)
                        BOT_DATASET['RESULT'] = BOT_DATASET['RELAY_RESULT']
                        BOT_DATASET['TEMPORARY_HOLD'] = True
                        #필요 파라메터 맵핑
                        BOT_DATASET['FINAL_TRRSRTCODE'] = BOT_DATASET['RESULT']['trrsrtCode']
                        BOT_DATASET['FINAL_FCLTYCODE'] = BOT_DATASET['RESULT']['fcltyCode']
                        BOT_DATASET['FINAL_FCLTYTYCODE'] = BOT_DATASET['RESULT']['fcltyTyCode']
                        # 한옥만 기존 faltycode를 사용한다. 매칭되지 않음. 망상만든 솔루션 쓰레기.
                        if BOT_DATASET['FINAL_TYPE_NAME'] == '전통한옥':
                            BOT_DATASET['FINAL_FCLTYCODE'] = BOT_DATASET['FCLTYCODE']
                        BOT_DATASET['FINAL_PREOCPCFCLTYCODE'] = BOT_DATASET['RESULT'][
                            'fcltyCode']  #fcltyCode 랑 같은 데이터로 추정 BOT_DATASET['RESULT']['preocpcFcltyCode']
                        BOT_DATASET['FINAL_RESVENOCODE'] = BOT_DATASET['RESULT']['resveNoCode']
                        BOT_DATASET['FINAL_RESVEBEGINDE'] = BOT_DATASET['RESULT']['resveBeginDe']
                        BOT_DATASET['FINAL_RESVEENDDE'] = BOT_DATASET['RESULT']['resveEndDe']
                        BOT_DATASET['FINAL_RESVENO'] = BOT_DATASET['RESULT']['resveNo']
                        #BOT_DATASET['FINAL_REGISTERID'] = BOT_DATASET['registerId']  #로그인 아이디 초기값 하드코딩
                        #BOT_DATASET['FINAL_RSVCTMNM'] = BOT_DATASET['rsvctmNm']  #사용자 이름 초기값 하드코딩
                        #BOT_DATASET['FINAL_RSVCTMENCPTMBTLNUM'] = BOT_DATASET['rsvctmEncptMbtlnum']  #전화번호
                        #BOT_DATASET['FINAL_ENCPTEMGNCCTTPC'] = BOT_DATASET['encptEmgncCttpc']  #긴급전화번호
                        #BOT_DATASET['FINAL_RSVCTMAREA'] = '1005'  #거주지역
                        #BOT_DATASET['FINAL_ENTRCEDELAYCODE'] = '1004'  #입실시간 해당없음.
                        #BOT_DATASET['FINAL_DSPSNFCLTYUSEAT'] = 'N'  #장애인시설 사용여부
                        BOT_DATASET['JUST_RESERVED'] = False
                        BOT_DATASET['STAND_BY_TIME'] = None
                        BOT_DATASET = mm.message4(BOT_DATASET, BOT_DATASET['BOT_NAME'] +
                                                                 ' ' + '임시 점유 완료 ' + BOT_DATASET[
                                        'TARGET_MAX_CNT'] + '인실 ' + BOT_DATASET['site_name'] + ' => ' + str(
                                        BOT_DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                                        BOT_DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                        BOT_DATASET['FINAL_RESVEENDDE']))
                    else:
                        BOT_DATASET = mm.message5(BOT_DATASET, BOT_DATASET['BOT_NAME'] +
                                                             ' ' + '임시 점유 실패 예약 시도를 계속 합니다.')
                        #delete_occ(DATASET)
                    return BOT_DATASET
                else:  # 문자열 형태인 경우
                    BOT_DATASET['RESULT'] = {**dict_meta, **{'text': response.text}}
                    print('error = > ' + str(response))
                    login(DATASET)
                DATASET['RELAY_OUTPUT'] = 'DONE'
        except requests.exceptions.RequestException as ex:
            continue
        finally:
            DATASET['RELAY_OUTPUT'] = 'DONE'


def final_reservation(DATASET, BOT_DATASET):
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertresve.do"
    dict_data = {
        'trrsrtCode': str(BOT_DATASET['FINAL_TRRSRTCODE']),
        'fcltyCode': str(BOT_DATASET['FINAL_FCLTYCODE']),
        'fcltyTyCode': str(BOT_DATASET['FINAL_FCLTYTYCODE']),
        'preocpcFcltyCode': str(BOT_DATASET['FINAL_PREOCPCFCLTYCODE']),
        'resveNoCode': '',
        'resveBeginDe': str(BOT_DATASET['FINAL_RESVEBEGINDE']),
        'resveEndDe': str(BOT_DATASET['FINAL_RESVEENDDE']),
        'resveNo': str(BOT_DATASET['FINAL_RESVENO']),
        'registerId': str(BOT_DATASET['FINAL_REGISTERID']),
        'rsvctmNm': str(BOT_DATASET['FINAL_RSVCTMNM']),
        'rsvctmEncptMbtlnum': str(BOT_DATASET['FINAL_RSVCTMENCPTMBTLNUM']),
        'encptEmgncCttpc': str(BOT_DATASET['FINAL_ENCPTEMGNCCTTPC']),
        'rsvctmArea': str(BOT_DATASET['FINAL_RSVCTMAREA']),
        'entrceDelayCode': str(BOT_DATASET['FINAL_ENTRCEDELAYCODE']),
        'dspsnFcltyUseAt': str(BOT_DATASET['FINAL_DSPSNFCLTYUSEAT'])
    }
    response = ''
    while response == '':
        try:
            if BOT_DATASET['TEMPORARY_HOLD']:
                response = BOT_DATASET['SESSION'].post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False, headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Connection': 'keep-alive',
                    'Content-Length': '320',
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

                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    BOT_DATASET['FINAL_RESULT'] = {**dict_meta, **response.json()}
                    return BOT_DATASET
                else:  # 문자열 형태인 경우
                    BOT_DATASET['FINAL_RESULT'] = {**dict_meta, **{'text': response.text}}
                    return BOT_DATASET
            return BOT_DATASET
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def delete_occ(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_deletePreOcpcInfo.do"
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, cookies=DATASET['COOKIE'], verify=False)
        except requests.exceptions.RequestException as ex:
            continue

def login(DATASET):
    DATASET = mm.message(DATASET, 'LOGIN PROCESSING!!')
    DATASET['CURRENT_PROCESS'] = 'login'

    rid = DATASET['CURRENT_USER']['rid']
    rpwd = DATASET['CURRENT_USER']['rpwd']

    driver = DATASET['LOGIN_BROWSER']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    try:
        driver.get(url)
    finally:
        driver.get(url)

    for i in range(5):
        driver.refresh()
        time.sleep(0.5)
    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(rid)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(rpwd)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "banner")))
    CHECK_LOAD = False
    _bannerList = []
    for i in range(5):
        driver.refresh()
        time.sleep(0.5)
    while not CHECK_LOAD:
        try:
            _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
            isDone = driver.find_elements(By.CLASS_NAME, 'jsBtnClose2')
            if len(isDone) == len(_bannerList):
                CHECK_LOAD = True
                for banner in _bannerList:
                    banner.find_element(By.TAG_NAME, 'button').click()
        except Exception:
            CHECK_LOAD = False
            continue

    DATASET['LOGIN_TIME'] = time.time()

    _cookies = DATASET['LOGIN_BROWSER'].get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
    DATASET['COOKIE'] = cookie_dict

    return DATASET


def pingpong1_login(DATASET):
    DATASET['CURRENT_PROCESS'] = 'login1'

    prid1 = DATASET['PINGPONG_USER1']['rid']
    prpwd1 = DATASET['PINGPONG_USER1']['rpwd']

    driver = DATASET['LOGIN_BROWSER1']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)

    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(prid1)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(prpwd1)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "banner")))
    CHECK_LOAD = False
    _bannerList = []
    while not CHECK_LOAD:
        try:
            _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
            isDone = driver.find_elements(By.CLASS_NAME, 'jsBtnClose2')
            if len(isDone) == len(_bannerList):
                CHECK_LOAD = True
                for banner in _bannerList:
                    banner.find_element(By.TAG_NAME, 'button').click()
        except Exception:
            CHECK_LOAD = False
            continue

    DATASET['LOGIN_TIME1'] = time.time()

    _cookies = DATASET['LOGIN_BROWSER1'].get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
    DATASET['COOKIE1'] = cookie_dict

    return DATASET


def pingpong2_login(DATASET):
    DATASET['CURRENT_PROCESS'] = 'login2'

    prid2 = DATASET['PINGPONG_USER2']['rid']
    prpwd2 = DATASET['PINGPONG_USER2']['rpwd']

    driver = DATASET['LOGIN_BROWSER2']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)

    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(prid2)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(prpwd2)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "banner")))
    CHECK_LOAD = False
    _bannerList = []
    while not CHECK_LOAD:
        try:
            _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
            isDone = driver.find_elements(By.CLASS_NAME, 'jsBtnClose2')
            if len(isDone) == len(_bannerList):
                CHECK_LOAD = True
                for banner in _bannerList:
                    banner.find_element(By.TAG_NAME, 'button').click()
        except Exception:
            CHECK_LOAD = False
            continue

    DATASET['LOGIN_TIME2'] = time.time()

    _cookies = DATASET['LOGIN_BROWSER2'].get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
    DATASET['COOKIE2'] = cookie_dict

    return DATASET


def get_driver():
    chrome_options = Options()
    user_data_dir = tempfile.mkdtemp()  # 고유한 임시 디렉토리
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    return webdriver.Chrome(options=chrome_options)


def error(BOT_DATASET):
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ERROR INFO ::: ' + str(BOT_DATASET))
