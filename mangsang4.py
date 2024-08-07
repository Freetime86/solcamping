from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from datetime import datetime
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
room_want = ['112', '115', '119', '101', '110', '106', '102', '103', '109', '111', '116', '120', '121', '122', '123']
#2인실 ['104' ,'105', '107', '108', '113', '114, '117', '118']
#4인실 ['102', '103', '109', '111', '116', '120', '121', '122', '123']
#6인실 ['112', '115', '119']
#8인실 ['101', '110']
#10인실 ['106']

sel_month_list = ['8']
sel_date_list = ['01', '02', '03', '09', '10', '15', '16', '17', '23', '24', '30', '31']
site = '1'

continue_work = False
trying = False
current_room = '0'
user_type = 2  # 사용자 정보 세팅

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
    rpwd = 'cca1174848'
    rid = 'jsy3033'
elif user_type == 1:
    user_name = '권혁인'
    rpwd = 'hi83188318'
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
    rpwd = 'cjswosla86'
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
if site == '1':
    site_text = '든바다'
elif site == '2':
    site_text = '난바다'
elif site == '3':
    site_text = '허허바다'
elif site == '4':
    site_text = '전통한옥'
elif site == '5':
    site_text = '캐라반'
elif site == '6':
    site_text = '자동차캠핑장'
elif site == '7':
    site_text = '글램핑'       #2인
elif site == '8':
    site_text = '글램핑'       #4인
