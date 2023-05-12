from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pyautogui as py
import numpy as np
import cv2
import requests
import time
import json
import threading

# 시스템 설정
py.FAILSAFE = False
global try_cnt

machine = 10     # 예약 머신 숫자 높을 수록 압도적이지만, 서버 박살낼 수가 있음.. 조심
time_cut = 10    # 머신 시작 간격


class Worker(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name  # thread 이름 지정

    def run(self):
        threading.Thread(target=main(name))


def main(thread_name):
    sel_month_list = ['06']
    sel_date_list = ['0602', '0603', '0604', '0605', '0606', '0609', '0610', '0611']
    sel_site_list = ['E']
    period = 1      # 연박 수
    sel_num_list = []

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

    # site_index = 0              # 사이트 인텍스 계산 값
    while True:
        for sel_month in sel_month_list:
            form_date = datetime.now().strftime("%Y") + '-' + sel_month + '-'
            # param_date = datetime.now().strftime("%Y") + sel_month

            # if target_btn != 'D':
            for date in sel_date_list:
                month = date[0:2]
                day = date[2:4]
                if sel_month == month:
                    for site in sel_site_list:
                        target_date = form_date + str(day)
                        if site == 'A':
                            loop_site_cnt = a_site_cnt  # 사이트 순환 돌릴 꺼
                            start_index = target_index_a
                        elif site == 'B':
                            loop_site_cnt = b_site_cnt  # 사이트 순환 돌릴 꺼
                            start_index = target_index_b
                        elif site == 'C':
                            loop_site_cnt = c_site_cnt  # 사이트 순환 돌릴 꺼
                            start_index = target_index_c
                        elif site == 'D':
                            loop_site_cnt = d_site_cnt  # 사이트 순환 돌릴 꺼
                            start_index = target_index_d
                        elif site == 'E':
                            loop_site_cnt = e_site_cnt  # 사이트 순환 돌릴 꺼
                            start_index = target_index_e
                        for site_index in range(loop_site_cnt):
                            url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_tracking.json'  # 솔향기 커넥션 정보 GET
                            data = {
                                'actFile': 'tracking',
                                'actMode': 'Areain',
                                'actZone': site,
                                'actDate': target_date
                            }  # 요청할 데이터
                            response = web_request_no_cookie(method_name='POST', url=url, dict_data=data)

                            if response.get('status_code') == 200:
                                dict_data = json.loads(response.get('text')).get('data')

                            room_key = str('appRoom[') + str(start_index) + str("]")
                            machine_id_txt = str(thread_name) + ' ::: 예약 : ' + site + ' ' + target_date + ' ' + room_key + ' -> '
                            cookie = response.get('cookies')
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
                            response = web_request(method_name='POST', url=url, dict_data=data, cookies=cookie)
                            if response.get('status_code') != 200:
                                print(machine_id_txt + '네트워크 전송에 실패하였습니다.')
                            else:
                                result_txt = json.loads(response.get('text'))
                                if result_txt.get('ERROR') == '이미 예약되었거나, 예약할 수 없는 구역이 선택되었습니다.' \
                                        or result_txt.get('ERROR') == '선택하신 기간은 예약할 수 없습니다.' \
                                        or result_txt.get('ERROR') == '자동입력방지코드가 일치하지 않습니다.':
                                    print(machine_id_txt + result_txt.get('ERROR'))
                                dict_data = json.loads(response.get('text')).get('data')

                            if dict_data:
                                url = 'https://camping.gtdc.or.kr/DZ_reservation/procedure/execCamping_reservation.json'  # 솔향기 커넥션 정보 GET
                                data = {
                                    'appName': '박상민',  # 이름
                                    'appMobile_1': '010',  # 변수
                                    'appMobile_2': '2486',  # 변수
                                    'appMobile_3': '3038',  # 변수
                                    'appMobile_Sending': 'Y',  # 정보 제공 Y 고정
                                    'appEmail_id': 'psm0705',  # 변수
                                    'appEmail_dom': 'gmail.com',  # 변수
                                    'startArea_1': '경기도',
                                    'startArea_2': '남양주시',
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
                                response = web_request(method_name='POST', url=url, dict_data=data, cookies=cookie)
                                if response.get('status_code') == 200:
                                    print(machine_id_txt + str(datetime.now().strftime("%X")) + "예약 완료")
                                    exit()
                            start_index = start_index + 1
            # else:
            # print(str(datetime.now().strftime("%X")) + target_btn + " 지정일 예약 가능 정보 수신 불가")

def captcha(cookie, thread_name):
    # 이미지 로드
    millisec = int(time.time() * 1000)
    url = "https://camping.gtdc.or.kr/DZ_reservation/CAPTCHA/code_numbers.png?v=" + str(millisec)
    response = requests.post(url=url, cookies=cookie)
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
    #print(str(datetime.now().strftime("%X")) + ' color code : ' + cpatcha_code)
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

def web_request(method_name, url, dict_data, cookies, is_urlencoded=True):
    """Web GET or POST request를 호출 후 그 결과를 dict형으로 반환 """
    method_name = method_name.upper()  # 메소드이름을 대문자로 바꾼다
    if method_name not in ('GET', 'POST'):
        raise Exception('method_name is GET or POST plz...')

    if method_name == 'GET':  # GET방식인 경우
        response = requests.get(url=url, params=dict_data)
    elif method_name == 'POST':  # POST방식인 경우
        if is_urlencoded is True:
            response = requests.post(url=url, data=dict_data,
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'}, cookies=cookies)
        else:
            response = requests.post(url=url, data=json.dumps(dict_data),
                                     headers={'Content-Type': 'application/json'},
                                     cookies=cookies)

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}

def web_request_no_cookie(method_name, url, dict_data, is_urlencoded=True):
    """Web GET or POST request를 호출 후 그 결과를 dict형으로 반환 """
    method_name = method_name.upper()  # 메소드이름을 대문자로 바꾼다
    if method_name not in ('GET', 'POST'):
        raise Exception('method_name is GET or POST plz...')

    if method_name == 'GET':  # GET방식인 경우
        response = requests.get(url=url, params=dict_data)
    elif method_name == 'POST':  # POST방식인 경우
        if is_urlencoded is True:
            response = requests.post(url=url, data=dict_data,
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'})
        else:
            response = requests.post(url=url, data=json.dumps(dict_data),
                                     headers={'Content-Type': 'application/json'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}


for i in range(machine):
    nametag = i + 1
    name = "MACHINE{}".format(nametag)
    t = Worker(name)  # sub thread 생성
    t.start()
    time.sleep(time_cut)