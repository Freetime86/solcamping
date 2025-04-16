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
import pytesseract

# 시스템 설정
py.FAILSAFE = False
options = Options()
options.add_experimental_option("detach", True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)





def main():

    dowork = False
    driver = webdriver.Chrome(options=options)
    url = "https://teams.microsoft.com/v2/?culture=ko-kr&country=kr"
    driver.get(url)

    while True:
        try:
            time.sleep(250)
            driver.refresh()
        except Exception as ex:
            #dr.refresh()
            continue


main()