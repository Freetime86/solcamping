import mangsang_data as md
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from user_agent import generate_user_agent
import pyautogui as py
import win32gui
import win32con
import requests
import time
import urllib3
import sys


# 시스템 설정
py.FAILSAFE = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main(DATASET):
    if DATASET['THREAD_FLAG']:
        THREAD_FLAG = 'MAIN'
        DATASET['THREAD_FLAG'] = False
        DATASET = message(DATASET, DATASET['BOT_NAME'] + ' START!')
        DATASET = login(DATASET)
    else:
        THREAD_FLAG = 'SUB'
        DATASET = message(DATASET, DATASET['BOT_NAME'] + ' START!')

    while True:
        if 'COOKIE' in DATASET:
            break
        else:
            message(DATASET, 'BOT WAITING')

    for target in DATASET['TARGET_LIST']:
        _wants = '지정안함'
        _range = '지정안함'
        if len(DATASET['ROOM_RANGE']) > 0:
            _range = str(DATASET['ROOM_RANGE']) + ')인실'
        if len(DATASET['ROOM_WANTS']) > 0:
            _wants = str(DATASET['ROOM_WANTS'])
        DATASET = message(DATASET, '입력정보 ' + str(target['site_name']) + ' => 탐색 범위 : (' + str(target['TARGET_NO']) + ') 지정 대상 (' + _range + ') 대상 정보 (' + _wants + ')')
        if not len(target['TARGET_NO']) == len(target['TARGET_TYPE']):
            print('대상 번호와 코드가 일치하지 않습니다.')
            exit()

    DATASET['CURRENT_PROCESS'] = 'main'
    while True:

        # MAIN SUB 프로세스 분기
        if THREAD_FLAG == 'MAIN':
            DATE = '1'
        elif THREAD_FLAG == 'SUB':
            if DATASET['TEMPORARY_HOLD']:
                while True:
                    DATASET = message(DATASET, ' 임시 점유 홀드 프로세스 기동 ' + DATASET['TARGET_MAX_CNT'] + ' ' + str(DATASET['FINAL_TYPE_NAME']) + ' => ' + str(DATASET['FINAL_FCLTYCODE']) + ' / ' + str(DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(DATASET['FINAL_RESVEENDDE']))
                    if 'preocpcEndDt' in DATASET['RESULT']:
                        message2(DATASET, '점유 시간 ' + DATASET['RESULT']['preocpcBeginDt'] + ' ~ ' + DATASET['RESULT']['preocpcEndDt'])
                        if DATASET['RESULT']['preocpcEndDt'] is not None:
                            DATASET['RESERVE_TIME'] = datetime.strptime(DATASET['FINAL_RESVEBEGINDE'], '%Y-%m-%d')
                            DATASET['LIVE_TIME'] = datetime.now()
                            if DATASET['FINAL_RESERVE'] and (DATASET['LIVE_TIME'] >= DATASET['OPEN_TIME'] or DATASET['RESERVE_TIME'] < DATASET['LIMIT_TIME']):
                                DATASET = message(DATASET, ' 확정 예약 진행 중... ' + DATASET['TARGET_MAX_CNT'] + ' ' + str(DATASET['FINAL_TYPE_NAME']) + ' => ' + str(DATASET['FINAL_FCLTYCODE']) + ' / ' + str(DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(DATASET['FINAL_RESVEENDDE']))
                                DATASET = final_reservation(DATASET)
                                if DATASET['RESULT']['status_code'] == 200:
                                    if 'message' in DATASET['RESULT']:
                                        print(DATASET, DATASET['RESULT']['message'])
                                        RESULT_TXT = DATASET['RESULT']['message']
                                        if '예약이 불가능한 시설입니다.' not in RESULT_TXT or '일시적인 장애로 예약신청이 정상 완료되지 않았습니다.' not in RESULT_TXT or '이미 완료된 예약입니다.' not in RESULT_TXT:
                                            message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + DATASET['TARGET_MAX_CNT'] + ' ' + str(DATASET['FINAL_FCLTYCODE']) + ' / ' + str(DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(DATASET['FINAL_RESVEENDDE']) + ' => ' + ' 예약이 완료되었습니다. ')
                                            #DATASET['SELECT_DATE'].pop('FINAL_RESVEBEGINDE', None)
                                            DATASET['TEMPORARY_HOLD'] = False
                                            exit()
                            else:
                                DATASET = get_facility(DATASET)
                        else:
                            DATASET = get_facility(DATASET)
                    else:
                        DATASET = get_facility(DATASET)


            if not DATASET['TEMPORARY_HOLD']:
                for target_type_list in DATASET['TARGET_LIST']:
                    idx = 0
                    for type_no in target_type_list['TARGET_NO']:
                        type_no_txt = type_no
                        if len(type_no) == 5:
                            type_no_txt = type_no[2:5]
                        if (type_no_txt in DATASET['ROOM_WANTS'] or DATASET['ROOM_WANTS'][0] == 'ALL') and type_no_txt not in DATASET['ROOM_EXPT']:
                            for begin_date in DATASET['SELECT_DATE']:
                                end_date = (datetime.strptime(begin_date, '%Y-%m-%d') + timedelta(days=DATASET['PERIOD'])).strftime("%Y-%m-%d")
                                if not DATASET['TEMPORARY_HOLD']:
                                    DATASET['FCLTYCODE'] = type_no
                                    DATASET['FCLTYTYCODE'] = target_type_list['TARGET_TYPE'][idx]
                                    DATASET['TARGET_MAX_CNT'] = target_type_list['TARGET_MAX_CNT'][idx] + '인실'
                                    DATASET['RESVENOCODE'] = target_type_list['resveNoCode']
                                    DATASET['TRRSRTCODE'] = target_type_list['trrsrtCode']
                                    DATASET['registerId'] = DATASET['CURRENT_USER']['rid']  # 로그인 아이디 초기값 하드코딩
                                    DATASET['rsvctmNm'] = DATASET['CURRENT_USER']['user_name']  # 사용자 이름 초기값 하드코딩
                                    DATASET['rsvctmEncptMbtlnum'] = DATASET['CURRENT_USER']['rphone']  # 전화번호
                                    DATASET['encptEmgncCttpc'] = DATASET['CURRENT_USER']['rphone']  # 긴급전화번호
                                    DATASET['FROM_DATE'] = begin_date
                                    DATASET['TO_DATE'] = end_date

                                    DATASET = get_facility(DATASET)
                                    if DATASET['TEMPORARY_HOLD']:
                                        DATASET['FINAL_TYPE_NAME'] = target_type_list['site_name']
                                        DATASET = message(DATASET, ' 임시 점유 완료 ' + DATASET['TARGET_MAX_CNT'] + ' ' + str(target_type_list['site_name']) + ' => ' + str(DATASET['FINAL_FCLTYCODE']) + ' / ' + str(DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(DATASET['FINAL_RESVEENDDE']))
                                        break
                                    else:
                                        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' 대상 SCAN 중 ' + DATASET['TARGET_MAX_CNT'] + ' ' + str(target_type_list['site_name']) + ' => ' + str(DATASET['FCLTYTYCODE']) + ' / ' + str(DATASET['FROM_DATE']) + ' ~ ' + str(DATASET['TO_DATE']))
                                        #DATASET = message(DATASET, ' 대상 SCAN 중 ' + str(target_type_list['site_name']) + ' => ' + str(DATASET['FCLTYTYCODE']))
                        idx = idx + 1
                        if DATASET['TEMPORARY_HOLD']:
                            break
                    if DATASET['TEMPORARY_HOLD']:
                        break


def get_facility(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(DATASET['TRRSRTCODE']),
        'fcltyCode': str(DATASET['FCLTYCODE']),
        'resveNoCode': str(DATASET['RESVENOCODE']),
        'resveBeginDe': str(DATASET['FROM_DATE']),
        'resveEndDe': str(DATASET['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False)
            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                result = {**dict_meta, **response.json()}
                if result['preocpcEndDt'] is not None:
                    DATASET['RESULT'] = {**dict_meta, **response.json()}
                    #필요 파라메터 맵핑
                    DATASET['FINAL_TRRSRTCODE'] = DATASET['RESULT']['trrsrtCode']
                    DATASET['FINAL_FCLTYCODE'] = DATASET['RESULT']['fcltyCode']
                    DATASET['FINAL_FCLTYTYCODE'] = DATASET['RESULT']['fcltyTyCode']
                    DATASET['FINAL_PREOCPCFCLTYCODE'] = DATASET['RESULT']['fcltyCode'] #fcltyCode 랑 같은 데이터로 추정 DATASET['RESULT']['preocpcFcltyCode']
                    DATASET['FINAL_RESVENOCODE'] = DATASET['RESULT']['resveNoCode']
                    DATASET['FINAL_RESVEBEGINDE'] = DATASET['RESULT']['resveBeginDe']
                    DATASET['FINAL_RESVEENDDE'] = DATASET['RESULT']['resveEndDe']
                    DATASET['FINAL_RESVENO'] = DATASET['RESULT']['resveNo']
                    DATASET['FINAL_REGISTERID'] = DATASET['registerId'] #로그인 아이디 초기값 하드코딩
                    DATASET['FINAL_RSVCTMNM'] = DATASET['rsvctmNm']     #사용자 이름 초기값 하드코딩
                    DATASET['FINAL_RSVCTMENCPTMBTLNUM'] = DATASET['rsvctmEncptMbtlnum'] #전화번호
                    DATASET['FINAL_ENCPTEMGNCCTTPC'] = DATASET['encptEmgncCttpc']       #긴급전화번호
                    DATASET['FINAL_RSVCTMAREA'] = '1005' #거주지역
                    DATASET['FINAL_ENTRCEDELAYCODE'] = '1004' #입실시간 해당없음.
                    DATASET['FINAL_DSPSNFCLTYUSEAT'] = 'N' #장애인시설 사용여부
                    DATASET['TEMPORARY_HOLD'] = True
                return DATASET
            else:  # 문자열 형태인 경우
                DATASET['RESULT'] = {**dict_meta, **{'text': response.text}}
                return DATASET
        except requests.exceptions.RequestException as ex:
            continue


def final_reservation(DATASET):
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertresve.do"
    dict_data = {
        'trrsrtCode': str(DATASET['FINAL_TRRSRTCODE']),
        'fcltyCode': str(DATASET['FINAL_FCLTYCODE']),
        'fcltyTyCode': str(DATASET['FINAL_FCLTYTYCODE']),
        'preocpcFcltyCode': str(DATASET['FINAL_PREOCPCFCLTYCODE']),
        'resveNoCode': '',
        'resveBeginDe': str(DATASET['FINAL_RESVEBEGINDE']),
        'resveEndDe': str(DATASET['FINAL_RESVEENDDE']),
        'resveNo': str(DATASET['FINAL_RESVENO']),
        'registerId': str(DATASET['FINAL_REGISTERID']),
        'rsvctmNm': str(DATASET['FINAL_RSVCTMNM']),
        'rsvctmEncptMbtlnum': str(DATASET['FINAL_RSVCTMENCPTMBTLNUM']),
        'encptEmgncCttpc': str(DATASET['FINAL_ENCPTEMGNCCTTPC']),
        'rsvctmArea': str(DATASET['FINAL_RSVCTMAREA']),
        'entrceDelayCode': str(DATASET['FINAL_ENTRCEDELAYCODE']),
        'dspsnFcltyUseAt': str(DATASET['FINAL_DSPSNFCLTYUSEAT'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False, headers={
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
                DATASET['RESULT'] = {**dict_meta, **response.json()}
                return DATASET
            else:  # 문자열 형태인 경우
                DATASET['RESULT'] = {**dict_meta, **{'text': response.text}}
                return DATASET
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def login(DATASET):
    DATASET['CURRENT_PROCESS'] = 'login'

    rid = DATASET['CURRENT_USER']['rid']
    rpwd = DATASET['CURRENT_USER']['rpwd']

    driver = DATASET['LOGIN_BROWSER']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)

    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(rid)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(rpwd)
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


def message(DATASET, text):
    DATASET['CURRENT_PROCESS'] = 'message'
    if DATASET['MESSAGE'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE'] = text
    return DATASET


def message2(DATASET, text):
    DATASET['CURRENT_PROCESS'] = 'message2'
    if DATASET['MESSAGE2'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE2'] = text
    return DATASET


def error(DATASET):
    DATASET['CURRENT_PROCESS'] = 'error'
    if DATASET['ERROR_MESSAGE'] != DATASET['ERROR_CODE']:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ######################  ERROR! ' + str(
            DATASET['ERROR_CODE']) + '  ######################')
        print(str(DATASET))
        DATASET['ERROR_MESSAGE'] = DATASET['ERROR_CODE']
        DATASET['CYCLE_ERR_CNT'] = 0
    else:
        DATASET['CYCLE_ERR_CNT'] = int(DATASET['CYCLE_ERR_CNT']) + 1
    return DATASET