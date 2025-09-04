import time
import mangsang_setting as ms
import mangsang_processing
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import mangsang_multiprocessing as processor
import mangsang_data as md
import threading
import tempfile
import requests
import random
import os


# 기초 데이터 PARSING
options = Options()
user_data_dir = tempfile.mkdtemp()  # 고유한 임시 디렉토리
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_experimental_option("detach", True)
options.add_argument("headless")  # 크롬창 숨기기
DATASET = ms.dataset()


# 시스템 설정 최소 값 1
DATASET['BOT_NUMBER'] = 1

# 사용자 설정 USER_NO : 최종예약자, PING_PONG_1 = 첫번째 홀더, PING_PONG_2 두번째 홀더
DATASET['USER_NO'] = '03'
DATASET['PIN_PONG_1'] = '00'
DATASET['PIN_PONG_2'] = '01'

# 감시모드 설정
DATASET['MODE_LIVE'] = False  # 실시간 가능 리스트 적용 유무
DATASET['FINAL_RESERVE'] = False  # 최종 예약까지 진행 이렇게 하면 잘못예약되 취소할 경우 패널티2시간이 생긴다
DATASET['DELAY'] = 0  # 임시점유 상태의 갱신 주기 속도 새벽엔 느리게 권장
DATASET['SYSTEM_OFF'] = False  # 1건 예약 후 시스템 종료 유무
DATASET['MULTI'] = True  # 1건당 1개의 봇으로 세팅
DATASET['SHOW_WORKS'] = False  # 1건당 1개의 봇으로 세팅
DATASET['MULTIPLE_BOT'] = 10

# 숙박 설정
DATASET['SELECT_DATE'] = ['2025-10-03']    # 지정일 기준 * 연박 ex) 2025-08-14 + 2박 => 2025-08-14 ~ 2025-08-16
DATASET['PERIOD'] = ['3']  # 연박 수
# 01:든바다, 02:난바다, 03:허허바다, 04:전통한옥, 05:캐라반, 06:자동차야영장, 07:글램핑A 08:글램핑B, 09:캐빈하우스
DATASET['ROOM_FACILITY'] = ['01', '02', '03']
# 바다 숙소 : 인실정보 적용 2인실, 4인실, 6인실, 8인실, 10인실  없을 경우 PASS 자동차야영장 등등은 없음.
# 한옥 : 인실정보 적용 2인실, 4인실, 6인실
DATASET['ROOM_RANGE'] = ['8']
# 선호 방 번호 (선호 대상이 없을 경우 그 외 대상을 선택하도록 함)
DATASET['ROOM_WANTS'] = []
# 제외 대상 설정
DATASET['ROOM_EXPT'] = []

DATASET['LOGIN_BROWSER'] = webdriver.Chrome(options=options)    #예약 당사자
#DATASET['LOGIN_BROWSER1'] = webdriver.Chrome(options=options)   #핑퐁 1
#DATASET['LOGIN_BROWSER2'] = webdriver.Chrome(options=options)   #핑퐁 2


class Worker(threading.Thread):
    def __init__(self, DATASET_NEW):
        super().__init__()
        self.name = DATASET['BOT_NAME']  # thread 이름 지정

    def run(self):
        threading.Thread(target=mangsang_processing.main(DATASET))


def get_proxy():
    file_path = os.path.join(os.path.expanduser("~"), "Desktop", "proxy.txt")

    proxies = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            proxy_addr = line.strip()
            if proxy_addr:  # 빈 줄 무시
                proxy = f"http://{proxy_addr}"
                proxies.append({
                    "http": proxy,
                    "https": proxy
                })
    return proxies


def validate_proxies(proxies, test_url="https://www.google.com", timeout=0.05):
    print('VALIDATING PROXIES....')
    valid_proxies = []
    for proxy in proxies:
        try:
            response = requests.get(test_url, proxies=proxy, timeout=timeout)
            if response.status_code == 200:
                print('WORK! ' + str(proxy))
                valid_proxies.append(proxy)
        except:
            continue
    return valid_proxies


DATASET = md.convert(DATASET)
#PROXIES = validate_proxies(get_proxy())
PROXIES = get_proxy()

for target_type_list in DATASET['TARGET_LIST']:
    idx = 0
    for type_no in target_type_list['TARGET_NO']:
        _max_cnt = target_type_list['TARGET_MAX_CNT'][idx]
        if _max_cnt == '0':
            copy_max_no = '전체이용'
        else:
            copy_max_no = target_type_list['TARGET_MAX_CNT'][idx] + '인실'
        type_no_txt = type_no
        if (type_no_txt in DATASET['ROOM_WANTS'] or DATASET['ROOM_WANTS'][0] == 'ALL') and type_no_txt not in DATASET['ROOM_EXPT']:
            DATASET['SEARCH_RANGE'].append(type_no)
            DATASET['TARGET_MAX_CNT'] = target_type_list['TARGET_MAX_CNT'][idx]
            DATASET['TARGET_TYPE'] = target_type_list['TARGET_TYPE'][idx]
            DATASET['site_name'] = target_type_list['site_name']
            DATASET['resveNoCode'] = target_type_list['resveNoCode']
            DATASET['trrsrtCode'] = target_type_list['trrsrtCode']
            for cnt in range(DATASET['MULTIPLE_BOT']):
                name = "{}_WORKER".format(str(type_no) + '_' + str(cnt + 1))
                DATASET['BOT_ID'] = str(type_no)
                DATASET['BOT_NAME'] = name
                random_index = random.randint(0, len(PROXIES) - 1)
                TARGET_PROXY = PROXIES[random_index]
                DATASET["{}_WORKER_PROXY".format(str(type_no) + '_' + str(cnt + 1))] = TARGET_PROXY
                t = processor.Worker(DATASET)  # sub thread 생성
                t.start()
                time.sleep(DATASET['BOT_STARTING_DELAY'])
        idx = idx + 1
