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
options.add_argument("headless") # 크롬창 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
global try_cnt

machine = 1  # 예약 머신 숫자 높을 수록 압도적이지만, 서버 박살낼 수가 있음.. 조심
time_cut = 5  # 머신 시작 간격
period = 2  # 연박 수
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
room_want = []
room_selt = []
# room_want = ['115']
# room_want = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
#room_want = ['101', '110', '106', '109', '113', '115']
room_selt = []

sel_year_list = ['2025']
sel_month_list = ['08']
sel_date_list = ['13']
site = '2'

current_room = '0'
user_type = 0           # 사용자 정보 세팅
MODE_LIVE = True        # 실시간 감시 여부 (취소표 잡을 때 사용)
FINAL_RESERVE = True    # 최종 예약까지 진행 이렇게 하면 잘못예약되 취소할 경우 패널티2시간이 생긴다
MODE_SPOT = False       # 지정 사이트만 강제 집중적으로 반복
ONLY_CHECK = False      # 예약 가능 대상만 체크
MODE_ALWS = True        # 항상 최종예약 오픈, 시간에 관계없이 최종예약을 한다. (주의 미리 선점하려는 사이트는 최종예약이 안됨으로 필히 OFF할것)
DELAY = 2               # 임시점유 상태의 갱신 주기 속도 새벽엔 느리게 권장

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
    rphone = '01024863033'
elif user_type == 1:
    user_name = '권혁인'
    rpwd = 'khi831883!'
    rid = 'sochi007'
    rphone = '01020569536'
elif user_type == 2:
    user_name = '김계자'
    rpwd = 'cjswosla86'
    rid = 'psm07051'
    rphone = '01056947788'
elif user_type == 3:
    user_name = '박응순'
    rpwd = 'cjswosla86'
    rid = 'parksi'
    rphone = '01021635418'
elif user_type == 4:
    user_name = '박현정'
    rpwd = 'khi831883!'
    rid = 'fpahs414'
    rphone = '01020569536'
elif user_type == 5:
    user_name = '박상민'
    rpwd = 'CJSWOsla86!@'
    rid = 'psm0705'
    rphone = '01024863038'
elif user_type == 6:
    user_name = '윤민주'
    rpwd = 'cca1174848'
    rid = 'jsy3038'
    rphone = '01048983777'
elif user_type == 7:
    user_name = '김형민'
    rpwd = 'zhffktk2ek!'
    rid = 'ttasik99'
    rphone = '01091251464'
elif user_type == 8:
    user_name = '박보림'
    rpwd = 'qhfla88067488!'
    rid = 'iborim'
    rphone = '01094138806'
elif user_type == 9:
    user_name = '김세익'
    rpwd = 'cjswosla88!@'
    rid = 'iseick'
    rphone = '01041798796'
elif user_type == 10:
    user_name = '강동우'   #든바다 104, 107, 114, 118
    rpwd = 'kdwpa8307!'
    rid = 'kdwpa8307'
    rphone = '01091179661'
else:
    print('User type이 없습니다. 종료합니다')
    exit()

