from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui as py
import numpy as np
import cv2
import requests
import time
import json
import threading
import sys
import urllib3
from selenium.webdriver.support.ui import WebDriverWait

# 시스템 설정
py.FAILSAFE = False
options = Options()
options.add_experimental_option("detach", True)
#options.add_argument("headless") # 크롬창 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)





def main():

    dowork = False
    driver = webdriver.Chrome(options=options)
    url = "https://teams.microsoft.com/v2/?culture=ko-kr&country=kr"
    driver.get(url)
    wait = WebDriverWait(driver, 300)
    wait.until(EC.visibility_of_element_located((By.ID, "i0116"))).send_keys('DT076070@mobis-partners.com')
    driver.find_element(By.ID, 'idSIButton9').click()
    wait.until(EC.visibility_of_element_located((By.ID, "i0118"))).send_keys('CJSWOsla86!@1')
    driver.find_element(By.ID, 'idSIButton9').click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "table")))
    driver.find_elements(By.CLASS_NAME, 'table')[1].click()
    wait.until(EC.visibility_of_element_located((By.ID, "idSIButton9")))
    driver.find_element(By.ID, 'idSIButton9').click()
    wait.until(EC.visibility_of_element_located((By.ID, "hiddenformSubmitBtn")))
    driver.find_element(By.ID, 'hiddenformSubmitBtn').click()
    while True:
        try:
            time.sleep(250)
            driver.refresh()
        except Exception as ex:
            #dr.refresh()
            continue


main()