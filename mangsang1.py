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
import pyautogui as py
import numpy as np
import cv2
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
period = 1  # 연박 수
delay = 1
night_delay = 5  # 모니터링 리프레시 속도
room_exception = []
#든바다
#2인실 ['104','105', '107', '108', '113', '114', '117', '118']
#4인실 ['120', '121', '122', '123', '103', '109', '116', '102', '111']
#6인실 ['112', '115', '119']
#8인실 ['101', '110']
#10인실 ['106']
#난바다
#4인실 ['103', '104', '107', '108', '111', '112']
#6인실 ['105', '102', '110', '114']
#8인실 ['101', '109', '113']
#10인실 ['106', '115']
#허허바다
#2인실 ['104','105', '107', '108', '113', '114', '117', '118']
#4인실 ['106', '107', '104', '103']
#6인실 ['105']
#8인실 ['102']
#10인실 ['101', '108']
#자동차야영장 1~41번까지
#앞열 5~13
#취사장 가까운 열 1~4
#room_want = ['115']
#room_want = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
room_want = []
room_selt = []

sel_year_list = ['2025']
sel_month_list = ['07']
sel_date_list = ['12']
site = '3'

continue_work = False
trying = False
current_room = '0'
user_type = 1  # 사용자 정보 세팅

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
    rpwd = 'p1357924680'
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
    'MONITOR': True,
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
    'CYCLE_ERR_CNT': 0
}

if DATASET['SITE'] == '1':
    DATASET['SITE_TEXT'] = '든바다'
    DATASET['faciltyNo'] = '1300'
    DATASET['resveNoCode'] = 'MA'
elif DATASET['SITE'] == '2':
    DATASET['SITE_TEXT'] = '난바다'
    DATASET['faciltyNo'] = '1400'
    DATASET['resveNoCode'] = 'MB'
elif DATASET['SITE'] == '3':
    DATASET['SITE_TEXT'] = '허허바다'
    DATASET['faciltyNo'] = '1500'
    DATASET['resveNoCode'] = 'MI'
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
elif DATASET['SITE'] == '7':   #2인
    DATASET['SITE_TEXT'] = '글램핑'
    DATASET['faciltyNo'] = '1801'
    DATASET['resveNoCode'] = 'LB'
elif DATASET['SITE'] == '8':   #4인
    DATASET['SITE_TEXT'] = '글램핑'
    DATASET['faciltyNo'] = '1802'
    DATASET['resveNoCode'] = 'LA'
elif DATASET['SITE'] == '9':
    DATASET['SITE_TEXT'] = '캐빈하우스'
    DATASET['faciltyNo'] = '1200'
    DATASET['resveNoCode'] = 'CH'
