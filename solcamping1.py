from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from datetime import datetime
from user_agent import generate_user_agent, generate_navigator
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
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


# 시스템 설정
py.FAILSAFE = False
options = Options()
options.add_experimental_option("detach", True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
global try_cnt

machine = 1  # 예약 머신 숫자 높을 수록 압도적이지만, 서버 박살낼 수가 있음.. 조심
time_cut = 5  # 머신 시작 간격
period = 1  # 연박 수
day_delay = 1
delay = 0
night_delay = 5  # 모니터링 리프레시 속도
test = True
#room_exception = ['501', '502']
room_exception = []
room_want = ['503']
sel_month_list = ['09']
sel_date_list = ['0913']
site = 'E'

continue_work = False
trying = False
current_room = '0'
user_type = 9  # 사용자 정보 세팅

user_name = ''
user_phone = ''
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
    user_phone = '01024863033'
    email = 'jsy3032'
    domain = 'gmail.com'
    area1 = '경기도'
    area2 = '광명'
elif user_type == 1:
    user_name = '최윤정'
    user_phone = '01047035795'
    email = 'cdw1317'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '광명'
elif user_type == 2:
    user_name = '김형민'
    user_phone = '01091251464'
    email = 'ttasik_asp'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '성남'
elif user_type == 3:
    user_name = '권혁인'
    user_phone = '01020569536'
    email = 'sochi007'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '남양주'
elif user_type == 4:
    user_name = '원성광'
    user_phone = '01024277670'
    email = 'dnjstjdrhkd'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '양평'
elif user_type == 5:
    user_name = '박상민'
    user_phone = '01024863038'
    email = 'psm0705'
    domain = 'gmail.com'
    area1 = '경기도'
    area2 = '의정부'
elif user_type == 6:
    user_name = '박태수'
    user_phone = '01029953995'
    email = 'parktaesu9999'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '부천'
elif user_type == 7:
    user_name = '문광일'
    user_phone = '01064145497'
    email = 'aizylove'
    domain = 'gmail.com'
    area1 = '경기도'
    area2 = '성남'
elif user_type == 8:
    user_name = '박현정'
    user_phone = '01085983083'
    email = 'fpahs414'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '구리'
elif user_type == 9:
    user_name = '김명신'
    user_phone = '01022866574'
    email = 'vspyths75cloud'
    domain = 'naver.com'
    area2 = '동탄'
elif user_type == 99:
    user_name = '김수혁'
    user_phone = '01025173038'
    email = 'sook78dock'
    domain = 'gmail.com'
    area1 = '경기도'
    area2 = '화성'
elif user_type == 999:
    user_name = '이유진'
    user_phone = '01083814672'
    email = 'leejin92'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '부천'
elif user_type == 9999:
    user_name = '김혁진'
    user_phone = '01077972487'
    email = 'kimjins88'
    domain = 'naver.com'
    area1 = '경기도'
    area2 = '부천'
elif user_type == 99999:
    user_name = '김수정'
    user_phone = '01056947788'
    email = 'sjflower0723'
    domain = 'gmail.com'
    area1 = '경상북도'
    area2 = '김천'
elif user_type == 999999:
    user_name = '김강민'
    user_phone = '01048983777'
    email = 'kangchlrh11'
    domain = 'gmail.com'
    area1 = '경상북도'
    area2 = '포항'
elif user_type == 9999999:
    user_name = '윤지영'
    user_phone = '0102165418'
    email = 'freechalee111'
    domain = 'gmail.com'
    area1 = '경상남도'
    area2 = '창원'

dataset = {"reservated": False}


class Worker(threading.Thread):
    def __init__(self, dataset):
        super().__init__()
        self.name = dataset['name']  # thread 이름 지정

    def run(self):
        threading.Thread(target=main(dataset))


def main(dataset):
    thread_name = dataset['name']
    nametag = dataset['nametag']
    user_phone1 = user_phone[0:3]
    user_phone2 = user_phone[3:7]
    user_phone3 = user_phone[7:11]

    # 고정 값
    a_site_cnt = 61  # 1~41  148~167 (차액 6) 보정
    b_site_cnt = 41  # 42~82
    c_site_cnt = 25  # 83~107
    d_site_cnt = 9  # 168~177
    e_site_cnt = 10  # 121~130

    target_index_a = 1  # A 사이트 시작 index
    target_index_a_1 = 148  # A 사이트 시작 index
    target_index_b = 42  # B 사이트 시작 index
    target_index_c = 83  # C 사이트 시작 index
    target_index_d = 168  # D 사이트 시작 index
    target_index_e = 121  # E 사이트 시작 index

    first_message = False
    enter_logic = True
    step = ''
    conn = ''
    area = ''
    checkin = ''

    driver = webdriver.Chrome(options=options)
    url = "https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=" + str(
        datetime.now().strftime("%Y") + sel_month_list[0])
    driver.get(url)
    time.sleep(5)
    #driver.find_element(By.NAME, 'today_dpnone').click()
    #time.sleep(1)
    driver.find_element(By.CLASS_NAME, 'btn-dark').click()
    # _cookies = driver.get_cookies()

    while True:
        try:
            if not first_message:
                print('WORKING... : ' + str(thread_name) + ' 예약 중')
                first_message = True

            # date_str_begin = datetime.now().strftime("%Y-%m-%d") + ' 09:59:59'
            # date_str_end = datetime.now().strftime("%Y-%m-%d") + ' 10:00:15'

            date_str_begin = datetime.now().strftime("%Y-%m-%d") + ' 07:00:00'
            date_str_end = datetime.now().strftime("%Y-%m-%d") + ' 23:00:00'

            date_dt_begin = datetime.strptime(date_str_begin, '%Y-%m-%d %H:%M:%S')
            date_dt_end = datetime.strptime(date_str_end, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()

            if date_dt_begin < now < date_dt_end:
                delay = day_delay
            else:
                delay = night_delay

            userAgent = generate_user_agent(os='win', device_type='desktop')

            if (date_dt_begin < now < date_dt_end) or test:
                # if True:
                if enter_logic:
                    time.sleep((nametag - 1) * 1)
                    enter_logic = False
                for sel_month in sel_month_list:
                    global param_date
                    form_date = datetime.now().strftime("%Y") + '-' + sel_month + '-'
                    param_date = str(datetime.now().strftime("%Y") + sel_month)
                    exist_cnt = False
                    if test:
                        # res = requests.get("https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=202407")
                        day_list = driver.find_elements(By.CLASS_NAME, 'mt5')
                        # print(str(thread_name) + ' CHECKING --- ' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        current_date = datetime.now().strftime("%m-%d")

                        index = 1
                        if current_date[0:2] == sel_month:
                            current_st_time = datetime.now().strftime('%H:%M:%S')
                            if current_st_time < '14:00:00':
                                index = index - 1
                            index = index + int(current_date[3:5])

                        temp_sel_date_list = sel_date_list.copy()
                        for dayinfo in day_list:
                            if len(sel_date_list) == 0:
                                print('예약완료 시스템 종료')
                                sys.exit()
                            for date in temp_sel_date_list:
                                if int(index) == int(date[2:4]):
                                    str_idx = dayinfo.text.rfind(site)
                                    if len(dayinfo.text) >= int(str_idx) + 8:
                                        count = int(dayinfo.text[int(str_idx) + 6:int(str_idx) + 7])
                                        if count > 0:
                                            print(dayinfo.text)
                                            exist_cnt = True
                                            break
                                    temp_sel_date_list.remove(date)
                                    break
                            index = index + 1

                    if not test or exist_cnt:
                        for date in sel_date_list:
                            global continue_work
                            global trying

                            month = date[0:2]
                            day = date[2:4]
                            is_code_create = False

                            if test:
                                continue_work = False
                                trying = False
                            if sel_month == month:

                                if len(sel_date_list) >= 1 and not is_code_create:
                                    response = create_room_code(param_date, userAgent, site, form_date + str(day))
                                    if response.get('status_code') == 200:
                                        dict_data = json.loads(response.get('text')).get('data')
                                        step = dict_data['step']
                                        conn = dict_data['conn']
                                        area = dict_data['Area']
                                        checkin = dict_data['Checkin']
                                        is_code_create = True

                                response = checking_zone(param_date, userAgent, step, conn, area, checkin)
                                if response.get('status_code') == 200:

                                    cookie = response.get('cookies')

                                    html_code = BeautifulSoup(response['text'], 'html.parser')
                                    room_list = []
                                    btn_site_list = html_code.find_all('button', class_='areacode')
                                    for btn_site in btn_site_list:
                                        if 'on' in btn_site.attrs['class']:
                                            if btn_site.span.text[1:4] not in room_exception:
                                                room_list.append(btn_site.span.text[1:4])

                                    # 탐색 zone 순서
                                    # Machine 숫자로 단일 지정하게 된다.
                                    pass_logic = True
                                    msg_cnt_check = False
                                    room_want_copy = room_want.copy()
                                    for want in room_want_copy:
                                        if want in room_list:
                                            pass_logic = False
                                            break
                                    if len(room_want_copy) == 0 or pass_logic:
                                        room_want_copy = []
                                        # 가라 데이터 삽입 최소 room_want list로 1회 돌기 위함
                                        room_want_copy.append('99999')

                                    for room in room_list:
                                        if not msg_cnt_check:
                                            print(str(thread_name) + ' : ' + str(
                                                datetime.now().strftime("%X")) + ' ' + 'ROOM LIST : ' + str(room_list))
                                            msg_cnt_check = True

                                        for want in room_want_copy:
                                            if pass_logic or room == want:
                                                try:
                                                    # room = room_list[nametag-1]
                                                    target_date = form_date + str(day)
                                                    if site == 'A':
                                                        loop_site_cnt = a_site_cnt  # 사이트 순환 돌릴 꺼
                                                        start_index = target_index_a
                                                        fix_room_num = 100
                                                        fix_room_num_1 = -6
                                                    elif site == 'B':
                                                        loop_site_cnt = b_site_cnt  # 사이트 순환 돌릴 꺼
                                                        start_index = target_index_b
                                                        fix_room_num = 159
                                                        # 예외 하기 사이트는 추후 추가되어 정렬 숫자가 상위 호환되고 있어서 FIX 값 변경 필요
                                                        if room in ('243', '244', '245'):
                                                            fix_room_num = 54
                                                    elif site == 'C':
                                                        loop_site_cnt = c_site_cnt  # 사이트 순환 돌릴 꺼
                                                        start_index = target_index_c
                                                        fix_room_num = 218
                                                    elif site == 'D':
                                                        loop_site_cnt = d_site_cnt  # 사이트 순환 돌릴 꺼
                                                        start_index = target_index_d
                                                        fix_room_num = 533  # D 예외 참조 : SITE ROOM : 709 APPROOM : 552
                                                    elif site == 'E':
                                                        loop_site_cnt = e_site_cnt  # 사이트 순환 돌릴 꺼
                                                        start_index = target_index_e
                                                        fix_room_num = 380
                                                    url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_tracking.json'  # 솔향기 커넥션 정보 GET
                                                    data = {
                                                        'actFile': 'tracking',
                                                        'actMode': 'Areain',
                                                        'actZone': site,
                                                        'actDate': target_date
                                                    }  # 요청할 데이터
                                                    response = request_step1(userAgent, method_name='POST', url=url,
                                                                             dict_data=data)
                                                    if response.get('status_code') == 200:
                                                        dict_data = json.loads(response.get('text')).get('data')
                                                    cookie = response.get('cookies')

                                                    # for site_index in range(loop_site_cnt):
                                                    # sel_num = 0
                                                    # if int(room) > 0:
                                                    # sel_num = int(room) - fix_room_num
                                                    # if start_index == sel_num or sel_num == 0:

                                                    start_index = int(room) - fix_room_num

                                                    # 객실정보 처리
                                                    # D 사이트 709번은 APP INDEX를 한칸 더 간다.
                                                    if site == 'D' and room == '709':
                                                        start_index = start_index + 1
                                                    room_key = str('appRoom[') + str(start_index) + str("]")
                                                    machine_id_txt = str(datetime.now()) + ' // ' + str(
                                                        thread_name) + ' ::: 예약 : ' + site + ' ' + target_date + ' ' + room_key + '/' + site + str(
                                                        room) + ' -> '
                                                    room_num = str(site + str(int(start_index) + fix_room_num))

                                                    dict_meta = captcha(cookie, thread_name)
                                                    url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_reservation.json'  # 솔향기 커넥션 정보 GET
                                                    data = {
                                                        'step': dict_data.get('step'),
                                                        'conn': dict_data.get('conn'),
                                                        'resArea': dict_data.get('Area'),
                                                        'resCheckin': dict_data.get('Checkin'),
                                                        'resPeriod': str(period),
                                                        'actFile': 'reservation',
                                                        'actMode': 'Entryin',
                                                        room_key: '1',
                                                        'CAPTCHA_TEXT': dict_meta.get('captcha')
                                                    }
                                                    while continue_work:
                                                        if test:
                                                            break
                                                        if trying and not test:
                                                            print(thread_name + ' 이미 예약이 성공하여 프로세스를 종료 합니다.')
                                                            sys.exit()
                                                        # else:
                                                        #    print('시스템 대기 상태 중')
                                                    if not continue_work and not trying:
                                                        continue_work = True
                                                        response = request_step2(userAgent, method_name='POST', url=url,
                                                                                 dict_data=data,
                                                                                 cookies=cookie)
                                                        if response.get('status_code') != 200:
                                                            print(machine_id_txt + '네트워크 전송에 실패하였습니다.')
                                                            continue_work = False
                                                        else:
                                                            result_txt = json.loads(response.get('text'))
                                                            if result_txt.get(
                                                                    'ERROR') == '이미 예약되었거나, 예약할 수 없는 구역이 선택되었습니다.' \
                                                                    or result_txt.get('ERROR') == '선택하신 기간은 예약할 수 없습니다.' \
                                                                    or result_txt.get('ERROR') == '자동입력방지코드가 일치하지 않습니다.' \
                                                                    or result_txt.get('ERROR') == '객실정보가 확인되지 않았습니다.':
                                                                if result_txt.get(
                                                                        'ERROR') == '이미 예약되었거나, 예약할 수 없는 구역이 선택되었습니다.':
                                                                    continue_work = False
                                                                    print(machine_id_txt + ' 이미 선점된 사이트라 재시도 합니다.')
                                                                    # raise Exception('dsdsd')
                                                                    # sys.exit()
                                                                else:
                                                                    continue_work = False
                                                                    print(machine_id_txt + result_txt.get('ERROR'))
                                                            else:
                                                                dict_data = json.loads(response.get('text')).get('data')
                                                                if not trying and dict_data is not None:
                                                                    url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_reservation.json'  # 솔향기 커넥션 정보 GET
                                                                    data = {
                                                                        'appName': user_name,  # 이름
                                                                        'appMobile_1': user_phone1,  # 변수
                                                                        'appMobile_2': user_phone2,  # 변수
                                                                        'appMobile_3': user_phone3,  # 변수
                                                                        'appMobile_Sending': 'Y',  # 정보 제공 Y 고정
                                                                        'appEmail_id': email,  # 변수
                                                                        'appEmail_dom': domain,  # 변수
                                                                        'startArea_1': area1,
                                                                        'startArea_2': area2,
                                                                        'arrivalDate': '14',  # 도착 시간 14시 고정
                                                                        'discountType': '0',  # 할인 정보 없음 고정
                                                                        'step': 'Confirm',  # 승인 플래그
                                                                        'conn': dict_data.get('conn'),
                                                                        'resArea': dict_data.get('Area'),
                                                                        'resCheckin': dict_data.get('Checkin'),
                                                                        'resPeriod': str(period),
                                                                        'resRoom': dict_data.get('Room'),
                                                                        'actFile': 'reservation',
                                                                        'actMode': 'Request'
                                                                    }
                                                                    if not trying:
                                                                        trying = True
                                                                        # print(form_date + str(day) + ' ' + str(thread_name) + ' : ' + str(datetime.now().strftime("%X")) + ' ' + room_num + " 예약 완료")
                                                                        response = request_step3(userAgent,
                                                                                                 method_name='POST',
                                                                                                 url=url,
                                                                                                 dict_data=data,
                                                                                                 cookies=cookie)
                                                                        if response.get('status_code') == 200:
                                                                            print(form_date + str(day) + ' ' + str(
                                                                                thread_name) + ' : ' + str(
                                                                                datetime.now().strftime(
                                                                                    "%X")) + ' ' + room_num + " 예약 완료")
                                                                            if test:
                                                                                break
                                                                        else:
                                                                            print(form_date + str(day) + ' ' + str(
                                                                                thread_name) + ' : ' + str(
                                                                                datetime.now().strftime(
                                                                                    "%X")) + ' ' + room_num + " 예약 실패")
                                                                        if not test:
                                                                            sys.exit()
                                                                    else:
                                                                        if not test:
                                                                            print(
                                                                                thread_name + ' 선행된 예약이 있어, 최종 확정 예약을 수행 하지 않고 종료 합니다.')
                                                                            sys.exit()

                                                    else:
                                                        if not test:
                                                            print(
                                                                thread_name + ' 선행된 예약이 있어, 더 이상 예약 시도를 하지 않고 종료 합니다.')
                                                            sys.exit()
                                                except Exception as ex:
                                                    print(ex)
                                                    continue_work = False
                                                    if trying and not test:
                                                        print(thread_name + ' 이미 예약이 성공하여 프로세스를 종료 합니다.')
                                                        sys.exit()
                                                    print(str(thread_name) + ' 에러 발생 재실행')
                                                    retry_moudule(userAgent, site, target_date, room, fix_room_num,
                                                                  thread_name, continue_work,
                                                                  trying, user_phone1, user_phone2, user_phone3)

            driver.refresh()
            time.sleep(delay)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-dark')))
            driver.find_element(By.CLASS_NAME, 'btn-dark').click()
        except Exception as ex:
            print('EXCEPTION!!!!! // ' + str(ex))
            continue


def retry_moudule(userAgent, site, target_date, room, fix_room_num, thread_name, continue_work, trying, user_phone1, user_phone2,
                  user_phone3):
    print(thread_name + ' 오류 재가동 모듈을 실행합니다.')
    if trying and not test:
        print(thread_name + ' 이미 예약이 성공하여 프로세스를 종료 합니다.')
        sys.exit()
    try:
        url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_tracking.json'  # 솔향기 커넥션 정보 GET
        data = {
            'actFile': 'tracking',
            'actMode': 'Areain',
            'actZone': site,
            'actDate': target_date
        }  # 요청할 데이터
        response = request_step1(userAgent, method_name='POST', url=url, dict_data=data)
        if response.get('status_code') == 200:
            dict_data = json.loads(response.get('text')).get('data')
            cookie = response.get('cookies')

            # for site_index in range(loop_site_cnt):
            #    sel_num = 0
            #    if int(room) > 0:
            #        sel_num = int(room) - fix_room_num
            #    if start_index == sel_num or sel_num == 0:
            start_index = int(room) - fix_room_num
            room_key = str('appRoom[') + str(start_index) + str("]")
            machine_id_txt = str(datetime.now()) + ' // ' + str(
                thread_name) + ' ::: 예약 : ' + site + ' ' + target_date + ' ' + room_key + '/' + site + room + ' -> '
            room_num = str(site + str(int(start_index) + fix_room_num))

            dict_meta = captcha(cookie, thread_name)
            url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_reservation.json'  # 솔향기 커넥션 정보 GET
            data = {
                'step': dict_data.get('step'),
                'conn': dict_data.get('conn'),
                'resArea': dict_data.get('Area'),
                'resCheckin': dict_data.get('Checkin'),
                'resPeriod': str(period),
                'actFile': 'reservation',
                'actMode': 'Entryin',
                room_key: '1',
                'CAPTCHA_TEXT': dict_meta.get('captcha')
            }
            while continue_work:
                print(thread_name + ' 9999')
                if trying and not test:
                    print(thread_name + ' 이미 예약 완료된 기록이 존재 합니다. 종료 합니다.')
                    sys.exit()
                # else:
                #    print('시스템 대기 상태 중')
            if not continue_work and not trying:
                continue_work = True
                response = request_step2(userAgent, method_name='POST', url=url, dict_data=data, cookies=cookie)
                if response.get('status_code') != 200:
                    print(machine_id_txt + '네트워크 전송에 실패하였습니다.')
                    continue_work = False
                else:
                    result_txt = json.loads(response.get('text'))
                    if result_txt.get('ERROR') == '이미 예약되었거나, 예약할 수 없는 구역이 선택되었습니다.' \
                            or result_txt.get('ERROR') == '선택하신 기간은 예약할 수 없습니다.' \
                            or result_txt.get('ERROR') == '자동입력방지코드가 일치하지 않습니다.':
                        if result_txt.get('ERROR') == '이미 예약되었거나, 예약할 수 없는 구역이 선택되었습니다.':
                            continue_work = False
                            print(machine_id_txt + ' 이미 선점된 사이트라 예약 시도를 종료 합니다.')
                            # sys.exit()
                        else:
                            continue_work = False
                            print(machine_id_txt + result_txt.get('ERROR'))
                    else:
                        print(thread_name + ' 5555')
                        dict_data = json.loads(response.get('text')).get('data')
                        if not trying and dict_data is not None:
                            url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_reservation.json'  # 솔향기 커넥션 정보 GET
                            data = {
                                'appName': user_name,  # 이름
                                'appMobile_1': user_phone1,  # 변수
                                'appMobile_2': user_phone2,  # 변수
                                'appMobile_3': user_phone3,  # 변수
                                'appMobile_Sending': 'Y',  # 정보 제공 Y 고정
                                'appEmail_id': email,  # 변수
                                'appEmail_dom': domain,  # 변수
                                'startArea_1': area1,
                                'startArea_2': area2,
                                'arrivalDate': '14',  # 도착 시간 14시 고정
                                'discountType': '0',  # 할인 정보 없음 고정
                                'step': 'Confirm',  # 승인 플래그
                                'conn': dict_data.get('conn'),
                                'resArea': dict_data.get('Area'),
                                'resCheckin': dict_data.get('Checkin'),
                                'resPeriod': str(period),
                                'resRoom': dict_data.get('Room'),
                                'actFile': 'reservation',
                                'actMode': 'Request'
                            }
                            if not trying:
                                trying = True
                                response = request_step3(userAgent, method_name='POST', url=url, dict_data=data,
                                                         cookies=cookie)
                                if response.get('status_code') == 200:
                                    print(str(thread_name) + ' : ' + str(
                                        datetime.now().strftime("%X")) + ' ' + room_num + " 예약 완료")
                                else:
                                    print(str(thread_name) + ' : ' + str(
                                        datetime.now().strftime("%X")) + ' ' + room_num + " 예약 실패")
                                if not test:
                                    sys.exit()
                            else:
                                if not test:
                                    print(thread_name + ' 선행된 예약이 있어, 최종 확정 예약을 수행 하지 않고 종료 합니다.')
                                    sys.exit()
    except Exception as ex:
        print(ex)
        continue_work = False
        if trying and not test:
            print(thread_name + ' 이미 예약이 성공하여 프로세스를 종료 합니다.')
            sys.exit()
        print(str(thread_name) + '에러 발생 재실행2')
        retry_moudule(userAgent, site, target_date, room, fix_room_num, thread_name, continue_work,
                      trying, user_phone1, user_phone2, user_phone3)


def captcha(cookie, thread_name):
    # 이미지 로드
    millisec = int(time.time() * 1000)
    url = "https://camping.gtdc.or.kr/DZ_reservation/CAPTCHA/code_numbers.png?v=" + str(millisec)
    response = requests.post(url=url, cookies=cookie, verify=False)
    if response.status_code == 200:
        with open("captcha" + str(thread_name) + ".png", 'wb') as f:
            f.write(response.content)
    image = Image.open('captcha' + str(thread_name) + '.png')
    image.save('captcha' + str(thread_name) + '.png')
    target_image = cv2.imread('captcha' + str(thread_name) + '.png')
    index = 0
    color = 'b'
    cpatcha_code = '00000'
    while index < 10:
        check_count1 = 0  # 최소 3개 이상 찍혀야 인정하자
        check_count2 = 0  # 최소 3개 이상 찍혀야 인정하자
        check_count3 = 0  # 최소 3개 이상 찍혀야 인정하자
        check_count4 = 0  # 최소 3개 이상 찍혀야 인정하자
        check_count5 = 0  # 최소 3개 이상 찍혀야 인정하자
        check_flag1 = False
        check_flag2 = False
        check_flag3 = False
        check_flag4 = False
        check_flag5 = False
        max_count = 3  # 정교함 밑에 쓰레드홀드랑 연관

        last_index = 0
        color_loop = 0  # 5개의 색깔별 숫자

        while color_loop < 5:
            if color_loop == 0:
                color = 'b'
            elif color_loop == 1:
                color = 'g'
            elif color_loop == 2:
                color = 'r'
            elif color_loop == 3:
                color = 's'
            elif color_loop == 4:
                color = 'y'
            template_name = 'captcha/' + color + str(index) + '.png'
            # 이미지 로드
            img = cv2.imread(template_name)
            # 색상 제거
            # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 타겟 이미지에서 탬플릿 매칭
            result = cv2.matchTemplate(img, target_image, cv2.TM_CCOEFF_NORMED)
            threshold = 0.63  # 절때 건들이지 말것 정확도  맨앞 노란8잡기위함
            loc = np.where(result >= threshold)
            for pt in zip(*loc[::-1]):
                x = pt[0]
                if 1 < x < 10 and not check_flag1:
                    check_count1 = check_count1 + 1
                    # print(str(x) + ' ' + template_name)
                    if last_index != index:
                        check_count1 = 1
                    if check_count1 >= max_count:
                        # print(template_name + ' : 첫번째' + str(x))
                        cpatcha_code = str(index) + cpatcha_code[1:5]
                        check_flag1 = True
                    last_index = index
                elif 30 < x < 40 and not check_flag2:
                    check_count2 = check_count2 + 1
                    if last_index != index:
                        check_count2 = 1
                    if check_count2 >= max_count:
                        # print(template_name + ' : 두번째' + str(x))
                        cpatcha_code = cpatcha_code[0:1] + str(index) + cpatcha_code[2:5]
                        check_flag2 = True
                    last_index = index
                elif 60 < x < 70 and not check_flag3:
                    check_count3 = check_count3 + 1
                    if last_index != index:
                        check_count3 = 1
                    if check_count3 >= max_count:
                        # print(template_name + ' : 세번째' + str(x))
                        cpatcha_code = cpatcha_code[0:2] + str(index) + cpatcha_code[3:5]
                        check_flag3 = True
                    last_index = index
                elif 90 < x < 100 and not check_flag4:
                    check_count4 = check_count4 + 1
                    if last_index != index:
                        check_count4 = 1
                    if check_count4 >= max_count:
                        # print(template_name + ' : 네번째' + str(x))
                        cpatcha_code = cpatcha_code[0:3] + str(index) + cpatcha_code[4:5]
                        check_flag4 = True
                    last_index = index
                elif 120 < x < 130 and not check_flag5:
                    if last_index != index:
                        check_count5 = 1
                    check_count5 = check_count5 + 1
                    if check_count5 >= max_count:
                        # print(template_name + ' : 다섯번째' + str(x))
                        cpatcha_code = cpatcha_code[0:4] + str(index) + cpatcha_code[5:5]
                        check_flag5 = True
                    last_index = index
            color_loop = color_loop + 1

        index = index + 1
    # print(str(datetime.now().strftime("%X")) + ' color code : ' + cpatcha_code)
    dict_meta = {'status_code': response.status_code, 'cookies': cookie, 'captcha': cpatcha_code}
    return dict_meta


def select_area(sel_num_list, wait, driver):
    area_list = driver.find_elements(By.CSS_SELECTOR, "button.on")
    area_found = False
    for area in area_list:
        if len(sel_num_list) > 0:
            for sel_site_num in sel_num_list:
                if (area.find_element(By.CSS_SELECTOR, "span").text == sel_site_num) and not area_found:
                    print(str(datetime.now().strftime("%X")) + ' 사이트 선택 : ' + str(
                        area.find_element(By.CSS_SELECTOR, "span").text))
                    area.click()
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "select.select30")))
                    selector = Select(driver.find_elements(By.CSS_SELECTOR, "select.select30")[0])
                    selector.select_by_index(4)
                    area_found = True

                    break
        else:
            if not area_found:
                print(str(datetime.now().strftime("%X")) + ' 사이트 선택 : ' + str(
                    area.find_element(By.CSS_SELECTOR, "span").text))
                area.click()
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "select.select30")))
                selector = Select(driver.find_elements(By.CSS_SELECTOR, "select.select30")[0])
                selector.select_by_index(4)
                area_found = True

    if not area_found:
        exit(str(datetime.now().strftime("%X")) + ' THERE IS NO AREA ENABLE')


