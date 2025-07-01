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
test = True
room_exception = []
#room_want = ['103', '105', '107', '108', '113', '114', '117', '118']
#2인실 ['104' ,'105', '107', '108', '113', '114', '117', '118']
#4인실 ['102', '103', '109', '111', '116', '120', '121', '122', '123']
#6인실 ['112', '115', '119']
#8인실 ['101', '110']
#10인실 ['106']
#자동차야영장 1~41번까지
#앞열 5~13
#취사장 가까운 열 1~4
#room_want = ['115']
room_want = [27]
room_pick = []

sel_year_list = ['2025']
sel_month_list = ['07']
sel_date_list = ['21']

continue_work = False
trying = False
current_room = '0'
user_type = 1  # 사용자 정보 세팅

user_name = ''
user_phone = ''
rpwd = ''
rid = ''
email = ''
domain = ''
area1 = ''
area2 = ''
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

dataset = {"reservated": False}

#예약 타입 text
site_text = ''
faciltyNo = ''
faciltyCode = ''
text_code = ''
site = '6'
if site == '1':
    site_text = '든바다'
    faciltyNo = '1300'
    faciltyCode = 'MA'
    text_code = ''
elif site == '2':
    site_text = '난바다'
    faciltyNo = '1400'
    faciltyCode = 'MB'
    text_code = 'NG'
elif site == '3':
    site_text = '허허바다'
    faciltyNo = '1500'
    faciltyCode = 'MB'
    text_code = 'HE'
elif site == '4':
    site_text = '전통한옥'
    faciltyNo = '1100'
    faciltyCode = 'HA'
    text_code = ''
elif site == '5':
    site_text = '캐라반'
    faciltyNo = '1700'
    faciltyCode = 'BA'
    text_code = ''
elif site == '6':
    site_text = '자동차캠핑장'
    faciltyNo = '1600'
    faciltyCode = 'RR'
    text_code = ''
elif site == '7':
    site_text = '글램핑'  #2인
    faciltyNo = '1801'
    faciltyCode = 'LB'
    text_code = ''
elif site == '8':
    site_text = '글램핑'  #4인
    faciltyNo = '1802'
    faciltyCode = 'LA'
    text_code = ''
elif site == '9':
    site_text = '캐빈하우스'
    faciltyNo = '1200'
    faciltyCode = 'CH'
    text_code = ''
else:
    print('사이트 선택 오류! 시스템 종료')
    exit()


class Worker(threading.Thread):
    def __init__(self, dataset):
        super().__init__()
        self.name = dataset['name']  # thread 이름 지정

    def run(self):
        threading.Thread(target=main(dataset))