DATASET = {
    'MODE_LIVE': MODE_LIVE,
    'MODE_ALWS': MODE_ALWS,
    'MODE_SPOT': MODE_SPOT,
    'TEMPORARY_HOLD': False,
    'FINAL_RESERVE': FINAL_RESERVE,
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
    'TIME_DELAY': DELAY,
    'MULTI_HOUR': 0,
    'CYCLE_ERR_CNT': 0,
    'CURRENT_PROCESS': 'BEGIN',
    'HOLDING_TIME': 0,
    'registerId': rid,
    'rsvctmNm': user_name,
    'rsvctmEncptMbtlnum': rphone,
    'encptEmgncCttpc': rphone,
    'ONLY_CHECK': ONLY_CHECK
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
    DATASET['resveNoCodeList'] = ['MA', 'MI', 'MB']
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
    DATASET['CURRENT_PROCESS'] = 'main'
    DATASET['START_TIME'] = time.time()
    DATASET['FINAL_ROOM_NAME'] = DATASET['SITE_TEXT']
    DATASET['FINAL_TYPE_NAME'] = DATASET['SITE_TEXT']
    DATASET['AVAILABLE_TEXT_MSG'] = ''

    if len(room_want) == 0:
        DATASET['ROOM_WANT'] = ['ALL']
    else:
        DATASET['ROOM_WANT'] = room_want

    DATASET = message(DATASET, '감시 모드 시작')
    DATASET = message(DATASET, '입력정보 ' + str(DATASET['SITE_TEXT']) + ' / 범위 : ' + str(DATASET['ROOM_WANT']) + ' 지정 대상 ' + str(DATASET['ROOM_SELT']))

    # 변수

    #windows = Desktop(backend="uia").windows(title_re="data;,")
    #for w in windows:
    #    try:
    #        print(f"닫는 중: {w.window_text()}")
    #        w.close()  # 윈도우 닫기 시도
    #    except Exception as e:
    #        print(f"닫기 실패: {w.window_text()} - {e}")

    DATASET['LOGIN_BROWSER'] = webdriver.Chrome(options=options)
    #all_windows = Desktop(backend="uia").windows(title_re="data:,")
    #DATASET['MY_WINDOW'] = all_windows[len(all_windows) - 1].handle  # 첫 번째 창 핸들
    DATASET = login(DATASET)

    # DATASET['ERROR_CODE'] = 'delete_reserve'
    # CLEAR = False
    # while not CLEAR:
    #    response = delete_reserve(DATASET)
    #    if response['status_code'] == 200:
    #        DATASET = message(DATASET, '임시 점유 정보 CLEAR')
    #        CLEAR = True
    #    else:
    #        error(DATASET)

    while True:
        try:
            time.sleep(DATASET['TIME_DELAY'])
            # 실시간 감시 모드
            if DATASET['MODE_LIVE']:
                DATASET['CURRENT_PROCESS'] = 'MODE_LIVE TRUE'
                for year in sel_year_list:
                    for month in sel_month_list:
                        for date in sel_date_list:
                            DATASET['year'] = str(year)
                            DATASET['month'] = str(month)
                            DATASET['date'] = str(date)

                            # 임시 점유시 처리
                            if DATASET['TEMPORARY_HOLD']:
                                DATASET['CURRENT_PROCESS'] = 'TEMPORARY_HOLD TRUE'
                                DATASET = temporary_hold(DATASET)

                            # 임시 점유가 없으면 처리
                            elif not DATASET['TEMPORARY_HOLD']:
                                DATASET['CURRENT_PROCESS'] = 'TEMPORARY_HOLD FALSE'
                                DATASET['FROM_DATE'] = (
                                    datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'],
                                                      '%Y%m%d')).strftime('%Y-%m-%d')
                                DATASET['TO_DATE'] = (
                                        datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'],
                                                          '%Y%m%d') + timedelta(days=int(period))).strftime(
                                    '%Y-%m-%d')

                                if DATASET['SITE'] == '10':
                                    for index in range(len(DATASET['faciltyNoList'])):
                                        if DATASET['TEMPORARY_HOLD']:
                                            break
                                        DATASET['faciltyNo'] = DATASET['faciltyNoList'][index]
                                        DATASET['resveNoCode'] = DATASET['resveNoCodeList'][index]
                                        DATASET['ERROR_CODE'] = 'reservation_list'
                                        DATASET['RESULT'] = reservation_list(DATASET)

                                        if not 'login' in str(DATASET['RESULT']):
                                            if DATASET['RESULT']['status_code'] == 200:
                                                DATASET['AVAILABLE_TEXT_MSG'] = ''
                                                if DATASET['RESULT']['value'] is not None:
                                                    DATASET = reservationList_filter(DATASET)
                                            elif DATASET['RESULT']['status_code'] != 200:
                                                message(DATASET, '통신 실패 STATUS CODE = ' + str(DATASET['RESULT']['status_code']))
                                                #error(DATASET)
                                        else:
                                            DATASET = relogin(DATASET)
                                            DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'

                                    if len(DATASET['AVAILABLE_ROOMS']) == 0 and not DATASET['TEMPORARY_HOLD']:
                                        message(DATASET, DATASET['FINAL_TYPE_NAME'] + ' ' + str(
                                            DATASET['CANCELING_ROOMS']) + ' 취소 대기 중... / 시스템 메시지 : ' + str(
                                            DATASET['RESULT']['message']))

                                    if DATASET['SITE'] == '10':
                                        if len(DATASET['AVAILABLE_ROOMS']) > 0:
                                            message(DATASET,
                                                    DATASET['SITE_TEXT'] + ' 예약가능 : ' + str(DATASET['ROOM_NAMES']))
                                            #DATASET = find_want_rooms(DATASET)

                                else:
                                    DATASET['ERROR_CODE'] = 'reservation_list'
                                    DATASET['RESULT'] = reservation_list(DATASET)
                                    if not 'login' in str(DATASET['RESULT']):
                                        if DATASET['RESULT']['status_code'] == 200:
                                            if DATASET['RESULT']['value'] is not None:
                                                DATASET = reservationList_filter(DATASET)
                                            else:
                                                message(DATASET, DATASET['RESULT']['message'])
                                        elif DATASET['RESULT']['status_code'] != 200:
                                            message(DATASET,
                                                    '통신 실패 STATUS CODE = ' + str(DATASET['RESULT']['status_code']))
                                            #error(DATASET)
                                        else:
                                            DATASET = remove_temp(DATASET)
                                            message(DATASET,
                                                    str('점유 불가 ' + DATASET['RESULT']['message']) + ' 예약 가능대상 확인 중...')
                                    else:
                                        DATASET = relogin(DATASET)
                                        DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'

            # TIMING 예약
            elif not DATASET['MODE_LIVE']:
                DATASET['CURRENT_PROCESS'] = 'MODE_LIVE FALSE'
                START_TIMER = datetime.strptime(datetime.now().strftime("%Y-%m-%d") + ' 00:36:10', '%Y-%m-%d %H:%M:%S')
                END_TIME = datetime.strptime(datetime.now().strftime("%Y-%m-%d") + ' 12:30:00', '%Y-%m-%d %H:%M:%S')
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
                                    DATASET = temporary_hold(DATASET)

                                # 임시 점유가 없으면 처리
                                elif not DATASET['TEMPORARY_HOLD']:
                                    DATASET['CURRENT_PROCESS'] = 'TEMPORARY_HOLD FALSE'
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
                                                if DATASET['RESULT']['status_code'] == 200:
                                                    DATASET['AVAILABLE_TEXT_MSG'] = ''
                                                    if DATASET['RESULT']['value'] is not None:
                                                        DATASET = reservationList_filter(DATASET)
                                                elif DATASET['RESULT']['status_code'] != 200:
                                                    message(DATASET, '통신 실패 STATUS CODE = ' + str(
                                                        DATASET['RESULT']['status_code']))
                                            else:
                                                DATASET = relogin(DATASET)
                                                DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'

                                        if len(DATASET['AVAILABLE_ROOMS']) == 0 and not DATASET['TEMPORARY_HOLD']:
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
                                            if DATASET['RESULT']['status_code'] == 200:
                                                if DATASET['RESULT']['value'] is not None:
                                                    DATASET = reservationList_filter(DATASET)
                                                else:
                                                    message(DATASET, DATASET['RESULT']['message'])
                                            elif DATASET['RESULT']['status_code'] != 200:
                                                message(DATASET, '통신 실패 STATUS CODE = ' + str(
                                                    DATASET['RESULT']['status_code']))
                                                #error(DATASET)
                                            else:
                                                DATASET = remove_temp(DATASET)
                                                message(DATASET, str('점유 불가 ' + DATASET['RESULT'][
                                                    'message']) + ' 예약 가능대상 확인 중...')
                                        else:
                                            DATASET = relogin(DATASET)
                                            DATASET['RESULT']['message'] = '다시 로그인을 하여 재 시작합니다.'

                else:
                    DATASET = message(DATASET, '예약 시간이 되지 않아 대기 중 입니다.')


        except Exception as ex:
            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' EXCEPTION!!' + str(ex))
            print('ERROR PROCESS = ' + str(DATASET['CURRENT_PROCESS']))
            error(DATASET)
            #DATASET = relogin(DATASET)
            continue


