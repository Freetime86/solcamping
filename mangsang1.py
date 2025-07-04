from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from user_agent import generate_user_agent, generate_navigator
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pygetwindow as gw
import pyautogui as py
import pywinauto
from pywinauto.keyboard import send_keys
from pywinauto import Desktop
import numpy as np
import cv2
import win32gui
import win32con
import requests
import time
import json
import threading
import sys
import urllib3
import pytesseract

# 시스템 설정
py.FAILSAFE = False
options = Options()
options.add_experimental_option("detach", True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
global try_cnt

machine = 1  # 예약 머신 숫자 높을 수록 압도적이지만, 서버 박살낼 수가 있음.. 조심
time_cut = 5  # 머신 시작 간격
period = 3  # 연박 수
delay = 1
night_delay = 5  # 모니터링 리프레시 속도
room_exception = []
# 든바다
# 2인실 ['104','105', '107', '108', '113', '114', '117', '118']
# 4인실 ['120', '121', '122', '123', '103', '109', '116', '102', '111']
# 6인실 ['112', '115', '119']
# 8인실 ['101', '110']
# 10인실 ['106']
# 난바다
# 4인실 ['103', '104', '107', '108', '111', '112']
# 6인실 ['105', '102', '110', '114']
# 8인실 ['101', '109', '113']
# 10인실 ['106', '115']
# 허허바다
# 2인실 ['104','105', '107', '108', '113', '114', '117', '118']
# 4인실 ['106', '107', '104', '103']
# 6인실 ['105']
# 8인실 ['102']
# 10인실 ['101', '108']
# 자동차야영장 1~41번까지
# 앞열 5~13
# 취사장 가까운 열 1~4
# room_want = ['115']
# room_want = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
#room_want = ['101', '110', '109', '113', '106', '115', '102', '108']
room_want = []
room_selt = []

sel_year_list = ['2025']
sel_month_list = ['08']
sel_date_list = ['04']
site = '6'

continue_work = False

current_room = '0'
user_type = 2  # 사용자 정보 세팅
MODE_LIVE = False
MODE_SPOT = False   #SPOT 모드는 재예약할 떄 사용하는 FUNCTION 취소중 건 뚫을 때도 사용

rpwd = ''
rid = ''

# 01082095418
# 01026585418
# 01048325418
# 01021535418
# 01021655418
# 01021177488
# 01099898806
if user_type == 0:
    user_name = '조수윤'
    rpwd = 'CJSWOsla86!@123'
    rid = 'jsy3033'
elif user_type == 1:
    user_name = '권혁인'
    rpwd = 'khi831883!'
    rid = 'sochi007'
elif user_type == 2:
    user_name = '김계자'
    rpwd = 'cjswosla86'
    rid = 'psm07051'
elif user_type == 3:
    user_name = '박응순'
    rpwd = 'cjswosla86'
    rid = 'parksi'
elif user_type == 4:
    user_name = '박현정'
    rpwd = 'khi831883!'
    rid = 'fpahs414'
elif user_type == 5:
    user_name = '박상민'
    rpwd = 'CJSWOsla86!@'
    rid = 'psm0705'
elif user_type == 6:
    user_name = '윤민주'
    rpwd = 'cca1174848'
    rid = 'jsy3038'
else:
    print('User type이 없습니다. 종료합니다')
    exit()

DATASET = {
    'MODE_LIVE': MODE_LIVE,
    'TEMPORARY_HOLD': False,
    'trrsrtCode': '1000',
    'ROOM_WANT': room_want,
    'ROOM_SELT': room_selt,
    'ERROR_MESSAGE': '',
    'ERROR_CODE': '',
    'MESSAGE': '',
    'PERIOD': period,
    'SITE': site,
    'AVAILABLE_ROOMS': [],
    'CANCELING_ROOMS': [],
    'FINAL_ROOM_NAME': [],
    'ROOM_NAMES': [],
    'TIME_DELAY': 0,
    'CYCLE_ERR_CNT': 0
}

if DATASET['SITE'] == '1':
    DATASET['SITE_TEXT'] = '든바다'
    DATASET['faciltyNo'] = '1300'
    DATASET['resveNoCode'] = 'MA'
elif DATASET['SITE'] == '2':
    DATASET['SITE_TEXT'] = '난바다'
    DATASET['faciltyNo'] = '1400'
    DATASET['resveNoCode'] = 'MI'
elif DATASET['SITE'] == '3':
    DATASET['SITE_TEXT'] = '허허바다'
    DATASET['faciltyNo'] = '1500'
    DATASET['resveNoCode'] = 'MB'
elif DATASET['SITE'] == '4':
    DATASET['SITE_TEXT'] = '전통한옥'
    DATASET['faciltyNo'] = '1100'
    DATASET['resveNoCode'] = 'HA'
elif DATASET['SITE'] == '5':
    DATASET['SITE_TEXT'] = '캐라반'
    DATASET['faciltyNo'] = '1700'
    DATASET['resveNoCode'] = 'BA'
elif DATASET['SITE'] == '6':
    DATASET['SITE_TEXT'] = '자동차캠핑장'
    DATASET['faciltyNo'] = '1600'
    DATASET['resveNoCode'] = 'RR'
elif DATASET['SITE'] == '7':  # 2인
    DATASET['SITE_TEXT'] = '글램핑'
    DATASET['faciltyNo'] = '1801'
    DATASET['resveNoCode'] = 'LB'
elif DATASET['SITE'] == '8':  # 4인
    DATASET['SITE_TEXT'] = '글램핑'
    DATASET['faciltyNo'] = '1802'
    DATASET['resveNoCode'] = 'LA'
elif DATASET['SITE'] == '9':
    DATASET['SITE_TEXT'] = '캐빈하우스'
    DATASET['faciltyNo'] = '1200'
    DATASET['resveNoCode'] = 'CH'
elif DATASET['SITE'] == '10':
    # 든, 난, 허 순
    DATASET['SITE_TEXT'] = '바다'
    DATASET['faciltyNoList'] = ['1300', '1400', '1500']
    DATASET['resveNoCodeList'] = ['MA', 'MB', 'MB']
else:
    print('사이트 선택 오류! 시스템 종료')
    exit()


class Worker(threading.Thread):
    def __init__(self, DATASET):
        super().__init__()
        self.name = DATASET['name']  # thread 이름 지정

    def run(self):
        threading.Thread(target=main(DATASET))


def main(DATASET):
    DATASET['START_TIME'] = time.time()
    DATASET['FINAL_ROOM_NAME'] = DATASET['SITE_TEXT']
    DATASET['FINAL_TYPE_NAME'] = DATASET['SITE_TEXT']
    DATASET['AVAILABLE_TEXT_MSG'] = ''

    if len(room_want) == 0:
        DATASET['ROOM_WANT'] = ['ALL']
    else:
        DATASET['ROOM_WANT'] = room_want

    DATASET = message(DATASET, '감시 모드 시작')
    DATASET = message(DATASET, '입력정보 ' + str(DATASET['SITE_TEXT']) + ' / ' + str(DATASET['ROOM_WANT']))

    # 변수

    windows = Desktop(backend="uia").windows(title_re="data;,")
    for w in windows:
        try:
            print(f"닫는 중: {w.window_text()}")
            w.close()  # 윈도우 닫기 시도
        except Exception as e:
            print(f"닫기 실패: {w.window_text()} - {e}")

    DATASET['LOGIN_BROWSER'] = webdriver.Chrome(options=options)
    all_windows = Desktop(backend="uia").windows(title_re="data:,")
    DATASET['MY_WINDOW'] = all_windows[len(all_windows) - 1].handle  # 첫 번째 창 핸들
    DATASET = login(DATASET)


    #DATASET['ERROR_CODE'] = 'delete_reserve'
    #CLEAR = False
    #while not CLEAR:
    #    response = delete_reserve(DATASET)
    #    if response['status_code'] == 200:
    #        DATASET = message(DATASET, '임시 점유 정보 CLEAR')
    #        CLEAR = True
    #    else:
    #        error(DATASET)

    while True:

        #ELAPSED_TIME = time.time() - DATASET['LOGIN_TIME']  # 로그인 후 경과 시간 계산
        #if ELAPSED_TIME >= 1800 and not DATASET['TEMPORARY_HOLD']:
        #    DATASET = relogin(DATASET)

        try:

            time.sleep(DATASET['TIME_DELAY'])
            # 실시간 감시 모드
            if DATASET['MODE_LIVE']:
                for year in sel_year_list:
                    for month in sel_month_list:
                        for date in sel_date_list:
                            DATASET['year'] = str(year)
                            DATASET['month'] = str(month)
                            DATASET['date'] = str(date)

                            # 임시 점유시 처리
                            if DATASET['TEMPORARY_HOLD']:

                                #사실 상 종료 TEST 기간.
                                DATASET = direct_link(DATASET)

                                elapsed_time = time.time() - DATASET['START_TIME']
                                if elapsed_time >= 550:
                                    # 기 임시 점유건 전부 제거
                                    #DATASET['ERROR_CODE'] = 'delete_reserve'
                                    #response = delete_reserve(DATASET)
                                    #if response['status_code'] == 200:
                                        #DATASET = message(DATASET, '임시 점유 정보 CLEAR 및 재 점유')
                                    
                                    #제 예약 시 취소를 하지 않고 계속 조지기
                                    DATASET['RE_TRIED'] = False
                                    while not DATASET['RE_TRIED']:
                                        DATASET['ERROR_CODE'] = 'get_facility'
                                        response = get_facility(DATASET)
                                        if response['status_code'] == 200:
                                            if elapsed_time >= 630:
                                                DATASET['RE_TRIED'] = True
                                                DATASET['TEMPORARY_HOLD'] = True
                                                DATASET['START_TIME'] = time.time()
                                        else:
                                            error(DATASET)
                                    #else:
                                    #    error(DATASET)
                                else:
                                    message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
                                        DATASET['FINAL_ROOM_NAME']) + ' ' + str(DATASET['FROM_DATE']) + ' ' + str(
                                        DATASET['PERIOD']) + '박 임시점유 대기 중 (' + str(int(elapsed_time / 60)) + ')분 지났습니다.')

                            # 임시 점유가 없으면 처리
                            elif not DATASET['TEMPORARY_HOLD']:
                                DATASET['FROM_DATE'] = (
                                    datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'],
                                                      '%Y%m%d')).strftime('%Y-%m-%d')
                                DATASET['TO_DATE'] = (
                                            datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'],
                                                              '%Y%m%d') + timedelta(days=int(period))).strftime(
                                    '%Y-%m-%d')

                                if DATASET['SITE'] == '10':
                                    for index in range(len(DATASET['faciltyNoList'])):
                                        DATASET['faciltyNo'] = DATASET['faciltyNoList'][index]
                                        DATASET['resveNoCode'] = DATASET['resveNoCodeList'][index]
                                        DATASET['ERROR_CODE'] = 'reservation_list'
                                        DATASET['RESULT'] = reservation_list(DATASET)

                                        if not 'login' in str(DATASET['RESULT']):
                                            if DATASET['RESULT']['status_code'] == 200 and DATASET['RESULT']['value'] is not None:
                                                DATASET = reservationList_filter(DATASET)
                                            elif DATASET['RESULT']['status_code'] != 200:
                                                error(DATASET)
                                            elif DATASET['RESULT']['status_code'] == 200:
                                                DATASET['AVAILABLE_TEXT_MSG'] = ''
                                        else:
                                            DATASET = relogin(DATASET)
                                            DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'

                                    if len(DATASET['AVAILABLE_ROOMS']) == 0:
                                        DATASET = remove_temp(DATASET)
                                        message(DATASET, DATASET['FINAL_TYPE_NAME'] + ' ' + str(
                                                DATASET['CANCELING_ROOMS']) + ' 취소 대기 중... / 시스템 메시지 : ' + str(DATASET['RESULT']['message']))

                                    if DATASET['SITE'] == '10':
                                        if len(DATASET['AVAILABLE_ROOMS']) > 0:
                                            message(DATASET,
                                                    DATASET['SITE_TEXT'] + ' 예약가능 : ' + str(DATASET['ROOM_NAMES']))
                                            DATASET = find_want_rooms(DATASET)

                                else:
                                    DATASET['ERROR_CODE'] = 'reservation_list'
                                    DATASET['RESULT'] = reservation_list(DATASET)
                                    if not 'login' in str(DATASET['RESULT']):
                                        if DATASET['RESULT']['status_code'] == 200 and DATASET['RESULT']['value'] is not None:
                                            DATASET = reservationList_filter(DATASET)
                                        elif DATASET['RESULT']['status_code'] != 200:
                                            error(DATASET)
                                        else:
                                            DATASET = remove_temp(DATASET)
                                            message(DATASET,str('점유 불가 ' + DATASET['RESULT']['message']) + ' 예약 가능대상 확인 중...')
                                    else:
                                        DATASET = relogin(DATASET)
                                        DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'

            # TIMING 예약
            elif not DATASET['MODE_LIVE']:

                START_TIME = datetime.now().strftime("%Y-%m-%d") + ' 10:55:30'
                END_TIME = datetime.now().strftime("%Y-%m-%d") + ' 11:30:00'
                RESERVATION_TIME = datetime.now().strftime("%Y-%m-%d") + ' 11:00:05'

                START_TIMER = datetime.strptime(START_TIME, '%Y-%m-%d %H:%M:%S')
                END_TIME = datetime.strptime(START_TIME, '%Y-%m-%d %H:%M:%S')
                CURRENT_TIMER = datetime.now()

                if START_TIMER < CURRENT_TIMER < END_TIME:
                    for year in sel_year_list:
                        for month in sel_month_list:
                            for date in sel_date_list:
                                DATASET['year'] = str(year)
                                DATASET['month'] = str(month)
                                DATASET['date'] = str(date)

                                # 임시 점유시 처리
                                if DATASET['TEMPORARY_HOLD']:

                                    if RESERVATION_TIME > CURRENT_TIMER:
                                        DATASET = direct_link(DATASET)

                                    elapsed_time = time.time() - DATASET['START_TIME']
                                    if elapsed_time >= 550:
                                        # 기 임시 점유건 전부 제거
                                        #DATASET['ERROR_CODE'] = 'delete_reserve'
                                        #response = delete_reserve(DATASET)
                                        if response['status_code'] == 200:
                                            DATASET = message(DATASET, '임시 점유 정보 CLEAR 및 재 점유')
                                            DATASET['RE_TRIED'] = False
                                            while not DATASET['RE_TRIED']:
                                                DATASET['ERROR_CODE'] = 'get_facility'
                                                response = get_facility(DATASET)
                                                if response['status_code'] == 200:
                                                    if elapsed_time >= 630:
                                                        DATASET['RE_TRIED'] = True
                                                        DATASET['TEMPORARY_HOLD'] = True
                                                        DATASET['START_TIME'] = time.time()
                                            else:
                                                error(DATASET)
                                        else:
                                            error(DATASET)
                                    else:
                                        message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
                                            DATASET['FINAL_ROOM_NAME']) + ' ' + str(DATASET['FROM_DATE']) + ' ' + str(
                                            DATASET['PERIOD']) + '박 임시점유 대기 중 (' + str(
                                            int(elapsed_time / 60)) + ')분 지났습니다.')

                                # 임시 점유가 없으면 처리
                                elif not DATASET['TEMPORARY_HOLD']:
                                    DATASET['FROM_DATE'] = (datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'],'%Y%m%d')).strftime('%Y-%m-%d')
                                    DATASET['TO_DATE'] = (datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'],'%Y%m%d') + timedelta(days=int(period))).strftime('%Y-%m-%d')

                                    if DATASET['SITE'] == '10':
                                        for index in range(len(DATASET['faciltyNoList'])):
                                            DATASET['faciltyNo'] = DATASET['faciltyNoList'][index]
                                            DATASET['resveNoCode'] = DATASET['resveNoCodeList'][index]
                                            DATASET['ERROR_CODE'] = 'reservation_list'
                                            DATASET['RESULT'] = reservation_list(DATASET)
                                            if not 'login' in str(DATASET['RESULT']):
                                                if DATASET['RESULT']['status_code'] == 200 and DATASET['RESULT']['value'] is not None:
                                                    DATASET = reservationList_filter(DATASET)
                                                elif DATASET['RESULT']['status_code'] != 200:
                                                    error(DATASET)
                                                elif DATASET['RESULT']['status_code'] == 200:
                                                    DATASET['AVAILABLE_TEXT_MSG'] = ''
                                            else:
                                                DATASET = relogin(DATASET)
                                                DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'


                                        if len(DATASET['AVAILABLE_ROOMS']) == 0:
                                            DATASET = remove_temp(DATASET)
                                            message(DATASET, DATASET['FINAL_TYPE_NAME'] + ' ' + str(
                                                DATASET['CANCELING_ROOMS']) + ' 취소 대기 중... / 시스템 메시지 : ' + str(
                                                DATASET['RESULT']['message']))

                                        if DATASET['SITE'] == '10':
                                            if len(DATASET['AVAILABLE_ROOMS']) > 0:
                                                message(DATASET,
                                                        DATASET['SITE_TEXT'] + ' 예약가능 : ' + str(DATASET['ROOM_NAMES']))
                                                DATASET = find_want_rooms(DATASET)

                                    else:
                                        DATASET['ERROR_CODE'] = 'reservation_list'
                                        DATASET['RESULT'] = reservation_list(DATASET)
                                        if not 'login' in str(DATASET['RESULT']):
                                            if DATASET['RESULT']['status_code'] == 200 and DATASET['RESULT']['value'] is not None:
                                                DATASET = reservationList_filter(DATASET)
                                            elif DATASET['RESULT']['status_code'] != 200:
                                                error(DATASET)
                                            else:
                                                DATASET = remove_temp(DATASET)
                                                message(DATASET, str('점유 불가 ' + DATASET['RESULT']['message']) + ' 예약 가능대상 확인 중...')
                                        else:
                                            DATASET = relogin(DATASET)
                                            DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'
                
                else:
                    DATASET = message(DATASET, '예약 시간이 되지 않아 대기 중 입니다.')


        except Exception as ex:
            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' EXCEPTION!!' + str(ex))
            error(DATASET)
            DATASET = relogin(DATASET)
            continue


def check_available(data):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectFcltyCalendarDetail.do"
    dict_data = {
        'trrsrtCode': str(data['trrsrtCode']),
        'q_year': str(data['year']),
        'q_month': str(data['month']),
        'qDay': str(data['date'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, verify=False)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def reservation_list(data):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectChildFcltyList.do"
    dict_data = {
        'trrsrtCode': str(data['trrsrtCode']),
        'fcltyCode': str(data['faciltyNo']),
        'resveNoCode': str(data['resveNoCode']),
        'resveBeginDe': str(data['FROM_DATE']),
        'resveEndDe': str(data['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=data['COOKIE'], verify=False)
            dict_meta = {}
            if not 'login' in response.text:
                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    return {**dict_meta, **response.json()}
                else:  # 문자열 형태인 경우
                    return {**dict_meta, **{'text': response.text}}
            else:  # 문자열 형태인 경우
                message(data, '로그인 TIMEOUT 발생, 재로그인 시도')
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


# 자리선점
def get_facility(data):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(data['trrsrtCode']),
        'fcltyCode': str(data['fcltyCode']),
        'resveNoCode': str(data['resveNoCode']),
        'resveBeginDe': str(data['FROM_DATE']),
        'resveEndDe': str(data['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=data['COOKIE'], verify=False)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


# 자리선점
def delete_reserve(data):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_deletePreOcpcInfo.do"

    response = ''
    while response == '':
        try:
            response = requests.post(url=url, cookies=data['COOKIE'], verify=False)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue

    #다이렉트 접근 TRACKING 정보 입력
def insertTracking(data):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/component/anallyze/ND_insertTracking.do"
    dict_data = {
        'userId': '58.87.60.213|' + str(int(round(float(time.time()), 3) * 1000)),
        'domnNm': 'www.campingkorea.or.kr',
        'userMenuCode': 'resveReqst01',
        'url': 'https://www.campingkorea.or.kr/user/reservation/BD_reservationReq.do',
        'transrCours': 'https://www.campingkorea.or.kr/user/reservation/BD_reservation.do',
        'userAgent': str(generate_user_agent(os='win', device_type='desktop')),
        'rsoltnAr': '2560',
        'rsoltnHg': '1440',
        'scrinColorCo': '24',
        'pgeSj': '온라인 예약하기 : HOME > 온라인예약 > 온라인 예약하기',
        'frstConectrAt': 'N',
        'searchEngineInflowAt': 'N',
        'pgeViewCo': '13',
        'frstConectHourAt': 'N',
        'frstConectDeAt': 'N',
        'frstConectWeekAt': 'N',
        'frstConectMtAt': 'N',
        'againVisitPd': '0'
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=data['COOKIE'], verify=False)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def login(data):
    driver = data['LOGIN_BROWSER']
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

    return data


def relogin(data):
    driver = data['LOGIN_BROWSER']
    url = "https://www.campingkorea.or.kr/index.do"
    driver.get(url)

    wait = WebDriverWait(driver, 1000)
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

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "util")))
    time.sleep(0.5)
    exit_tag = driver.find_elements(By.CLASS_NAME, "util")
    exit_tag[0].find_elements(By.CSS_SELECTOR, "a")[0].click()
    data['MESSAGE'] = ''
    data = login(data)
    return data


def reservationList_filter(data):
    room_list = data['RESULT']['value']['childFcltyList']

    if data['SITE'] != '10':
        data['AVAILABLE_ROOMS'] = []
        data['ROOM_NAMES'] = []

    data['CANCELING_ROOMS'] = []
    data['CANCEL_ROOMS'] = []
    data['AVAILABLE_TEXT_MSG'] = ''
    for data['ROOM'] in room_list:
        data['AVAILABLE_YN'] = str(data['ROOM']['resveAt'])
        data['CANCEL_YN'] = str(data['ROOM']['canclYn'])

        #AVAILABLE Y 예약가능 N 불가능 // CANCEL Y 취소완료 여부 Y 취소완료 여부 N
        if data['AVAILABLE_YN'] == 'Y':
            if data['CANCEL_YN'] == 'Y':
                data['ROOM_NAME'] = str(data['ROOM']['fcltyNm']).replace('호', '').replace('번', '')  # naming으로 처리하여 식별하기
                if str(data['ROOM_NAME']) in data['ROOM_WANT'] or (
                        len(data['ROOM_WANT']) == 1 and data['ROOM_WANT'][0] == 'ALL'):
                    data['AVAILABLE_ROOMS'].append(data['ROOM'])
                    data['ROOM_NAMES'].append(str(data['ROOM']['fcltyNm']))
            elif data['CANCEL_YN'] == 'N':
                data['ROOM_NAME'] = str(data['ROOM']['fcltyNm']).replace('호', '').replace('번', '')  # naming으로 처리하여 식별하기
                if str(data['ROOM_NAME']) in data['ROOM_WANT'] or (len(data['ROOM_WANT']) == 1 and data['ROOM_WANT'][0] == 'ALL'):
                    data['AVAILABLE_TEXT_MSG'] = '예약 가능상태 이나 취소중인 건 입니다. 최초 체크 시간: ' + str(datetime.now().strftime('%Y-%m-%d %H:%M'))
                    data['CANCEL_ROOMS'].append(data['ROOM'])
                    data['CANCELING_ROOMS'].append(str(data['ROOM']['fcltyNm']))
                    data = remove_temp(data)
        
        #SPOT 모드
        if MODE_SPOT and (len(data['AVAILABLE_ROOMS']) > 0 or len(data['CANCEL_ROOMS']) > 0):
            NO_AVAILABLE = True
            while NO_AVAILABLE:
                for room in data['AVAILABLE_ROOMS']:
                    message(data, '취소 대상 대기 중.. ' + str(room['fcltyNm']))
                    data['FINAL_ROOM_NAME'] = str(room['fcltyNm'])
                    data['fcltyCode'] = str(room['fcltyCode'])
                    data['resveNoCode'] = str(room['resveNoCode'])
                    data['ERROR_CODE'] = 'spot get_facility'
                    response = get_facility(data)
                    if response['status_code'] == 200:
                        data['TEMPORARY_HOLD'] = True
                        data = direct_link(data)
                        DATASET['START_TIME'] = time.time()
                    else:
                        if NO_AVAILABLE:
                            NO_AVAILABLE = False
                        error(data)
                if data['TEMPORARY_HOLD']:
                    break
                for room in data['CANCEL_ROOMS']:
                    message(data, '취소 대상 대기 중.. ' + str(room['fcltyNm']))
                    data['FINAL_ROOM_NAME'] = str(room['fcltyNm'])
                    data['fcltyCode'] = str(room['fcltyCode'])
                    data['resveNoCode'] = str(room['resveNoCode'])
                    data['ERROR_CODE'] = 'spot get_facility'
                    response = get_facility(data)
                    if response['status_code'] == 200:
                        data['TEMPORARY_HOLD'] = True
                        data = direct_link(data)
                        DATASET['START_TIME'] = time.time()
                        message(data, '임시 점유 완료 ' + str(room['fcltyNm']))
                    else:
                        if NO_AVAILABLE:
                            NO_AVAILABLE = False
                        error(data)
                if data['TEMPORARY_HOLD']:
                    break


        if data['AVAILABLE_TEXT_MSG'] == '':
            data = remove_temp(data)
            data['AVAILABLE_TEXT_MSG'] = '예약 가능한 대상이 없습니다. 최초 체크 시간: ' + str(datetime.now().strftime('%Y-%m-%d %H:%M'))
    if data['SITE'] != '10':
        if len(data['AVAILABLE_ROOMS']) == 0:
            message(DATASET, str(data['CANCELING_ROOMS']) + ' ' + str(data['FINAL_ROOM_NAME']) + ' ' + data['AVAILABLE_TEXT_MSG'])
        else:
            message(DATASET, data['SITE_TEXT'] + ' 예약가능 : ' + str(data['ROOM_NAMES']))
            data = find_want_rooms(data)
    return data


def find_want_rooms(data):
    if len(data['ROOM_SELT']) == 0:
        data['FINAL_ROOM_NAME'] = str(data['AVAILABLE_ROOMS'][0]['fcltyNm'])
        data['fcltyCode'] = str(data['AVAILABLE_ROOMS'][0]['fcltyCode'])
        data['resveNoCode'] = str(data['AVAILABLE_ROOMS'][0]['resveNoCode'])

        if data['fcltyCode'][0:2] == 'DD':
            data['FINAL_TYPE_NAME'] = '든바다'
        elif data['fcltyCode'][0:2] == 'NG':
            data['FINAL_TYPE_NAME'] = '난바다'
        elif data['fcltyCode'][0:2] == 'HB':
            data['FINAL_TYPE_NAME'] = '허허바다'
        else:
            data['FINAL_TYPE_NAME'] = data['SITE_TEXT']

    else:
        for room in data['AVAILABLE_ROOMS']:
            name = str(room['fcltyNm']).replace('호', '').replace('번', '')
            if str(name) in data['ROOM_SELT']:
                data['FINAL_ROOM_NAME'] = str(room['fcltyNm'])
                data['fcltyCode'] = str(room['fcltyCode'])
                data['resveNoCode'] = str(room['resveNoCode'])

    DATASET['ERROR_CODE'] = 'find_want_rooms -> get_facility'
    response = get_facility(data)
    if response['status_code'] == 200:
        DATASET['TEMPORARY_HOLD'] = True
        DATASET['START_TIME'] = time.time()
    else:
        DATASET['TEMPORARY_HOLD'] = False
        error(DATASET)
    return data


def direct_link(data):
    # DIRECT 화면이동
    data['RESULT'] = insertTracking(data)
    html = '''
                                    <form id="postForm" method="POST" action="https://www.campingkorea.or.kr/user/reservation/BD_reservationReq.do">
                                      <input type="hidden" name="trrsrtCode" value="1000">
                                      <input type="hidden" name="q_trrsrtCd" value="">
                                      <input type="hidden" name="q_year" value=''' + '"' + data['year'] + '"' + '''>
                                      <input type="hidden" name="q_month" value=''' + '"' + data['month'] + '"' + '''>
                                      <input type="hidden" name="flag" value="Y">
                                      <input type="hidden" name="resveBeginDe" value=''' + '"' + data['FROM_DATE'] + '"' + '''>
                                      <input type="hidden" name="stayngPd" value="">
                                      <input type="hidden" name="resveEndDe" value=''' + '"' + data['TO_DATE'] + '"' + '''>
                                      <input type="hidden" name="answer" value="">
                                    </form>
                                    <script>
                                      document.getElementById('postForm').submit();
                                    </script>
                                    '''
    data['LOGIN_BROWSER'].get("data:text/html;charset=utf-8," + html)
    time.sleep(3)
    # VK_RETURN은 Enter 키
    win32gui.PostMessage(data['MY_WINDOW'], win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.05)
    win32gui.PostMessage(data['MY_WINDOW'], win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    # 사실 상 매크로 종료.
    time.sleep(300)
    return data


def remove_temp(data):
    # 해제할 때만 사용
    if data['TEMPORARY_HOLD']:
        data['TEMPORARY_HOLD'] = False
    return data


def create_new_browser(driver):
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)
    driver.maximize_window()
    return driver


def message(data, text):
    if data['MESSAGE'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        data['MESSAGE'] = text
    return data


def error(data):
    if data['ERROR_MESSAGE'] != data['ERROR_CODE']:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ######################  ERROR! ' + str(
            data['ERROR_CODE']) + '  ######################')
        print(str(data))
        data['ERROR_MESSAGE'] = data['ERROR_CODE']
        data['CYCLE_ERR_CNT'] = 0
    else:
        data['CYCLE_ERR_CNT'] = int(data['CYCLE_ERR_CNT']) + 1
    return data


for i in range(machine):
    nametag = i + 1
    name = "MACHINE{}".format(nametag)
    DATASET['name'] = name
    DATASET['nametag'] = nametag
    t = Worker(DATASET)  # sub thread 생성
    t.start()
    time.sleep(time_cut)