def request_step1(userAgent, method_name, url, dict_data, is_urlencoded=True):
    """Web GET or POST request를 호출 후 그 결과를 dict형으로 반환 """
    method_name = method_name.upper()  # 메소드이름을 대문자로 바꾼다

    if method_name not in ('GET', 'POST'):
        raise Exception('method_name is GET or POST plz...')

    if method_name == 'GET':  # GET방식인 경우
        response = requests.get(url=url, params=dict_data)
    elif method_name == 'POST':  # POST방식인 경우
        if is_urlencoded is True:
            response = requests.post(url=url, data=dict_data, verify=False,
                                     headers={
                                         'Accept': 'application/json, text/javascript, */*; q=0.01',
                                         'Accept-Encoding': 'gzip, deflate, br',
                                         'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                                         'Connection': 'keep-alive',
                                         'Content-Length': '177',
                                         'Content-Type': 'application/x-www-form-urlencoded',
                                         'Host': 'camping.gtdc.or.kr',
                                         'Origin': 'https://camping.gtdc.or.kr',
                                         'Referer': 'https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=' + param_date,
                                         'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                                         'Sec-Ch-Ua-Mobile': '?0',
                                         'Sec-Ch-Ua-Platform': '"Windows"',
                                         'Sec-Fetch-Dest': 'empty',
                                         'Sec-Fetch-Mode': 'cors',
                                         'Sec-Fetch-Site': 'same-origin',
                                         'User-Agent': userAgent,
                                         'X-Requested-With': 'XMLHttpRequest'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}


def request_step2(userAgent, method_name, url, dict_data, cookies, is_urlencoded=True):
    """Web GET or POST request를 호출 후 그 결과를 dict형으로 반환 """
    method_name = method_name.upper()  # 메소드이름을 대문자로 바꾼다

    if method_name not in ('GET', 'POST'):
        raise Exception('method_name is GET or POST plz...')

    if method_name == 'GET':  # GET방식인 경우
        response = requests.get(url=url, params=dict_data)
    elif method_name == 'POST':  # POST방식인 경우
        if is_urlencoded is True:
            response = requests.post(url=url, data=dict_data, cookies=cookies, verify=False,
                                     headers={
                                         'Accept': 'application/json, text/javascript, */*; q=0.01',
                                         'Accept-Encoding': 'gzip, deflate, br',
                                         'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                                         'Connection': 'keep-alive',
                                         'Content-Length': '177',
                                         'Content-Type': 'application/x-www-form-urlencoded',
                                         'Host': 'camping.gtdc.or.kr',
                                         'Origin': 'https://camping.gtdc.or.kr',
                                         'Referer': 'https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=' + param_date + '&step=Areas',
                                         'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                                         'Sec-Ch-Ua-Mobile': '?0',
                                         'Sec-Ch-Ua-Platform': '"Windows"',
                                         'Sec-Fetch-Dest': 'empty',
                                         'Sec-Fetch-Mode': 'cors',
                                         'Sec-Fetch-Site': 'same-origin',
                                         'User-Agent': userAgent,
                                         'X-Requested-With': 'XMLHttpRequest'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}


def request_step3(userAgent, method_name, url, dict_data, cookies, is_urlencoded=True):
    """Web GET or POST request를 호출 후 그 결과를 dict형으로 반환 """
    method_name = method_name.upper()  # 메소드이름을 대문자로 바꾼다

    if method_name not in ('GET', 'POST'):
        raise Exception('method_name is GET or POST plz...')

    if method_name == 'GET':  # GET방식인 경우
        response = requests.get(url=url, params=dict_data)
    elif method_name == 'POST':  # POST방식인 경우
        if is_urlencoded is True:
            response = requests.post(url=url, data=dict_data, cookies=cookies, verify=False,
                                     headers={
                                         'Accept': 'application/json, text/javascript, */*; q=0.01',
                                         'Accept-Encoding': 'gzip, deflate, br',
                                         'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                                         'Connection': 'keep-alive',
                                         'Content-Length': '78',
                                         'Content-Type': 'application/x-www-form-urlencoded',
                                         'Host': 'camping.gtdc.or.kr',
                                         'Origin': 'https://camping.gtdc.or.kr',
                                         'Referer': 'https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=' + param_date + '&step=Entry',
                                         'Sec-Ch-Ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                                         'Sec-Ch-Ua-Mobile': '?0',
                                         'Sec-Ch-Ua-Platform': '"Windows"',
                                         'Sec-Fetch-Dest': 'empty',
                                         'Sec-Fetch-Mode': 'cors',
                                         'Sec-Fetch-Site': 'same-origin',
                                         'User-Agent': userAgent,
                                         'X-Requested-With': 'XMLHttpRequest'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    # dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
    #             'headers': response.headers}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}


def check_sites(sdate, userAgent):
    # 예약 파라미터 세팅
    url = "https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=" + sdate
    response = requests.get(url=url,
                            headers={
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                                'Accept-Encoding': 'gzip, deflate, br, zstd',
                                'Accept-Language': 'ko,en;q=0.9,en-US;q=0.8',
                                'Connection': 'keep-alive',
                                'Content-Length': '317',
                                'Cookie': 'DENOBIZID=sdo845l7s8p8u0ninlh2hbmn21; weather=%7B%222024-06-29%22%3A%7B%22icon%22%3A%22cloud%22%2C%22tmp%22%3A%2219.1%22%2C%22reh%22%3A%2284%22%2C%22wsd%22%3A%222.3%22%7D%2C%222024-06-30%22%3A%7B%22min%22%3A%2222%22%2C%22max%22%3A%2226%22%2C%22icon%22%3A%22rain%22%7D%2C%222024-07-01%22%3A%7B%22min%22%3A%2223%22%2C%22max%22%3A%2223%22%2C%22icon%22%3A%22cloud2%22%7D%2C%222024-07-02%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2226%22%7D%2C%222024-07-03%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-04%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2230%22%7D%2C%222024-07-05%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-06%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2229%22%7D%2C%222024-07-07%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-08%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-09%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2227%22%7D%7D',
                                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'Host': 'camping.gtdc.or.kr',
                                'Origin': 'https://www.cjfmc.or.kr',
                                'Referer': 'https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation',
                                'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
                                'Sec-Ch-Ua-Mobile': '?0',
                                'Sec-Ch-Ua-Platform': '"Windows"',
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'same-origin',
                                'Sec-Fetch-User': '?1',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': userAgent})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}

def checking_zone(sdate, userAgent, step, conn, area, checkin):
    # 예약 파라미터 세팅
    data = {
        'step': step,
        'conn': conn,
        'resArea': area,
        'resCheckin': checkin
    }
    url = "https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=" + sdate + "&step=Areas"
    response = requests.post(url=url, data=data, verify=False,
                            headers={
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                                'Accept-Encoding': 'gzip, deflate, br, zstd',
                                'Accept-Language': 'ko,en;q=0.9,en-US;q=0.8',
                                'Cashe-Control': 'max-age=0',
                                'Connection': 'keep-alive',
                                'Content-Length': '92',
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Cookie': '_fwb=1087YMtDkxacg2rmDe2mK1T.1704761532551; _pk_id.2.e22d=125687f4c95c914f.1716335579.; popupbox_cautionAgree=1; DENOBIZID=730kkdlng6mp1it6mqs7khh3d1; weather=%7B%222024-06-30%22%3A%7B%22min%22%3A%2222%22%2C%22max%22%3A%2226%22%2C%22icon%22%3A%22cloud2%22%2C%22tmp%22%3A%2222.6%22%2C%22reh%22%3A%2297%22%2C%22wsd%22%3A%220.3%22%7D%2C%222024-07-01%22%3A%7B%22min%22%3A%2222%22%2C%22max%22%3A%2223%22%2C%22icon%22%3A%22cloud2%22%7D%2C%222024-07-02%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2226%22%7D%2C%222024-07-03%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-04%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2230%22%7D%2C%222024-07-05%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-06%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2229%22%7D%2C%222024-07-07%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-08%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-09%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2227%22%7D%7D; weather_now=%7B%22sunrise%22%3A%220740%22%2C%22icon%22%3A%22cloud2%22%2C%22tmp%22%3A%2222.6%22%2C%22reh%22%3A%2297%22%2C%22wsd%22%3A%220.3%22%7D; _dz_[aa93685bcc63bc88e7996084b90aaa29]=1; _pk_ref.2.e22d=%5B%22%22%2C%22%22%2C1719682959%2C%22https%3A%2F%2Fsearch.naver.com%2Fsearch.naver%3Fwhere%3Dnexearch%26sm%3Dtop_hty%26fbm%3D0%26ie%3Dutf8%26query%3D%EC%97%B0%EA%B3%A1%2B%EC%86%94%ED%96%A5%EA%B8%B0%22%5D; _pk_ses.2.e22d=1; wcs_bt=30b89a3a9feb3:1719683091',
                                'Host': 'camping.gtdc.or.kr',
                                'Origin': 'https://camping.gtdc.or.kr',
                                'Referer': 'https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=' + sdate,
                                'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
                                'Sec-Ch-Ua-Mobile': '?0',
                                'Sec-Ch-Ua-Platform': '"Windows"',
                                'Sec-Fetch-Dest': 'document',
                                'Sec-Fetch-Mode': 'navigate',
                                'Sec-Fetch-Site': 'same-origin',
                                'Sec-Fetch-User': '?1',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': userAgent})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}


def create_room_code(sdate, userAgent, site, sel_date):
    # 예약 파라미터 세팅
    data = {
        'actFile': 'tracking',
        'actMode': 'Areain',
        'actZone': site,
        'actDate': sel_date
    }
    url = "https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_tracking.json"
    response = requests.post(url=url, data=data, verify=False,
                            headers={
                                'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'Accept-Encoding': 'gzip, deflate, br, zstd',
                                'Accept-Language': 'ko,en;q=0.9,en-US;q=0.8',
                                'Connection': 'keep-alive',
                                'Content-Length': '60',
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Cookie': '_fwb=1087YMtDkxacg2rmDe2mK1T.1704761532551; _pk_id.2.e22d=125687f4c95c914f.1716335579.; popupbox_cautionAgree=1; DENOBIZID=730kkdlng6mp1it6mqs7khh3d1; weather=%7B%222024-06-30%22%3A%7B%22min%22%3A%2222%22%2C%22max%22%3A%2226%22%2C%22icon%22%3A%22cloud2%22%2C%22tmp%22%3A%2222.6%22%2C%22reh%22%3A%2297%22%2C%22wsd%22%3A%220.3%22%7D%2C%222024-07-01%22%3A%7B%22min%22%3A%2222%22%2C%22max%22%3A%2223%22%2C%22icon%22%3A%22cloud2%22%7D%2C%222024-07-02%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2226%22%7D%2C%222024-07-03%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-04%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2230%22%7D%2C%222024-07-05%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-06%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2222%22%2C%22max%22%3A%2229%22%7D%2C%222024-07-07%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-08%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2228%22%7D%2C%222024-07-09%22%3A%7B%22icon%22%3A%22rain%22%2C%22min%22%3A%2223%22%2C%22max%22%3A%2227%22%7D%7D; weather_now=%7B%22sunrise%22%3A%220740%22%2C%22icon%22%3A%22cloud2%22%2C%22tmp%22%3A%2222.6%22%2C%22reh%22%3A%2297%22%2C%22wsd%22%3A%220.3%22%7D; _dz_[aa93685bcc63bc88e7996084b90aaa29]=1; _pk_ref.2.e22d=%5B%22%22%2C%22%22%2C1719682959%2C%22https%3A%2F%2Fsearch.naver.com%2Fsearch.naver%3Fwhere%3Dnexearch%26sm%3Dtop_hty%26fbm%3D0%26ie%3Dutf8%26query%3D%EC%97%B0%EA%B3%A1%2B%EC%86%94%ED%96%A5%EA%B8%B0%22%5D; _pk_ses.2.e22d=1; wcs_bt=30b89a3a9feb3:1719683091',
                                'Host': 'camping.gtdc.or.kr',
                                'Origin': 'https://camping.gtdc.or.kr',
                                'Referer': 'https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=' + sdate,
                                'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
                                'Sec-Ch-Ua-Mobile': '?0',
                                'Sec-Ch-Ua-Platform': '"Windows"',
                                'Sec-Fetch-Dest': 'empty',
                                'Sec-Fetch-Mode': 'cors',
                                'Sec-Fetch-Site': 'same-origin',
                                'User-Agent': userAgent,
                                'X-Requested-With': 'XMLHttpRequest'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}

for i in range(machine):
    nametag = i + 1
    name = "MACHINE{}".format(nametag)
    dataset['name'] = name
    dataset['nametag'] = nametag
    t = Worker(dataset)  # sub thread 생성
    # t.daemon = True
    t.start()
    time.sleep(time_cut)