elif DATASET['SITE'] == '10':
    #든, 난, 허 순
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
    if len(room_want) == 0:
        DATASET['ROOM_WANT'] = ['ALL']
    else:
        DATASET['ROOM_WANT'] = room_want

    DATASET = message(DATASET, '감시 모드 시작')
    DATASET = message(DATASET, '입력정보 ' + str(DATASET['SITE_TEXT']) + ' / ' + str(DATASET['ROOM_WANT']))

    # 변수

    DATASET['LOGIN_BROWSER'] = webdriver.Chrome(options=options)
    DATASET = login(DATASET)

    while True:

        ELAPSED_TIME = time.time() - DATASET['LOGIN_TIME']  # 로그인 후 경과 시간 계산
        if ELAPSED_TIME >= 1800 and not DATASET['TEMPORARY_HOLD']:
            DATASET = relogin(DATASET)

        try:
            #실시간 감시 모드
            if DATASET['MONITOR']:

                #_isTarget = False
                #while not _isTarget:
                #    for year in sel_year_list:
                #        for month in sel_month_list:
                #            for date in sel_date_list:
                #                DATASET['year'] = str(year)
                #                DATASET['month'] = str(month)
                #                DATASET['date'] = str(date)
                #                DATASET['ERROR_CODE'] = 'check_available'
                #                DATASET['RESULT'] = check_available(DATASET)
                #                if DATASET['RESULT'].get('status_code') != 200:
                #                    DATASET = message(DATASET, str(DATASET['RESULT']))
                #                    DATASET = error(DATASET)
                #                else:
                #                    DATASET['ERROR_CODE'] = 'if DATASET[' + 'RESULT].get(' + 'value' + ') is not None'
                #                    if DATASET['RESULT'].get('value', None) is not None:
                #                        _list = DATASET['RESULT'].get('value').split('|^|')
                #                        for _roomType in _list:
                #                            if not '예약완료' in _roomType and str(DATASET['SITE_TEXT']) in _roomType:
                #                                DATASET = message(DATASET, '예약 리스트 활성화 확인')
                #                                _isTarget = True
                #                    else:
                #                        error(DATASET)
                #                        message(DATASET, '10초 후 계속 진행됩니다...'
                #                                         '' + str(DATASET['RESULT']))
                #                        time.sleep(10)

                for year in sel_year_list:
                    for month in sel_month_list:
                        for date in sel_date_list:
                            DATASET['year'] = str(year)
                            DATASET['month'] = str(month)
                            DATASET['date'] = str(date)
                            DATASET['FINAL_ROOM_NAME'] = DATASET['SITE_TEXT']

                            #임시 점유시 처리
                            if DATASET['TEMPORARY_HOLD']:
                                elapsed_time = time.time() - DATASET['START_TIME']
                                if elapsed_time >= 550:
                                    # 기 임시 점유건 전부 제거
                                    DATASET['ERROR_CODE'] = 'delete_reserve'
                                    response = delete_reserve(DATASET)
                                    if response['status_code'] == 200:
                                        DATASET = message(DATASET, '임시 점유 정보 CLEAR 및 재 점유')
                                        DATASET['ERROR_CODE'] = 'get_facility'
                                        response = get_facility(DATASET)
                                        if response['status_code'] == 200:
                                            DATASET['TEMPORARY_HOLD'] = True
                                        else:
                                            error(DATASET)
                                    else:
                                        error(DATASET)
                                else:
                                    message(DATASET, '[' + str(DATASET['FINAL_TYPE_NAME']) + '] ' + str(DATASET['FINAL_ROOM_NAME']) + ' ' + str(DATASET['FROM_DATE']) + ' ' + str(DATASET['PERIOD']) + '박 임시점유 대기 중 (' + str(int(elapsed_time/60)) + ')분 지났습니다.')

                            #임시 점유가 없으면 처리
                            elif not DATASET['TEMPORARY_HOLD']:
                                DATASET['FROM_DATE'] = (datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'], '%Y%m%d')).strftime('%Y-%m-%d')
                                DATASET['TO_DATE'] = (datetime.strptime(DATASET['year'] + DATASET['month'] + DATASET['date'], '%Y%m%d') + timedelta(days=int(period))).strftime('%Y-%m-%d')

                                if DATASET['SITE'] == '10':
                                    for index in range(len(DATASET['faciltyNoList'])):
                                        DATASET['faciltyNo'] = DATASET['faciltyNoList'][index]
                                        DATASET['resveNoCode'] = DATASET['resveNoCodeList'][index]
                                        DATASET['ERROR_CODE'] = 'reservation_list'
                                        DATASET['RESULT'] = reservation_list(DATASET)
                                        if DATASET['RESULT']['status_code'] == 200 and DATASET['RESULT']['value'] is not None:
                                            DATASET = reservationList_filter(DATASET)
                                        elif DATASET['RESULT']['status_code'] != 200:
                                            error(DATASET)

                                    if len(DATASET['AVAILABLE_ROOMS']) == 0:
                                        DATASET = remove_temp(DATASET)
                                        message(DATASET, '점유 불가' + str(DATASET['RESULT']['message']))

                                    if DATASET['SITE'] == '10':
                                        if len(DATASET['AVAILABLE_ROOMS']) == 0:
                                            message(DATASET, DATASET['FINAL_TYPE_NAME'] + ' ' + str(DATASET['CANCELING_ROOMS']) + ' 취소 대기 중 ' + DATASET['AVAILABLE_TEXT_MSG'])
                                        else:
                                            message(DATASET, DATASET['SITE_TEXT'] + ' 예약가능 : ' + str(DATASET['ROOM_NAMES']))
                                            DATASET = find_want_rooms(DATASET)

                                else:
                                    DATASET['ERROR_CODE'] = 'reservation_list'
                                    DATASET['RESULT'] = reservation_list(DATASET)
                                    if DATASET['RESULT']['status_code'] == 200 and DATASET['RESULT']['value'] is not None:
                                        DATASET = reservationList_filter(DATASET)
                                    elif DATASET['RESULT']['status_code'] != 200:
                                        error(DATASET)
                                    else:
                                        DATASET = remove_temp(DATASET)
                                        message(DATASET, str('점유 불가' + DATASET['RESULT']['message']) + ' 예약 가능대상 확인 중...')

            #TIMING 예약
            #elif not DATASET['MONITOR']:


                
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

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


#자리선점
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
    print(str(dict_data))
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


#자리선점
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


def login(data):
    driver = data['LOGIN_BROWSER']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)
    driver.maximize_window()

    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(rid)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(rpwd)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    #wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "jsBtnClose2")))
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "banner")))
    _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
    for banner in _bannerList:
        banner.find_element(By.TAG_NAME, 'button').click()
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
    _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
    for banner in _bannerList:
        banner.find_element(By.TAG_NAME, 'button').click()

    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "util")))
    exit_tag = driver.find_elements(By.CLASS_NAME, "util")
    exit_tag[0].find_elements(By.CSS_SELECTOR, "a")[0].click()
    data = login(data)
    return data


