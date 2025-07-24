import time
import mangsang_setting as ms
import mangsang_data
import mangsang_processing
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import threading
import sys
import urllib3
import pytesseract

# 기초 데이터 PARSING
options = Options()
options.add_experimental_option("detach", True)
options.add_argument("headless")  # 크롬창 숨기기
DATASET = ms.dataset()


# 시스템 설정 최소 값 1
DATASET['BOT_NUMBER'] = 10

# 사용자 설정 USER_NO : 최종예약자, PING_PONG_1 = 첫번째 홀더, PING_PONG_2 두번째 홀더
DATASET['USER_NO'] = '09'
DATASET['PIN_PONG_1'] = '00'
DATASET['PIN_PONG_2'] = '01'

# 감시모드 설정
DATASET['MODE_LIVE'] = True  # 실시간 감시 여부 (취소표 잡을 때 사용)
DATASET['FINAL_RESERVE'] = True  # 최종 예약까지 진행 이렇게 하면 잘못예약되 취소할 경우 패널티2시간이 생긴다
DATASET['DELAY'] = 0  # 임시점유 상태의 갱신 주기 속도 새벽엔 느리게 권장
DATASET['SYSTEM_OFF'] = False  # 1건 예약 후 시스템 종료 유무

# 숙박 설정
DATASET['SELECT_DATE'] = ['2025-08-16']   # 지정일 기준 * 연박 ex) 2025-08-14 + 2박 => 2025-08-14 ~ 2025-08-16
DATASET['PERIOD'] = 1  # 연박 수
# 01:든바다, 02:난바다, 03:허허바다, 04:전통한옥, 05:캐라반, 06:자동차야영장, 07:글램핑A 08:글램핑B, 09:캐빈하우스
DATASET['ROOM_FACILITY'] = ['02']
# 인실정보 적용 2인실, 4인실, 6인실, 8인실, 10인실  없을 경우 PASS 자동차야영장 등등은 없음.
DATASET['ROOM_RANGE'] = ['8']
# 선호 방 번호 (선호 대상이 없을 경우 그 외 대상을 선택하도록 함)
DATASET['ROOM_WANTS'] = ['113']
# 제외 대상 설정
DATASET['ROOM_EXPT'] = []
DATASET['LOGIN_BROWSER'] = webdriver.Chrome(options=options)    #예약 당사자
DATASET['LOGIN_BROWSER1'] = webdriver.Chrome(options=options)   #핑퐁 1
DATASET['LOGIN_BROWSER2'] = webdriver.Chrome(options=options)   #핑퐁 2


class Worker(threading.Thread):
    def __init__(self, DATASET_NEW):
        super().__init__()
        self.name = DATASET['BOT_NAME']  # thread 이름 지정

    def run(self):
        threading.Thread(target=mangsang_processing.main(DATASET))


for i in range(DATASET['BOT_NUMBER']):
    nametag = i + 1
    name = "WORKER{}".format(nametag)
    DATASET['BOT_NAME'] = name
    t = Worker(DATASET)  # sub thread 생성
    t.start()
    time.sleep(DATASET['BOT_STARTING_DELAY'])