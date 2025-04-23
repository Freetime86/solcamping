import sys
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from user_agent import generate_user_agent, generate_navigator


import urllib3
import requests
import threading
import json
from datetime import datetime

# 브라우저를 종료하지 않고 유지하는 옵션
options = Options()
options.add_experimental_option("detach", True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 사이트 선택 ~ 순서는 A부터 절때 역방향이면 안됨!!
# EX A1 ~ B1 이면 A1,2,3,4,5 ~ 와 B사이트 1번까지 랜덤 선택

SITE_FROM = ['A01']
SITE_TO = ['A59']
START_DATE = ['20250503']
END_DATE = ['20250506']
RESERVATION_CNT = 1
SUCCESS_COUNT = 99

# 수시 체크 딜레이
DELAY = 3
# TRUE = 수시 감시, FALSE 실시간 예약
ALWAYS = True

if len(SITE_FROM) != RESERVATION_CNT:
    print("SITE_FROM 확인!!")
    sys.exit()
if len(SITE_TO) != RESERVATION_CNT:
    print("SITE_TO 확인!!")
    sys.exit()
if len(START_DATE) != RESERVATION_CNT:
    print("START_DATE 확인!!")
    sys.exit()
if len(END_DATE) != RESERVATION_CNT:
    print("END_DATE 확인!!")
    sys.exit()
if not ALWAYS:
    print("실시간 감시 모드")
    print("ALWAYS 0초로 변경")
    DELAY = 0
else:
    print("수시 감시 모드")

selectMonth = str(datetime.now().strftime("%Y-%m"))

# 파라미터
_data = {}


class Worker(threading.Thread):
    def __init__(self, _data):
        super().__init__()
        self.name = _data['name']  # thread 이름 지정

    def run(self):
        threading.Thread(target=main_process(_data))


def main_process(_data):
    thread_name = _data['name']

    _start_date = _data['START_DATE' + thread_name]
    _end_date = _data['END_DATE' + thread_name]
    _site_f_type = _data['SITE_F_TYPE' + thread_name]
    _site_t_type = _data['SITE_T_TYPE' + thread_name]
    _site_f_num = _data['SITE_F_NUM' + thread_name]
    _site_t_num = _data['SITE_T_NUM' + thread_name]
    thread_tag = thread_name + ' ' + _start_date + '~' + _end_date

    print(str(datetime.now()) + ' ' + thread_tag + ' ' + 'START!!')
    # 빠른 속도로 파라미터 생성
    param = {
        'tocken': '',
        'UserAgent': '',
        'selectStartDate': _start_date[0:4] + '-' + _start_date[4:6] + '-' + _start_date[6:8],
        'selectEndDate': _end_date[0:4] + '-' + _end_date[4:6] + '-' + _end_date[6:8],
        'selectMonth': selectMonth
    }
    add_f_cnt = 0
    add_t_cnt = 0
    if _site_f_type == 'A':
        add_f_cnt = 696
    if _site_f_type == 'B':
        add_f_cnt = 759
    if _site_f_type == 'C':
        add_f_cnt = 769
    site_f_cnt = _site_f_num + add_f_cnt

    if _site_t_type == 'A':
        add_t_cnt = 696
    if _site_t_type == 'B':
        add_t_cnt = 759
    if _site_t_type == 'C':
        add_t_cnt = 769

    site_t_cnt = _site_t_num + add_t_cnt
    driver = webdriver.Chrome(options=options)
    url = "https://www.cjfmc.or.kr/camping/cjcamp/campsite/L37844353"

    if ALWAYS:
        driver.get(url)
        time.sleep(1)
        _cookies = driver.get_cookies()
        wait = WebDriverWait(driver, 300)
        # token
        wait.until(EC.presence_of_element_located((By.ID, "tocken")))
        param['tocken'] = driver.find_element(By.ID, "tocken").get_attribute('value')

    cycle_cnt = 0
    while True:
        date_str_begin = datetime.now().strftime("%Y-%m-%d") + ' 09:00:00'
        date_dt_begin = datetime.strptime(date_str_begin, '%Y-%m-%d %H:%M:%S')
        now = datetime.now()

        # 헤더 랜덤 생성 request block 방지
        param['UserAgent'] = generate_user_agent(os='win', device_type='desktop')

        if (date_dt_begin < now) or ALWAYS:
            # 조회 API
            if not ALWAYS:
                driver.get(url)
                time.sleep(1)
                _cookies = driver.get_cookies()
                wait = WebDriverWait(driver, 300)
                # token
                wait.until(EC.presence_of_element_located((By.ID, "tocken")))
                param['tocken'] = driver.find_element(By.ID, "tocken").get_attribute('value')

            cookie_dict = {}
            for cookie in _cookies:
                cookie_dict[cookie['name']] = cookie['value']

            response = request_date(param, cookie_dict)
            if response.get('status_code') != 200:
                print(str(datetime.now()) + ' ' + thread_tag + ' 조회 API 오류')
                print(response)
                continue
                #sys.exit()
            else:
                result = json.loads(response['text'])
                _list = result['pinCategoryList'][0]['pinList']
                max_hold = 0
                for site in _list:
                    if site_f_cnt <= int(site['itemId'][17:20]) <= site_t_cnt and site['useAt'] == 'Y':
                        selectItemId = site['itemId']
                        param['selectItemId'] = selectItemId
                        # 예약 API
                        response = request_reservation(param, cookie_dict)

                        # driver.maximize_window()
                        if response.get('status_code') != 200:
                            print(str(datetime.now()) + ' ' + thread_tag + ' 예약 API 오류')
                            sys.exit()
                        else:
                            if response.get('text').find('사이트') != -1:
                                startNum = response.get('text').find('("')
                                endNum = response.get('text').find('")')
                                result = response.get('text')[startNum + 2:endNum]
                                print(str(datetime.now()) + ' ' + thread_tag + ' ' + result + " 예약 완료")
                                param['selectItemId'] = ''
                                max_hold = max_hold + 1
                                driver.refresh()

                    if max_hold >= SUCCESS_COUNT and not ALWAYS:
                        sys.exit(thread_name + ' 종료')

        # 반복문 딜레이 시간
        cycle_cnt = cycle_cnt + 1
        # (print(str(datetime.now()) + ' ' + thread_tag + '   ####################### ' + str(cycle_cnt) + " 번 싸이클" + ' #######################'))
        time.sleep(DELAY)


def request_cookie(param, cookies):
    # 예약 파라미터 세팅
    url = "https://camp.cjfmc.or.kr/cjcamp/campsite/L37844353"
    dict_data = {
        'tocken': param['tocken'],
        'approvalId': '',
        'checkType': '',
        'device': 'pc',
        'pageId': 'L37844353',
        'groupCode': 'cjcamp',
        'selectStartDate': param['selectStartDate'],
        'selectEndDate': param['selectEndDate'],
        'selectCategoryId': '',
        'selectMonth': param['selectMonth'],
        'selectItemId': '',
        'selectPageItemType': '',
        'selectBusSeatId': '',
        'cnt': '',
        'infoType': '',
        'token': ''
    }

    response = requests.get(url=url, data=dict_data, cookies=cookies, verify=False,
                            headers={
                                'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'Accept-Encoding': 'gzip, deflate, br, zstd',
                                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                                'Connection': 'keep-alive',
                                'Connection-Length': '288',
                                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                'Host': 'camp.cjfmc.or.kr',
                                'Origin': 'https://camp.cjfmc.or.kr',
                                'Referer': 'https://camp.cjfmc.or.kr/cjcamp/campsite/L37844353',
                                'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                                'Sec-Ch-Ua-Mobile': '?0',
                                'Sec-Ch-Ua-Platform': '"Windows"',
                                'Sec-Fetch-Dest': 'empty',
                                'Sec-Fetch-Mode': 'cors',
                                'Sec-Fetch-Site': 'same-origin',
                                'User-Agent': param['UserAgent'],
                                'X-Requested-With': 'XMLHttpRequest'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}


def request_date(param, cookies):
    # 예약 파라미터 세팅
    url = "https://www.cjfmc.or.kr/camping/campsite/selectAjaxDatePinInfo.do"
    dict_data = {
        'tocken': param['tocken'],
        'approvalId': '',
        'checkType': '',
        'device': 'pc',
        'pageId': 'L37844353',
        'groupCode': 'cjcamp',
        'selectStartDate': param['selectStartDate'],
        'selectEndDate': param['selectEndDate'],
        'selectCategoryId': '',
        'selectMonth': param['selectMonth'],
        'selectItemId': '',
        'selectPageItemType': '',
        'selectBusSeatId': '',
        'cnt': '',
        'infoType': '',
        'token': ''
    }

    dict_data_cal = {
        'groupCode': 'cjcamp',
        'pageId': 'L37844353',
        'tocken': param['tocken'],
        'selectStartDate': param['selectStartDate'],
        'selectEndDate': param['selectEndDate'],
        'selectMonth': param['selectMonth'],
    }
    response = ''
    while response == '':
        try:

            response = requests.post(url=url, data=dict_data, cookies=cookies, verify=False,
                                     headers={
                                         'Accept': 'application/json, text/javascript, */*; q=0.01',
                                         'Accept-Encoding': 'gzip, deflate, br, zstd',
                                         'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                                         'Connection': 'keep-alive',
                                         'Content-Length': '288',
                                         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                         'Host': 'www.cjfmc.or.kr',
                                         'Origin': 'https://www.cjfmc.or.kr',
                                         'Referer': 'https://www.cjfmc.or.kr/camping/cjcamp/campsite/L37844353',
                                         'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                                         'Sec-Ch-Ua-Mobile': '?0',
                                         'Sec-Ch-Ua-Platform': '"Windows"',
                                         'Sec-Fetch-Dest': 'empty',
                                         'Sec-Fetch-Mode': 'cors',
                                         'Sec-Fetch-Site': 'same-origin',
                                         'User-Agent': param['UserAgent'],
                                         'X-Requested-With': 'XMLHttpRequest'})
            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                return {**dict_meta, **response.json()}
            else:  # 문자열 형태인 경우
                return {**dict_meta, **{'text': response.text}}
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def request_reservation(param, cookies):
    # 예약 파라미터 세팅
    url = "https://www.cjfmc.or.kr/camping/campsite/selectTicketInfo.do"
    dict_data = {
        'tocken': param['tocken'],
        'approvalId': '',
        'checkType': 'selectPin',
        'device': 'pc',
        'pageId': 'L37844353',
        'groupCode': 'cjcamp',
        'selectStartDate': param['selectStartDate'],
        'selectEndDate': param['selectEndDate'],
        'selectCategoryId': '',
        'selectMonth': param['selectMonth'],
        'selectItemId': param['selectItemId'],
        'selectPageItemType': '',
        'selectBusSeatId': '',
        'cnt': '',
        'infoType': '',
        'token': ''
    }

    response = requests.post(url=url, data=dict_data, cookies=cookies, verify=False,
                             headers={
                                 'Accept': '*/*',
                                 'Accept-Encoding': 'gzip, deflate, br, zstd',
                                 'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                                 'Connection': 'keep-alive',
                                 'Content-Length': '317',
                                 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                 'Host': 'www.cjfmc.or.kr',
                                 'Origin': 'https://www.cjfmc.or.kr',
                                 'Referer': 'https://www.cjfmc.or.kr/camping/cjcamp/campsite/L37844353',
                                 'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                                 'Sec-Ch-Ua-Mobile': '?0',
                                 'Sec-Ch-Ua-Platform': '"Windows"',
                                 'Sec-Fetch-Dest': 'empty',
                                 'Sec-Fetch-Mode': 'cors',
                                 'Sec-Fetch-Site': 'same-origin',
                                 'User-Agent': param['UserAgent'],
                                 'X-Requested-With': 'XMLHttpRequest'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
    if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
        return {**dict_meta, **response.json()}
    else:  # 문자열 형태인 경우
        return {**dict_meta, **{'text': response.text}}


i = 0
for i in range(RESERVATION_CNT):
    # 사이트 선택
    site_f = SITE_FROM[i][0:1]
    site_t = SITE_TO[i][0:1]
    site_f_n = int(SITE_FROM[i][1:len(SITE_FROM[i])])
    site_t_n = int(SITE_TO[i][1:len(SITE_TO[i])])
    start_d = START_DATE[i]
    end_d = END_DATE[i]

    nametag = i + 1
    name = "MACHINE{}".format(nametag)
    _data['name'] = name
    _data['nametag' + name] = nametag
    _data['SITE_F_TYPE' + name] = site_f
    _data['SITE_T_TYPE' + name] = site_t
    _data['SITE_F_NUM' + name] = site_f_n
    _data['SITE_T_NUM' + name] = site_t_n
    _data['START_DATE' + name] = start_d
    _data['END_DATE' + name] = end_d
    t = Worker(_data)  # sub thread 생성
    t.start()
    time.sleep(3)