def reservationList_filter(data):
    room_list = data['RESULT']['value']['childFcltyList']

    if data['SITE'] != '10':
        data['AVAILABLE_ROOMS'] = []
        data['CANCELING_ROOMS'] = []
        data['ROOM_NAMES'] = []

    for data['ROOM'] in room_list:
        data['AVAILABLE_YN'] = str(data['ROOM']['resveAt'])
        data['CANCEL_YN'] = str(data['ROOM']['canclYn'])
        if data['AVAILABLE_YN'] == 'Y' and data['CANCEL_YN'] == 'Y':
            data['ROOM_NAME'] = str(data['ROOM']['fcltyNm']).replace('호', '').replace('번','')  # naming으로 처리하여 식별하기
            if str(data['ROOM_NAME']) in data['ROOM_WANT'] or (len(data['ROOM_WANT']) == 1 and data['ROOM_WANT'][0] == 'ALL'):
                data['AVAILABLE_ROOMS'].append(data['ROOM'])
                data['ROOM_NAMES'].append(str(data['ROOM']['fcltyNm']))
        else:
            if data['AVAILABLE_YN'] == 'Y' and data['CANCEL_YN'] == 'N':    #가능하지만 취소 N 상태 Y는 취소아님 활성화임
                data['CANCELING_ROOMS'].append(str(data['ROOM']['fcltyNm']))
            if data['AVAILABLE_YN'] != 'Y':
                data['AVAILABLE_TEXT_MSG'] = '예약이 이미 마감되었습니다.'
            if data['CANCEL_YN'] == 'Y':
                data['AVAILABLE_TEXT_MSG'] = '취소 예약이라 대기 중 입니다. 최초 체크 시간: ' + str(datetime.now().strftime('%Y-%m-%d %H:%M'))
            #예약 가능한 방이 없기 때문에 임시 점유는 점유 되어 있으면 해제한다. 신규 시도를 위한
            data = remove_temp(data)
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

        if data['faciltyNo'] == '1300':
            data['FINAL_TYPE_NAME'] = '든바다'
        elif data['faciltyNo'] == '1400':
            data['FINAL_TYPE_NAME'] = '난바다'
        elif data['faciltyNo'] == '1500':
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
    else:
        DATASET['TEMPORARY_HOLD'] = False
        error(DATASET)
    return data


def remove_temp(data):
    #해제할 때만 사용
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
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ######################  ERROR! ' + str(data['ERROR_CODE']) + '  ######################')
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
