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
    driver = webdriver.Chrome(options=options)
    url = "https://teams.microsoft.com/v2/?culture=ko-kr&country=kr"
    driver.get(url)

    while True:
        try:
            if not first_message:
                print('WORKING... : ' + str(thread_name) + ' 예약 중')
                first_message = True

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'placeholderContainer')))
            driver.find_element(By.NAME, 'passwd').send_keys('CJSWOsla86!@12')
            driver.find_element(By.ID, 'idSIButton9').click()
            driver.find_element(By.CLASS_NAME 'table-row').click()

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

                driver.find_element(By.ID, 'passwd').click()
                driver.find_element(By.ID, 'passwd').send_keys(rpwd)

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