def main(dataset):
    first_message = False
    start_time = time.time()
    begin = True
    temp_hold = False
    time_message = ''
    result_msg = ''
    chk_start_time = time.time()
    new_run_cnt = 0
    pre_msg = ''
    pre_target = ''
    pos_msg = ''
    global approve, target_facility
    _checker = False

    _roomstr = ''
    if len(room_want) == 0:
        _roomstr = 'ALL'
    else:
        _roomstr = room_want
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' 감시 모드 시작')
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' 입력정보 ' + str(site_text) + ' / ' + str(_roomstr))

    if test:
        while not _checker:
            _checker = False
            for year in sel_year_list:
                for month in sel_month_list:
                    for date in sel_date_list:
                        result = check_available(year, month, date)
                        if result.get('status_code') != 200:
                            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' 통신 실패 재점검')
                        else:
                            _list = result.get('value').split('|^|')
                            for type in _list:
                                if not '예약완료' in type and site_text in type:
                                    _checker = True
                                    approve = True
                                    if not temp_hold:
                                        print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' 예약 가능 활성화 확인 시스템 기동 시작')
                                    break

    driver = webdriver.Chrome(options=options)
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)
    driver.maximize_window()

    wait = WebDriverWait(driver, 100)

    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(rid)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(rpwd)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    # 팝업 보지않기 제거
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "jsBtnClose2")))

    _cookies = driver.get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
    delete_reserve(cookie_dict)
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' 기존 계정 점유 건 CLEAR')
    while True:
        try:
            if not first_message:
                first_message = True

            wait_time = time.time() - chk_start_time  # 경과된 시간 계산

            if wait_time >= 3600 * new_run_cnt:  # 3600초 == 1시간
                print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' / 경과 시간 : ' + str(new_run_cnt) + '시간')
                new_run_cnt = new_run_cnt + 1
            elif new_run_cnt == 0:
                new_run_cnt = 1

            if approve:
                elapsed_time = 0
                if test:
                    elapsed_time = time.time() - start_time
                    #if temp_hold:
                    #    elapsed_time = time.time() - start_time  # 경과된 시간 계산
                    #    message = '임시점유 대기 시간 ' + str(int(elapsed_time / 60)) + '분 대기 중'
                    #    if time_message != message:
                    #        time_message = message
                    #        print(message)
                    #    else:
                    #        time_message = message
                    if elapsed_time >= 280:
                        response = delete_reserve(cookie_dict)
                        if response['status_code'] == 200:
                            temp_hold = False
                            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + '취소 재 점유를 시도합니다.')

                if not temp_hold or begin or not test:
                    start_time = time.time()
                    begin = False
                    for year in sel_year_list:
                        for month in sel_month_list:
                            for date in sel_date_list:
                                from_date = (datetime.strptime(year + month + date, '%Y%m%d')).strftime('%Y-%m-%d')
                                to_date = (datetime.strptime(year + month + date, '%Y%m%d') + timedelta(days=int(period))).strftime('%Y-%m-%d')

                                new_target = str(from_date) + ' ~ ' + str(to_date) + ' / ' + str(site_text) + ' 예약 시도 중'
                                if pre_target != new_target:
                                    print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' ' + new_target)
                                    pre_target = new_target
                                response = reservation_list(from_date, to_date, faciltyNo, faciltyCode, cookie_dict)
                                room_list = []
                                _isPass = False
                                if response['status_code'] == 200 and response['value'] is not None:
                                    room_list = response['value']['childFcltyList']
                                    _isPass = True
                                else:
                                    temp_hold = False
                                    new_msg = '점유 불가 ' + response['message']
                                    if pos_msg != new_msg:
                                        print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' ' + new_msg)
                                        pos_msg = new_msg

                                if _isPass:
                                    text_msg = ''
                                    _available_rooms = []
                                    _names = []
                                    for room in room_list:
                                        _availableYn = room['resveAt']
                                        _cancelYn = room['canclYn']
                                        if _availableYn == 'Y' and _cancelYn == 'Y':
                                            name = str(room['fcltyNm']).replace('호', '').replace('번', '')   #naming으로 처리하여 식별하기
                                            if str(name) in room_want or len(room_want) == 0:
                                                _available_rooms.append(room)
                                                _names.append(str(room['fcltyNm']))
                                        else:
                                            if _availableYn != 'Y':
                                                text_msg = '예약이 이미 마감되었습니다.'
                                            if _cancelYn == 'Y':
                                                text_msg = '취소 예약이라 대기 중 입니다. 최초 체크 시간: ' + str(datetime.now().strftime('%Y-%m-%d %H:%M'))
                                            temp_hold = False

                                    if len(_available_rooms) == 0:
                                        if pre_msg[0:16] != text_msg[0:16]:
                                            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' ' + text_msg)
                                            pre_msg = text_msg
                                    else:
                                        text_msg = site_text + ' 예약가능 : ' + str(_names)
                                        if pre_msg != text_msg:
                                            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' ' + site_text + ' 예약가능 : ' + str(_names))
                                            pre_msg = text_msg

                                    _isDone = False
                                    for room in _available_rooms:
                                        name = str(room['fcltyNm']).replace('호', '').replace('번', '')
                                        if str(name) in room_pick:
                                            if text_code != '':
                                                target_facility = str(room['fcltyCode'])
                                            response = get_facility(from_date, to_date, target_facility, faciltyCode, cookie_dict)
                                            if response['status_code'] == 200:
                                                _isDone = True
                                                new_message = '###################임시점유 완료 ' + str(from_date) + '~' + str(to_date) + ' / ' + str(site_text) + str(room['fcltyNm'])
                                                if result_msg != new_message:
                                                    print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' ' + new_message)
                                                    result_msg = new_message
                                                temp_hold = True
                                            else:
                                                print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' 임시점유 실패 ' + str(from_date) + '~' + str(to_date) + ' / ' + str(
                                                    site_text) + str(room['fcltyNm']))
                                                temp_hold = False

                                    if not _isDone and len(_available_rooms) > 0:
                                        room = _available_rooms[len(_available_rooms) - 1]
                                        target_facility = str(room['fcltyCode'])
                                        response = get_facility(from_date, to_date, target_facility, faciltyCode,
                                                                cookie_dict)
                                        if response['status_code'] == 200:
                                            _isDone = True
                                            new_message = '###################임시점유 완료 ' + str(from_date) + '~' + str(to_date) + ' / ' + str(site_text) + str(room['fcltyNm'])
                                            if result_msg != new_message:
                                                print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' ' + new_message)
                                                result_msg = new_message
                                            temp_hold = True
                                        else:
                                            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' 임시점유 실패 ' + str(from_date) + '~' + str(to_date) + ' / ' + str(
                                                site_text) + str(room['fcltyNm']))
                                            temp_hold = False

        except Exception as ex:
            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' ' + str(ex))
            #driver.refresh()
            continue


def check_available(year, month, date):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectFcltyCalendarDetail.do"
    dict_data = {
        'trrsrtCode': '1000',
        'q_year': str(year),
        'q_month': str(month),
        'qDay': str(date)
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def reservation_list(from_date, to_date, faciltyNo, faciltyCode, cookies):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectChildFcltyList.do"
    dict_data = {
        'trrsrtCode': '1000',
        'fcltyCode': faciltyNo,
        'resveNoCode': faciltyCode,
        'resveBeginDe': from_date,
        'resveEndDe': to_date
    }

    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=cookies, verify=False)

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
def get_facility(from_date, to_date, faciltyNo, faciltyCode, cookies):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': '1000',
        'fcltyCode': faciltyNo,
        'resveNoCode': faciltyCode,
        'resveBeginDe': from_date,
        'resveEndDe': to_date
    }

    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=cookies, verify=False)

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
def delete_reserve(cookies):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_deletePreOcpcInfo.do"

    response = ''
    while response == '':
        try:
            response = requests.post(url=url, cookies=cookies, verify=False)

            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


for i in range(machine):
    nametag = i + 1
    name = "MACHINE{}".format(nametag)
    dataset['name'] = name
    dataset['nametag'] = nametag
    t = Worker(dataset)  # sub thread 생성
    # t.daemon = True
    t.start()
    time.sleep(time_cut)
