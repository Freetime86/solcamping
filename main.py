from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui as py
import numpy as np
from PIL import Image
import cv2
from playsound import playsound
from datetime import datetime
from bs4 import BeautifulSoup
import time

# 시스템 설정
py.FAILSAFE = False


def main():
    sel_month = '6'
    sel_date_list = ['6', '7']
    sel_site_list = ['A', 'B']
    sel_num_list = []

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 300)
    url = "https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation"
    driver.get(url)
    driver.maximize_window()

    # 캘린더 위치 찾기
    calander_month = driver.find_element(By.ID, "Doc_Page_Title").text
    curr_month = calander_month[6:8]
    if sel_month > curr_month:
        btn_list = driver.find_elements(By.CSS_SELECTOR, "button.btn-trans")
        for button in btn_list:
            if button.text == '다음달':

                # 이용수칙 팝업 찾기
                pop_btn_list = []
                check_box = driver.find_elements(By.NAME, 'today_dpnone')
                if len(check_box) > 0:
                    check_box[0].click()
                pop_btn_list = driver.find_elements(By.CSS_SELECTOR, "button.btn-dark")
                if len(pop_btn_list) > 0:
                    pop_btn_list[0].click()
                button.click()

    # 날짜 찾기
    is_enable = False
    while not is_enable:
        # pop_btn_list = driver.find_elements(By.CSS_SELECTOR, "button.btn-dark")
        # if len(pop_btn_list) > 0:
        #    pop_btn_list[0].click()

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.fs11pt")))
        date_list = driver.find_elements(By.CSS_SELECTOR, "span.fs11pt")
        site_list = driver.find_elements(By.CSS_SELECTOR, "ul.mt5")

        index = 0

        for date in date_list:
            for sel_date in sel_date_list:
                if date.text == sel_date:
                    date_area = site_list[index]
                    site = date_area.find_elements(By.CSS_SELECTOR, "li")
                    for sel_site in sel_site_list:
                        if sel_site == "A" and site[0].find_element(By.CSS_SELECTOR, "button").is_enabled():
                            site[0].find_element(By.CSS_SELECTOR, "button").click()
                            is_enable = True
                        elif sel_site == "B" and site[1].find_element(By.CSS_SELECTOR, "button").is_enabled():
                            site[1].find_element(By.CSS_SELECTOR, "button").click()
                            is_enable = True
                        elif sel_site == "C" and site[2].find_element(By.CSS_SELECTOR, "button").is_enabled():
                            site[2].find_element(By.CSS_SELECTOR, "button").click()
                            is_enable = True
                        elif sel_site == "D" and site[3].find_element(By.CSS_SELECTOR, "button").is_enabled():
                            site[3].find_element(By.CSS_SELECTOR, "button").click()
                            is_enable = True
                        elif sel_site == "E" and site[4].find_element(By.CSS_SELECTOR, "button").is_enabled():
                            site[4].find_element(By.CSS_SELECTOR, "button").click()
                            is_enable = True

                        if is_enable:
                            print(sel_site + ' ZONE 선택완료')
                            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.areacode")))
                            select_area(sel_num_list, wait, driver)
                            captcha(wait, driver)

                            while True:
                                playsound('done.mp3')

            index = index + 1
        #print('page refresh')
        driver.refresh()


def captcha(wait, driver):
    print(str(datetime.now().strftime("%X")) + ' captcha start')
    wait.until(EC.visibility_of_element_located((By.ID, "CAPTCHA_CODE")))
    driver.find_element(By.ID, 'CAPTCHA_CODE').screenshot('captcha.png')
    # 이미지 로드
    image = Image.open('captcha.png')
    image.save('captcha.png')

    # target_image = cv2.imread('captcha.png', cv2.IMREAD_GRAYSCALE)
    target_image = target_image = cv2.imread('captcha.png')
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
        max_count = 2   # 정교함 밑에 쓰레드홀드랑 연관

        last_template = ''
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
            threshold = 0.71    # 절때 건들이지 말것 정확도
            loc = np.where(result >= threshold)
            for pt in zip(*loc[::-1]):
                x = pt[0]
                if 0 < x < 31 and not check_flag1:
                    check_count1 = check_count1 + 1
                    if last_template != template_name:
                        check_count1 = 0
                    if check_count1 >= max_count:
                        print(template_name + ' : 첫번째' + str(x))
                        cpatcha_code = str(index) + cpatcha_code[1:5]
                        check_flag1 = True
                    last_template = template_name
                elif 31 < x < 61 and not check_flag2:
                    check_count2 = check_count2 + 1
                    if last_template != template_name:
                        check_count1 = 0
                    if check_count2 >= max_count:
                        print(template_name + ' : 두번째' + str(x))
                        cpatcha_code = cpatcha_code[0:1] + str(index) + cpatcha_code[2:5]
                        check_flag2 = True
                    last_template = template_name
                elif 61 < x < 91 and not check_flag3:
                    check_count3 = check_count3 + 1
                    if last_template != template_name:
                        check_count1 = 0
                    if check_count3 >= max_count:
                        print(template_name + ' : 세번째' + str(x))
                        cpatcha_code = cpatcha_code[0:2] + str(index) + cpatcha_code[3:5]
                        check_flag3 = True
                    last_template = template_name
                elif 91 < x < 121 and not check_flag4:
                    check_count4 = check_count4 + 1
                    if last_template != template_name:
                        check_count1 = 0
                    if check_count4 >= max_count:
                        print(template_name + ' : 네번째' + str(x))
                        cpatcha_code = cpatcha_code[0:3] + str(index) + cpatcha_code[4:5]
                        check_flag4 = True
                    last_template = template_name
                elif 121 < x < 151 and not check_flag5:
                    if last_template != template_name:
                        check_count1 = 0
                    check_count5 = check_count5 + 1
                    if check_count5 >= max_count:
                        print(template_name + ' : 다섯번째' + str(x))
                        cpatcha_code = cpatcha_code[0:4] + str(index) + cpatcha_code[5:5]
                        check_flag5 = True
                    last_template = template_name
            color_loop = color_loop + 1

        index = index + 1
    wait.until(EC.visibility_of_element_located((By.ID, "CAPTCHA_TEXT"))).send_keys(cpatcha_code)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.bluish"))).click()
    print(str(datetime.now().strftime("%X")) + ' color code : ' + cpatcha_code)

    pass


def select_area(sel_num_list, wait, driver):
    area_list = driver.find_elements(By.CSS_SELECTOR, "button.on")
    area_found = False
    for area in area_list:
        if len(sel_num_list) > 0:
            for sel_site_num in sel_num_list:
                if (area.find_element(By.CSS_SELECTOR, "span").text == sel_site_num) and not area_found:
                    print(str(datetime.now().strftime("%X")) + ' 사이트 선택 : ' + str(area.find_element(By.CSS_SELECTOR, "span").text))
                    area.click()
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "select.select30")))
                    selector = Select(driver.find_elements(By.CSS_SELECTOR, "select.select30")[0])
                    selector.select_by_index(4)
                    area_found = True

                    break
        else:
            if not area_found:
                print(str(datetime.now().strftime("%X")) + ' 사이트 선택 : ' + str(area.find_element(By.CSS_SELECTOR, "span").text))
                area.click()
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "select.select30")))
                selector = Select(driver.find_elements(By.CSS_SELECTOR, "select.select30")[0])
                selector.select_by_index(4)
                area_found = True

    if not area_found:
        exit(str(datetime.now().strftime("%X")) + ' THERE IS NO AREA ENABLE')


main()