elif site == '9':
    site_text = '캐빈하우스'
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
    thread_name = dataset['name']
    nametag = dataset['nametag']

    first_message = False
    enter_logic = True
    step = ''
    conn = ''
    area = ''
    checkin = ''

    driver = ''
    dowork = False
    driver1 = webdriver.Chrome(options=options)
    url1 = "https://www.campingkorea.or.kr/reservation/06.htm?code=&year=2024&month=" + sel_month_list[0] + "#container"
    driver1.get(url1)

    driver = webdriver.Chrome(options=options)
    url = "https://www.campingkorea.or.kr/member/login.htm"
    driver.get(url)
    # _cookies = driver.get_cookies()

    while True:
        try:
            if not first_message:
                print('WORKING... : ' + str(thread_name) + ' 예약 중')
                first_message = True

            WebDriverWait(driver1, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'calendar')))
            main_cals1 = driver1.find_element(By.CLASS_NAME, 'calendar')
            day_list1 = main_cals1.find_elements(By.CLASS_NAME, 'app-able')

            if len(day_list1) > 0:
                day_list_new = []
                for day in day_list1:
                    if site_text in day.text:
                        day_list_new.append(day)

                for day in day_list_new:
                    link_element = day.find_element(By.TAG_NAME, 'a')
                    day_text = link_element.get_attribute('title')[8:10]
                    if len(day_text) == 1:
                        day_text = '0' + day_text

                    if day_text in sel_date_list:
                        dowork = True
                        break
            if dowork:
                dowork = False
                if len(driver.find_elements(By.CLASS_NAME, 'btn_bg')) > 0:
                    driver.find_elements(By.CLASS_NAME, 'btn_bg')[0].find_element(By.TAG_NAME, 'a').click()
                    time.sleep(0.1)
                    driver.find_elements(By.CLASS_NAME, 'btn_bg')[0].find_element(By.TAG_NAME, 'a').click()
                driver.find_element(By.ID, 'userid').click()
                driver.find_element(By.ID, 'userid').send_keys(rid)
                driver.find_element(By.ID, 'passwd').click()
                driver.find_element(By.ID, 'passwd').send_keys(rpwd)
                driver.find_element(By.CLASS_NAME, 'btn_login').click()
                url = "https://www.campingkorea.or.kr/reservation/06.htm?code=&year=2024&month=" + sel_month_list[0] + "#container"
                driver.get(url)

                main_cals = driver.find_element(By.CLASS_NAME, 'calendar')
                day_list = main_cals.find_elements(By.CLASS_NAME, 'app-able')
                if len(day_list) > 0:
                    day_list_new = []
                    for day in day_list:
                        if site_text in day.text:
                            day_list_new.append(day)
                    for day in day_list_new:
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'a')))
                        link_element = day.find_element(By.TAG_NAME, 'a')
                        day_text = link_element.get_attribute('onclick')[48:50]
                        if len(day_text) == 1:
                            day_text = '0' + day_text
                        sel_date_list_temp = sel_date_list.copy()
                        if day_text in sel_date_list_temp:
                            link_element.click()
                            _cookies = driver.get_cookies()
                            cookie_dict = {}
                            for cookie in _cookies:
                                cookie_dict[cookie['name']] = cookie['value']

                            captcha_code = captcha(cookie_dict, thread_name)
                            driver.find_element(By.ID, 'auth_name').send_keys(captcha_code)
                            time.sleep(0.1)
                            buttons = driver.find_elements(By.CLASS_NAME, 'btn_blue')
                            if len(buttons) > 0:
                                buttons[0].click()
                                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'mapimg')))
                                all_sites = driver.find_element(By.ID, 'mapimg').find_elements(By.TAG_NAME, 'a')
                                if len(all_sites) > 0:
                                    for each_site in all_sites:
                                        href_text = each_site.get_attribute('href')
                                        #print(href_text)
                                        if 'area_act' in href_text or 'room_Code2' in href_text:
                                            site_num = each_site.text
                                            if len(site_num) == 1:
                                                site_num = '0' + site_num

                                            room_pass = False
                                            if site_num in room_want:
                                                room_pass = True
                                            elif len(room_want) == 0:
                                                room_pass = True

                                            if room_pass:
                                                each_site.click()
                                                summit_btn = driver.find_elements(By.CLASS_NAME, 'btn_color')
                                                if len(summit_btn) > 0:
                                                    time.sleep(0.1)
                                                    summit_btn[0].click()
                                                    #진행여부
                                                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                                                    driver.switch_to.alert.accept()
                                                    #다음단계진행 재차 확인
                                                    WebDriverWait(driver, 5).until(EC.alert_is_present())
                                                    driver.switch_to.alert.accept()
                                                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'res_Check')))
                                                    driver.find_element(By.ID, 'res_Check').click()
                                                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'animall_Check')))
                                                    driver.find_element(By.ID, 'animall_Check').click()
                                                    summit_btn = driver.find_elements(By.CLASS_NAME, 'btn_color')
                                                    if len(summit_btn) > 0:
                                                        time.sleep(0.1)
                                                        summit_btn[0].click()
                                                        WebDriverWait(driver, 5).until(EC.alert_is_present())
                                                        driver.switch_to.alert.accept()
                                                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'r_account3')))
                                                        driver.find_element(By.ID, 'r_account3').click()
                                                        WebDriverWait(driver, 5).until(EC.alert_is_present())
                                                        driver.switch_to.alert.accept()
                                                        summit_btn = driver.find_elements(By.CLASS_NAME, 'btn_color')
                                                        if len(summit_btn) > 0:
                                                            time.sleep(0.1)
                                                            summit_btn[0].click()
                                                            WebDriverWait(driver, 5).until(EC.alert_is_present())
                                                            driver.switch_to.alert.accept()
                                                            print(site_text + " " + site_num + " " + str(sel_month_list[0]) + "월 " + day_text + "일 예약완료")
                                                            sel_date_list_temp.remove(day_text)
                                                            driver.get(url)
                                    driver.refresh()
                                else:
                                    print('retry')
            driver1.refresh()
            time.sleep(delay)
        except Exception as ex:
            driver1.refresh()
            continue


def captcha(cookie, thread_name):
    #테서렉트 로드
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\psm07\AppData\Local\tesseract.exe'

    _pass = False
    captcha_code = ''
    while not _pass:
        # 이미지 로드
        url = "https://www.campingkorea.or.kr/bbs/bbs_gdlibrary.inc.php"
        response = requests.post(url=url, cookies=cookie, verify=False)

        if response.status_code == 200:
            filename = rid + "_captcha.png"
            with open(filename, 'wb') as f:
                f.write(response.content)
            image = Image.open(filename)
            image = cv2.imread(filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            captcha_code = pytesseract.image_to_string(gray, lang='eng', config='--psm 9 -c page_separator=""')
            #print(pytesseract.image_to_string(image, lang='eng', config='--psm 9 -c page_separator=""'))
            _pass = True
    return captcha_code



for i in range(machine):
    nametag = i + 1
    name = "MACHINE{}".format(nametag)
    dataset['name'] = name
    dataset['nametag'] = nametag
    t = Worker(dataset)  # sub thread 생성
    # t.daemon = True
    t.start()
    time.sleep(time_cut)
