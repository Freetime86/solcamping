from logging import exception
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
from selenium.common.exceptions import NoSuchElementException
import time

# 시스템 설정
py.FAILSAFE = False
global try_cnt

def main():
    try_cnt = 1
    while True:
        sel_month = '05'
        sel_date_list = ['30']
        sel_site_list = ['E']
        sel_num_list = []

        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 300)
        date_frame = datetime.now().strftime("%Y") + sel_month
        url = "https://camping.gtdc.or.kr/DZ_reservation/reserCamping_v3.php?xch=reservation&xid=camping_reservation&sdate=" + date_frame + "&step=Areas"
        driver.get(url)
        #driver.maximize_window()

        # 이용수칙 팝업 찾기
        check_box = driver.find_elements(By.NAME, 'today_dpnone')
        if len(check_box) > 0:
            check_box[0].click()
        pop_btn_list = driver.find_elements(By.CSS_SELECTOR, "button.btn-dark")
        if len(pop_btn_list) > 0:
            pop_btn_list[0].click()



        # 날짜 찾기
        is_enable = False
        while not is_enable:

            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.fs11pt")))
            date_frame = datetime.now().strftime("%Y") + "-" + sel_month + "-"

            for date in sel_date_list:
                for sel_site in sel_site_list:
                    button_value = "//button[@value='" + sel_site + ":" + date_frame + date + "']"

                    is_exception = False
                    try:
                        button = driver.find_element(By.XPATH, button_value)
                    except NoSuchElementException:
                        is_exception = True
                        print(date_frame + date + " : 가능한 " + sel_site + " 사이트가 없습니다.")

                    if not is_exception:
                        if button.is_enabled():
                            button.click()
                            is_enable = True
                            if is_enable:
                                print(date_frame + date + " 일자 : " + sel_site + ' ZONE 선택완료')
                                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.areacode")))
                                select_area(sel_num_list, wait, driver)
                                captcha(wait, driver)
                                # try_cnt = try_cnt + 1
                                # print('시도횟수 : ' + str(try_cnt))
                                # driver.close()
                                # main()
                                while True:
                                    playsound('done.mp3')
            driver.refresh()


def captcha(wait, driver):
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
        max_count = 3   # 정교함 밑에 쓰레드홀드랑 연관

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
    wait.until(EC.visibility_of_element_located((By.ID, "CAPTCHA_TEXT"))).send_keys(cpatcha_code)
    #time.sleep(3)
    #wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.bluish"))).click()
    #print(str(datetime.now().strftime("%X")) + ' color code : ' + cpatcha_code)

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