def check_available(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectFcltyCalendarDetail.do"
    dict_data = {
        'trrsrtCode': str(DATASET['trrsrtCode']),
        'q_year': str(DATASET['year']),
        'q_month': str(DATASET['month']),
        'qDay': str(DATASET['date'])
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


def reservation_list(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectChildFcltyList.do"
    dict_data = {
        'trrsrtCode': str(DATASET['trrsrtCode']),
        'fcltyCode': str(DATASET['faciltyNo']),
        'resveNoCode': str(DATASET['resveNoCode']),
        'resveBeginDe': str(DATASET['FROM_DATE']),
        'resveEndDe': str(DATASET['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False)
            dict_meta = {}
            if not 'login' in response.text:
                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    return {**dict_meta, **response.json()}
                else:  # 문자열 형태인 경우
                    return {**dict_meta, **{'text': response.text}}
            else:  # 문자열 형태인 경우
                message(DATASET, '로그인 TIMEOUT 발생, 재로그인 시도')
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


# 자리선점
def get_facility(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(DATASET['trrsrtCode']),
        'fcltyCode': str(DATASET['fcltyCode']),
        'resveNoCode': str(DATASET['resveNoCode']),
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
                return DATASET
            else:  # 문자열 형태인 경우
                DATASET['RESULT'] = {**dict_meta, **{'text': response.text}}
                return DATASET
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def reservation_page_check(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/BD_reservationInfo.do"
    dict_data = {
        'trrsrtCode': str(DATASET['FINAL_TRRSRTCODE']),
        'resveBeginDe': str(DATASET['FINAL_RESVEBEGINDE']),
        'resveEndDe': str(DATASET['FINAL_RESVEENDDE']),
        'stayngPd': '',
        'parentFcltyCode': str(DATASET['faciltyNo']),
        'fcltyCode': str(DATASET['FINAL_FCLTYCODE']),
        'fcltyTyCode': str(DATASET['FINAL_FCLTYTYCODE']),
        'resveNoCode': '',
        'resveNo': str(DATASET['FINAL_RESVENO']),
        'preocpcFcltyCode': str(DATASET['FINAL_PREOCPCFCLTYCODE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False)

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


# 최종예약
def final_reservation(DATASET):
    # 예약 파라미터 세팅
    #insertTracking(DATASET)
    #reservation_page_check(DATASET)
    #insertTracking(DATASET)

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

# 자리선점
def delete_reserve(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_deletePreOcpcInfo.do"

    response = ''
    while response == '':
        try:
            response = requests.post(url=url, cookies=DATASET['COOKIE'], verify=False)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue

    # 다이렉트 접근 TRACKING 정보 입력


def insertTracking(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/component/anallyze/ND_insertTracking.do"
    dict_data = {
        'userId': '121.132.97.61|' + str(int(round(float(time.time()), 3) * 1000)),
        'domnNm': 'www.campingkorea.or.kr',
        'userMenuCode': 'resveReqst01',
        'url': 'https://www.campingkorea.or.kr/user/reservation/BD_reservationReq.do',
        'transrCours': 'https://www.campingkorea.or.kr/user/reservation/BD_reservation.do',
        #'userAgent': str(generate_user_agent(os='win', device_type='desktop')),
        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'rsoltnAr': '2560',
        'rsoltnHg': '1440',
        'scrinColorCo': '24',
        'pgeSj': '온라인 예약하기 : HOME > 온라인예약 > 온라인 예약하기',
        'frstConectrAt': 'N',
        'searchEngineInflowAt': 'N',
        'pgeViewCo': '5',
        'frstConectHourAt': 'N',
        'frstConectDeAt': 'N',
        'frstConectWeekAt': 'N',
        'frstConectMtAt': 'N',
        'againVisitPd': '0'
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def login(DATASET):
    DATASET['CURRENT_PROCESS'] = 'login'
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


def relogin(DATASET):
    DATASET['CURRENT_PROCESS'] = 'relogin'
    driver = DATASET['LOGIN_BROWSER']
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
    DATASET['MESSAGE'] = ''
    DATASET = login(DATASET)
    return DATASET


def reservationList_filter(DATASET):
    DATASET['CURRENT_PROCESS'] = 'reservationList_filter'
    room_list = DATASET['RESULT']['value']['childFcltyList']

    if DATASET['SITE'] != '10':
        DATASET['AVAILABLE_ROOMS'] = []
        DATASET['ROOM_NAMES'] = []

    DATASET['CANCELING_ROOMS'] = []
    DATASET['CANCEL_ROOMS'] = []
    DATASET['AVAILABLE_TEXT_MSG'] = ''
    for DATASET['ROOM'] in room_list:
        DATASET['AVAILABLE_YN'] = str(DATASET['ROOM']['resveAt'])
        DATASET['CANCEL_YN'] = str(DATASET['ROOM']['canclYn'])

        if DATASET['MODE_SPOT']:    #SPOT 모드이면 강제로 선택한 타겟 지정
            DATASET['ROOM_NAME'] = str(DATASET['ROOM']['fcltyNm']).replace('호', '').replace('번', '')  # naming으로 처리하여 식별하기
            if str(DATASET['ROOM_NAME']) in DATASET['ROOM_SELT'] and len(DATASET['ROOM_SELT']) == 1:
                DATASET['AVAILABLE_ROOMS'] = []
                DATASET['ROOM_NAMES'] = []
                DATASET['AVAILABLE_ROOMS'].append(DATASET['ROOM'])
                DATASET['ROOM_NAMES'].append('SPOT MODE ' + str(DATASET['ROOM']['fcltyNm']))
                break

        # AVAILABLE Y 예약가능 N 불가능 // CANCEL Y 취소완료 여부 Y 취소완료 여부 N
        if DATASET['AVAILABLE_YN'] == 'Y':
            if DATASET['CANCEL_YN'] == 'Y':
                DATASET['ROOM_NAME'] = str(DATASET['ROOM']['fcltyNm']).replace('호', '').replace('번', '')  # naming으로 처리하여 식별하기
                if str(DATASET['ROOM_NAME']) in DATASET['ROOM_WANT'] or (len(DATASET['ROOM_WANT']) == 1 and DATASET['ROOM_WANT'][0] == 'ALL'):

                    DATASET['AVAILABLE_ROOMS'].append(DATASET['ROOM'])
                    #INPUT_TEXT = ''
                    #if DATASET['SITE'] == '10':
                    #    if DATASET['ROOM']['fcltyCode'][0:2] == 'DA':
                    #        INPUT_TEXT = '든바다' + str(DATASET['ROOM']['fcltyNm'])
                    #    else:
                    #        INPUT_TEXT = str(DATASET['ROOM']['fcltyNm'])
                    DATASET['ROOM_NAMES'].append(str(DATASET['ROOM']['fcltyNm']))
            elif DATASET['CANCEL_YN'] == 'N':
                DATASET['ROOM_NAME'] = str(DATASET['ROOM']['fcltyNm']).replace('호', '').replace('번', '')  # naming으로 처리하여 식별하기
                if str(DATASET['ROOM_NAME']) in DATASET['ROOM_WANT'] or (
                        len(DATASET['ROOM_WANT']) == 1 and DATASET['ROOM_WANT'][0] == 'ALL'):
                    DATASET['AVAILABLE_TEXT_MSG'] = '예약 가능상태 이나 취소중인 건 입니다. 최초 체크 시간: ' + str(
                        datetime.now().strftime('%Y-%m-%d %H:%M'))
                    DATASET['CANCEL_ROOMS'].append(DATASET['ROOM'])
                    DATASET['CANCELING_ROOMS'].append(str(DATASET['ROOM']['fcltyNm']))
                    DATASET = remove_temp(DATASET)

    if len(DATASET['AVAILABLE_ROOMS']) > 0:
        message(DATASET, '선택 대상 -> ' + str(DATASET['ROOM_SELT']) + ' /// 선점 예약가능 대상 -> ' + str(DATASET['ROOM_NAMES']) + ' 실시간 매칭 대상을 확인 합니다..')
    if len(DATASET['CANCEL_ROOMS']) > 0:
        message(DATASET, '선택 대상 -> ' + str(DATASET['ROOM_SELT']) + ' /// 취소 예약가능 대상 -> ' + str(DATASET['ROOM_NAMES']) + ' 실시간 매칭 대상을 확인 합니다..')
    # SPOT 모드
    if DATASET['ONLY_CHECK']:
        exit('가능 대상 체크, 시스템종료')
    if (len(DATASET['AVAILABLE_ROOMS']) > 0 or len(DATASET['CANCEL_ROOMS']) > 0) and not DATASET['TEMPORARY_HOLD']:
        NO_AVAILABLE = True
        while NO_AVAILABLE:
            RESULT_MSG = '예약을 지정할 수 있는 대상이 없습니다. 가능한 대상이 있다면 선호 대상 정보를 확인하세요.'
            for room in DATASET['AVAILABLE_ROOMS']:
                if DATASET['MODE_SPOT'] and len(DATASET['ROOM_SELT']) == 1:
                    END_SPOT = True
                    while END_SPOT:  # SPOT MODE 지정으로 여기서 종료
                        DATASET['FINAL_ROOM_NAME'] = str(room['fcltyNm'])
                        DATASET['fcltyCode'] = str(room['fcltyCode'])
                        DATASET['resveNoCode'] = str(room['resveNoCode'])
                        DATASET['ERROR_CODE'] = 'spot get_facility'
                        DATASET = get_facility(DATASET)
                        if DATASET['RESULT']['status_code'] == 200 and 'rsltMsg' in DATASET['RESULT']:
                            if DATASET['RESULT']['rsltMsg'] == '선택하신 시설이 선점되었습니다.':
                                message(DATASET, ' SPOT MODE 임시 점유 완료 ' + str(room['fcltyNm']))
                                DATASET['TEMPORARY_HOLD'] = True
                                break
                            elif DATASET['RESULT']['resveNo'] is not None:
                                message(DATASET, str(room['fcltyNm']) + ' SPOT MODE 이미 점유 중 계속 진행합니다. ')
                                DATASET['TEMPORARY_HOLD'] = True
                                break
                            else:
                                message(DATASET, 'SPOT MODE ' + DATASET['RESULT']['rsltMsg'])
                        if DATASET['TEMPORARY_HOLD']:
                            break

                name = str(room['fcltyNm']).replace('호', '').replace('번', '')
                if str(name) in DATASET['ROOM_SELT'] or len(DATASET['ROOM_SELT']) == 0:
                    DATASET['FINAL_ROOM_NAME'] = str(room['fcltyNm'])
                    DATASET['fcltyCode'] = str(room['fcltyCode'])
                    DATASET['resveNoCode'] = str(room['resveNoCode'])
                    DATASET['ERROR_CODE'] = 'spot get_facility'
                    DATASET = get_facility(DATASET)
                    if DATASET['RESULT']['status_code'] == 200 and 'rsltMsg' in DATASET['RESULT']:
                        if DATASET['RESULT']['rsltMsg'] == '선택하신 시설이 선점되었습니다.':
                            message(DATASET, '임시 점유 완료 ' + str(room['fcltyNm']))
                            DATASET['TEMPORARY_HOLD'] = True
                            break
                        elif DATASET['RESULT']['resveNo'] is not None:
                            message(DATASET, str(room['fcltyNm']) + ' 이미 점유 중 계속 진행합니다. ')
                            DATASET['TEMPORARY_HOLD'] = True
                            break
                        else:
                            RESULT_MSG = str(room['fcltyNm']) + ' ' + DATASET['RESULT']['rsltMsg']
                    else:
                        if NO_AVAILABLE:
                            NO_AVAILABLE = False
                        error(DATASET)

            if not DATASET['TEMPORARY_HOLD']:
                for room in DATASET['CANCEL_ROOMS']:
                    name = str(room['fcltyNm']).replace('호', '').replace('번', '')
                    if str(name) in DATASET['ROOM_SELT'] or len(DATASET['ROOM_SELT']) == 0:
                        DATASET['FINAL_ROOM_NAME'] = str(room['fcltyNm'])
                        DATASET['fcltyCode'] = str(room['fcltyCode'])
                        DATASET['resveNoCode'] = str(room['resveNoCode'])
                        DATASET['ERROR_CODE'] = 'spot get_facility'
                        DATASET = get_facility(DATASET)
                        if DATASET['RESULT']['status_code'] == 200 and 'rsltMsg' in DATASET['RESULT']:
                            if DATASET['RESULT']['rsltMsg'] == '선택하신 시설이 선점되었습니다.':
                                DATASET['TEMPORARY_HOLD'] = True
                                break
                            elif DATASET['RESULT']['resveNo'] is not None:
                                message(DATASET, str(room['fcltyNm']) + ' 이미 점유 중 계속 진행합니다. ')
                                DATASET['TEMPORARY_HOLD'] = True
                                break
                            else:
                                message(DATASET, '취소 건 강제 선점 중 ' + str(room['fcltyNm']))
                                DATASET['TEMPORARY_HOLD'] = True
                                break
                        else:
                            if NO_AVAILABLE:
                                NO_AVAILABLE = False
                            error(DATASET)
            if DATASET['TEMPORARY_HOLD']:
                break
            else:
                #message(DATASET, RESULT_MSG)
                break

        if DATASET['AVAILABLE_TEXT_MSG'] == '':
            DATASET['AVAILABLE_TEXT_MSG'] = '예약 가능한 대상이 없습니다. 최초 체크 시간: ' + str(datetime.now().strftime('%Y-%m-%d %H:%M'))
    else:
        message(DATASET, '예약 가능한 대상이 없습니다.')
    return DATASET


def find_want_rooms(DATASET):
    DATASET['CURRENT_PROCESS'] = 'find_want_rooms'
    if len(DATASET['ROOM_SELT']) == 0:
        DATASET['FINAL_ROOM_NAME'] = str(DATASET['AVAILABLE_ROOMS'][0]['fcltyNm'])
        DATASET['fcltyCode'] = str(DATASET['AVAILABLE_ROOMS'][0]['fcltyCode'])
        DATASET['resveNoCode'] = str(DATASET['AVAILABLE_ROOMS'][0]['resveNoCode'])

        if DATASET['fcltyCode'][0:2] == 'DD':
            DATASET['FINAL_TYPE_NAME'] = '든바다'
        elif DATASET['fcltyCode'][0:2] == 'NG':
            DATASET['FINAL_TYPE_NAME'] = '난바다'
        elif DATASET['fcltyCode'][0:2] == 'HB':
            DATASET['FINAL_TYPE_NAME'] = '허허바다'
        else:
            DATASET['FINAL_TYPE_NAME'] = DATASET['SITE_TEXT']

    else:
        for room in DATASET['AVAILABLE_ROOMS']:
            name = str(room['fcltyNm']).replace('호', '').replace('번', '')
            if str(name) in DATASET['ROOM_SELT']:
                DATASET['FINAL_ROOM_NAME'] = str(room['fcltyNm'])
                DATASET['fcltyCode'] = str(room['fcltyCode'])
                DATASET['resveNoCode'] = str(room['resveNoCode'])

    if 'fcltyCode' in DATASET and 'resveNoCode' in DATASET:
        DATASET['ERROR_CODE'] = 'find_want_rooms -> get_facility'
        DATASET = get_facility(DATASET)
        if DATASET['RESULT']['status_code'] == 200 and 'rsltMsg' in DATASET['RESULT']:
            if DATASET['RESULT']['resveNo'] is not None:
                DATASET['TEMPORARY_HOLD'] = True
                DATASET['START_TIME'] = time.time()
                #if DATASET['FINAL_RESERVE']:
                #    DATASET = final_reservation(DATASET)
                #    if DATASET['RESULT']['status_code'] == 200:
                #        message(DATASET, str(room['fcltyNm']) + ' 예약이 완료되었습니다. ')
                #        exit('예약 완료 시스템 종료')
        else:
            DATASET['TEMPORARY_HOLD'] = False
            error(DATASET)
    return DATASET


def direct_link(DATASET):
    DATASET['CURRENT_PROCESS'] = 'direct_link'
    # DIRECT 화면이동
    DATASET['RESULT'] = insertTracking(DATASET)
    html = '''
                                    <form id="postForm" method="POST" action="https://www.campingkorea.or.kr/user/reservation/BD_reservationReq.do">
                                      <input type="hidden" name="trrsrtCode" value="1000">
                                      <input type="hidden" name="q_trrsrtCd" value="">
                                      <input type="hidden" name="q_year" value=''' + '"' + DATASET['year'] + '"' + '''>
                                      <input type="hidden" name="q_month" value=''' + '"' + DATASET['month'] + '"' + '''>
                                      <input type="hidden" name="flag" value="Y">
                                      <input type="hidden" name="resveBeginDe" value=''' + '"' + DATASET[
        'FROM_DATE'] + '"' + '''>
                                      <input type="hidden" name="stayngPd" value="">
                                      <input type="hidden" name="resveEndDe" value=''' + '"' + DATASET['TO_DATE'] + '"' + '''>
                                      <input type="hidden" name="answer" value="">
                                    </form>
                                    <script>
                                      document.getElementById('postForm').submit();
                                    </script>
                                    '''
    DATASET['LOGIN_BROWSER'].get("DATASET:text/html;charset=utf-8," + html)
    time.sleep(3)
    # VK_RETURN은 Enter 키
    win32gui.PostMessage(DATASET['MY_WINDOW'], win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
    time.sleep(0.05)
    win32gui.PostMessage(DATASET['MY_WINDOW'], win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    # 사실 상 매크로 종료.
    time.sleep(300)
    return DATASET


def remove_temp(DATASET):
    DATASET['CURRENT_PROCESS'] = 'remove_temp'
    # 해제할 때만 사용
    if DATASET['TEMPORARY_HOLD']:
        DATASET['TEMPORARY_HOLD'] = False
    return DATASET


def create_new_browser(driver):
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)
    driver.maximize_window()
    return driver


def message(DATASET, text):
    DATASET['CURRENT_PROCESS'] = 'message'
    if DATASET['MESSAGE'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE'] = text
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

def temporary_hold(DATASET):

    OPEN_TIME = datetime.now().strftime("%Y-%m-%d") + ' 11:00:15'
    OPEN_TIMER = datetime.strptime(OPEN_TIME, '%Y-%m-%d %H:%M:%S')

    START_TIMER = datetime.strptime(DATASET['RESULT']['preocpcEndDt'], '%Y-%m-%d %H:%M:%S') + timedelta(seconds=0)
    END_TIMER = datetime.strptime(DATASET['RESULT']['preocpcEndDt'], '%Y-%m-%d %H:%M:%S') + timedelta(seconds=9999)
    CURRENT_TIMER = datetime.now()
    #if (START_TIMER <= CURRENT_TIMER <= END_TIMER) or (CURRENT_TIMER >= OPEN_TIMER):
    if START_TIMER <= CURRENT_TIMER <= END_TIMER:
        DATASET['RE_TRIED'] = False
        DATASET['ERROR_CODE'] = 'RE_TRIED get_facility'
        while not DATASET['RE_TRIED']:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            DATASET = get_facility(DATASET)
            if DATASET['RESULT']['status_code'] == 200 and 'rsltMsg' in DATASET['RESULT']:
                if DATASET['RESULT']['rsltMsg'] == '선택하신 시설이 선점되었습니다.':
                    DATASET['RE_TRIED'] = True
                    if DATASET['FINAL_RESERVE'] and (CURRENT_TIMER >= OPEN_TIMER or DATASET['MODE_ALWS']):
                        DATASET = final_reservation(DATASET)
                        if DATASET['RESULT']['status_code'] == 200:
                            message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
                            DATASET['FINAL_ROOM_NAME']) + ' 예약이 완료되었습니다. ')
                            exit('예약 완료 시스템 종료')
                    else:
                        message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
                            DATASET['FINAL_ROOM_NAME']) + ' ' + str(DATASET['FROM_DATE']) + ' ' + str(
                            DATASET['PERIOD']) + '박 재 점유 되었습니다. ' + str(
                            DATASET['RESULT']['preocpcBeginDt']) + ' ~ ' + str(DATASET['RESULT']['preocpcEndDt']))
                else:
                    if DATASET['FINAL_RESERVE'] and (CURRENT_TIMER >= OPEN_TIMER or DATASET['MODE_ALWS']):
                        DATASET = final_reservation(DATASET)
                        if DATASET['RESULT']['status_code'] == 200:
                            message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
                            DATASET['FINAL_ROOM_NAME']) + ' 예약이 완료되었습니다. ')
                            exit('예약 완료 시스템 종료')
                        else:
                            message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
                                DATASET['FINAL_ROOM_NAME']) + ' ' + str(DATASET['FROM_DATE']) + ' ' + str(
                                DATASET['PERIOD']) + '박 점유 실패 재 예약 중..  ' + str(
                                DATASET['RESULT']['preocpcBeginDt']) + ' ~ ' + str(DATASET['RESULT']['preocpcEndDt']))
                    else:
                        message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
                            DATASET['FINAL_ROOM_NAME']) + ' ' + str(DATASET['FROM_DATE']) + ' ' + str(
                            DATASET['PERIOD']) + '박 재 예약 송신 중... ' + str(
                            DATASET['RESULT']['preocpcBeginDt']) + ' ~ ' + str(DATASET['RESULT']['preocpcEndDt']))

            else:
                DATASET['ERROR_CODE'] = 'retry get_facility'
                DATASET = get_facility(DATASET)
                error(DATASET)
    else:
        message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(
            DATASET['FINAL_ROOM_NAME']) + ' ' + str(DATASET['FROM_DATE']) + ' ' + str(
            DATASET['PERIOD']) + '박 임시점유 대기 중 입니다. ' + str(DATASET['RESULT']['preocpcBeginDt']) + ' ~ ' + str(DATASET['RESULT']['preocpcEndDt']))
    return DATASET

for i in range(machine):
    nametag = i + 1
    name = "MACHINE{}".format(nametag)
    DATASET['name'] = name
    DATASET['nametag'] = nametag
    t = Worker(DATASET)  # sub thread 생성
    t.start()
    time.sleep(time_cut)
