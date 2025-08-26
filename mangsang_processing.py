import mangsang_data as md
import mangsang_message as mm
import mangsang_utils as mu
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from user_agent import generate_user_agent
import pyautogui as py
import win32gui
import win32con
import requests
import time
import urllib3
import sys

# 시스템 설정
py.FAILSAFE = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(DATASET):
    if DATASET['THREAD_FLAG']:
        DATASET['THREAD_FLAG'] = False
        _bot_name = DATASET['BOT_NAME']
        # 시스템 기본 수행작업 필수
        DATASET = md.convert(DATASET)
        if not md.check(DATASET):
            exit()
        DATASET = login(DATASET)
        DATASET = mm.message(DATASET, _bot_name + ' START!')
        THREAD_FLAG = 'MAIN'
    else:
        DATASET = mm.message(DATASET, DATASET['BOT_NAME'] + ' START!')
        THREAD_FLAG = 'SUB'

    while True:
        if 'COOKIE' in DATASET:
            break

    if THREAD_FLAG == 'MAIN':
        mm.message(DATASET, '예약자 : ' + str(DATASET['CURRENT_USER']['user_name']) + ' / 유저 NO:' + str(
            DATASET['USER_NO']) + ' (' + str(DATASET['PERIOD']) + ')박')
        mm.message(DATASET,
                   '아이디 : ' + str(DATASET['CURRENT_USER']['rid']) + ' / 패스워드 : ' + str(DATASET['CURRENT_USER']['rpwd']))
        _wants = '지정안함'
        _range = '지정안함'
        if len(DATASET['ROOM_RANGE']) > 0:
            _range = str(DATASET['ROOM_RANGE']) + ' 인실'
        if len(DATASET['ROOM_WANTS']) > 0:
            _wants = str(DATASET['ROOM_WANTS'])
        for target in DATASET['TARGET_LIST']:
            DATASET = mm.message(DATASET,
                                 '입력정보 ' + str(target['site_name']) + ' => 탐색 범위 : ' + str(target['TARGET_NO']))
            if not len(target['TARGET_NO']) == len(target['TARGET_TYPE']):
                print('대상 번호와 코드가 일치하지 않습니다.')
                exit()
        DATASET['RANGE_TARGETS'] = _range
        DATASET['SCAN_TARGETS'] = _wants

    # 경과 시간 계산
    start_time = time.time()
    run_cnt = 0

    while True:
        try:
            # MAIN SUB 프로세스 분기
            if THREAD_FLAG == 'MAIN' and DATASET['MODE_LIVE']:
                DATASET['AVAILABLE_TARGET_LIST'] = []
                DATASET['AVAILABLE_NAME_LIST'] = []
                DATASET['CANCEL_TARGET_LIST'] = []
                DATASET['CANCEL_NAME_LIST'] = []
                DATASET['AVA_FROM_DATE_LIST'] = []
                DATASET['AVA_TO_DATE_LIST'] = []
                DATASET['CAN_FROM_DATE_LIST'] = []
                DATASET['CAN_TO_DATE_LIST'] = []

                DATASET['AVAILABLE_NAME_TXT'] = ''
                DATASET['CANCEL_NAME_TXT'] = ''
                for target_type_list in DATASET['TARGET_LIST']:
                    for begin_date in DATASET['SELECT_DATE']:
                        end_date = (datetime.strptime(begin_date, '%Y-%m-%d') + timedelta(
                            days=DATASET['PERIOD'])).strftime("%Y-%m-%d")
                        if not DATASET['TEMPORARY_HOLD']:
                            DATASET['LIST_TRRSRTCODE'] = target_type_list['trrsrtCode']
                            DATASET['LIST_FCLTYCODE'] = target_type_list['faciltyNo']
                            DATASET['LIST_RESVENOCODE'] = target_type_list['resveNoCode']
                            DATASET['LIST_TARGET_NO'] = target_type_list['TARGET_NO']
                            DATASET['LIST_TARGET_NAME'] = target_type_list['site_name']
                            DATASET['LIST_FROM_DATE'] = begin_date
                            DATASET['LIST_TO_DATE'] = end_date
                            DATASET = reservation_list(DATASET)
                if len(DATASET['AVAILABLE_TARGET_LIST']) > 0 or len(DATASET['CANCEL_TARGET_LIST']) > 0:
                    if len(DATASET['AVAILABLE_TARGET_LIST']) > 0 and len(DATASET['CANCEL_TARGET_LIST']) > 0:
                        DATASET = mm.message3(DATASET, '가능 대상 => ' + str(DATASET['AVAILABLE_NAME_TXT']),
                                              '취소중 대상 => ' + str(DATASET['CANCEL_NAME_TXT']))
                    elif len(DATASET['AVAILABLE_TARGET_LIST']) > 0:
                        DATASET = mm.message3(DATASET, '가능 대상 => ' + str(DATASET['AVAILABLE_NAME_TXT']), '')
                    elif len(DATASET['CANCEL_TARGET_LIST']) > 0:
                        DATASET = mm.message3(DATASET, '', '취소중 대상 => ' + str(DATASET['CANCEL_NAME_TXT']))

            elif THREAD_FLAG == 'SUB' or (not DATASET['MODE_LIVE'] and THREAD_FLAG == 'MAIN'):
                if DATASET['TEMPORARY_HOLD']:
                    while not DATASET['JUST_RESERVED']:
                        if 'preocpcEndDt' in DATASET['RESULT']:
                            if DATASET['RESULT']['preocpcEndDt'] is not None:
                                DATASET = mm.message5(DATASET, '점유 시간 ' + DATASET['RESULT']['preocpcBeginDt'] + ' ~ ' +
                                                      DATASET['RESULT']['preocpcEndDt'])
                                CURRENT_TIME_STR = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                CURRENT_TIME = datetime.strptime(CURRENT_TIME_STR, '%Y-%m-%d %H:%M:%S')
                                IN_RESERVED_TIME = datetime.strptime(DATASET['RESULT']['preocpcEndDt'],
                                                                     '%Y-%m-%d %H:%M:%S') - timedelta(seconds=999)
                                #if CURRENT_TIME >= IN_RESERVED_TIME or DATASET['STAND_BY_TIME'] is None:
                                if DATASET['STAND_BY_TIME'] is None:
                                    DATASET['RESERVE_TIME'] = datetime.strptime(DATASET['FINAL_RESVEBEGINDE'],
                                                                                '%Y-%m-%d')
                                    DATASET['LIVE_TIME'] = datetime.now() + timedelta(days=30)
                                    if DATASET['FINAL_RESERVE'] and (
                                            DATASET['LIVE_TIME'] >= DATASET['OPEN_TIME'] or DATASET[
                                        'RESERVE_TIME'] <
                                            DATASET['LIMIT_TIME']):
                                        if not DATASET['TRY_RESERVE']:
                                            #if '임시 점유 실패' not in str(DATASET['MESSAGE']):
                                            DATASET = mm.message(DATASET,
                                                                 ' 확정 예약 진행 중... ' + DATASET[
                                                                     'TARGET_MAX_CNT'] + ' ' + str(
                                                                     DATASET['FINAL_TYPE_NAME']) + ' => ' + str(
                                                                     DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                                                                     DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                                                     DATASET['FINAL_RESVEENDDE']))
                                            DATASET = final_reservation(DATASET)
                                            if DATASET['FINAL_RESULT']['status_code'] == 200:
                                                if 'message' in DATASET['FINAL_RESULT']:
                                                    RESULT_TXT = DATASET['FINAL_RESULT']['message']
                                                    if RESULT_TXT == '예약신청이 정상적으로 완료되었습니다.':
                                                        DATASET = mm.message(DATASET, '[' + str(
                                                            DATASET['FINAL_TYPE_NAME']) + '] ' + DATASET[
                                                                                 'TARGET_MAX_CNT'] + ' ' + str(
                                                            DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                                                            DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                                            DATASET[
                                                                'FINAL_RESVEENDDE']) + ' => ' + ' 예약이 완료되었습니다. ')
                                                        #if str(DATASET['FINAL_RESVEBEGINDE']) in DATASET['SELECT_DATE']:
                                                        #    DATASET['SELECT_DATE'].remove(str(DATASET['FINAL_RESVEBEGINDE']))
                                                        DATASET['TEMPORARY_HOLD'] = False
                                                        DATASET['JUST_RESERVED'] = True
                                                        if DATASET['SYSTEM_OFF']:
                                                            exit()
                                                        DATASET = mm.message(DATASET, ' 완료된 일짜를 제외하고 다시 예약을 시작합니다.')
                                                    else:
                                                        if '예약가능 시간은' in DATASET['FINAL_RESULT']['message']:
                                                            DATASET['STAND_BY_TIME'] = datetime.strptime(
                                                                DATASET['FINAL_RESULT']['message'][26:45],
                                                                '%Y-%m-%d %H:%M:%S') - timedelta(seconds=2)
                                                            DATASET = mm.message7(DATASET, DATASET['FINAL_RESULT'][
                                                                'message'] + ' 가능 시간까지 대기상태로 진입합니다.')
                                                        elif '일시적인 장애로' in DATASET['FINAL_RESULT'][
                                                            'message'] or '비정상적인 접근' in DATASET['FINAL_RESULT'][
                                                            'message'] or '예약이 불가능한' in DATASET['FINAL_RESULT'][
                                                            'message']:
                                                            DATASET = mm.message8(DATASET,
                                                                                  '(' + DATASET['FINAL_RESULT'][
                                                                                      'message'] + ') 다음과 같은 사유로 예약시도를 계속 합니다.')
                                                            DATASET = get_facility_relay(DATASET)
                                                        else:
                                                            DATASET['TEMPORARY_HOLD'] = False
                                                            mm.message(DATASET, DATASET['FINAL_RESULT']['message'])
                                                            break
                                                else:
                                                    DATASET = final_reservation(DATASET)
                                            else:
                                                DATASET = get_facility_relay(DATASET)
                                    else:
                                        if CURRENT_TIME >= IN_RESERVED_TIME:
                                            DATASET = get_facility_relay(DATASET)
                                else:
                                    if CURRENT_TIME >= IN_RESERVED_TIME:
                                        DATASET = get_facility_relay(DATASET)
                                #else:
                                #    if CURRENT_TIME >= DATASET['STAND_BY_TIME']:
                                #        DATASET['STAND_BY_TIME'] = None
                            else:
                                DATASET = get_facility_relay(DATASET)
                        else:
                            DATASET = get_facility_relay(DATASET)

                if not DATASET['TEMPORARY_HOLD']:
                    for target_type_list in DATASET['TARGET_LIST']:
                        idx = 0
                        for type_no in target_type_list['TARGET_NO']:
                            if target_type_list['TARGET_MAX_CNT'][idx] == '0':
                                copy_max_no = '전체이용'
                            else:
                                copy_max_no = target_type_list['TARGET_MAX_CNT'][idx] + '인실'
                            type_no_txt = type_no
                            if (type_no_txt in DATASET['ROOM_WANTS'] or DATASET['ROOM_WANTS'][
                                0] == 'ALL') and type_no_txt not in DATASET['ROOM_EXPT']:
                                for begin_date in DATASET['SELECT_DATE']:
                                    end_date = (datetime.strptime(begin_date, '%Y-%m-%d') + timedelta(
                                        days=DATASET['PERIOD'])).strftime("%Y-%m-%d")
                                    CURRENT_DICT = {}
                                    if not DATASET['TEMPORARY_HOLD']:

                                        CURRENT_DICT['FCLTYCODE'] = type_no
                                        CURRENT_DICT['FCLTYTYCODE'] = target_type_list['TARGET_TYPE'][idx]
                                        CURRENT_DICT['TARGET_MAX_CNT'] = copy_max_no
                                        CURRENT_DICT['FINAL_TYPE_NAME'] = target_type_list['site_name']
                                        CURRENT_DICT['RESVENOCODE'] = target_type_list['resveNoCode']
                                        CURRENT_DICT['TRRSRTCODE'] = target_type_list['trrsrtCode']
                                        CURRENT_DICT['FROM_DATE'] = begin_date
                                        CURRENT_DICT['TO_DATE'] = end_date

                                        if not DATASET['TEMPORARY_HOLD']:
                                            DATASET = get_facility(DATASET, CURRENT_DICT)
                                            if DATASET['TEMPORARY_HOLD']:
                                                DATASET = mm.message4(DATASET, '임시 점유 완료 ' + DATASET[
                                                    'TARGET_MAX_CNT'] + ' ' + str(
                                                    DATASET['RESVENOCODE']) + ' => ' + str(
                                                    DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                                                    DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                                    DATASET['FINAL_RESVEENDDE']))
                                                break
                                            else:
                                                elapsed_time = time.time() - start_time  # 경과된 시간 계산
                                                if elapsed_time >= 3600 * run_cnt:  # 3600초 == 1시간
                                                    DATASET = mm.message(DATASET, ' 탐색 지정 대상 ' + DATASET[
                                                        'RANGE_TARGETS'] + ' / ' + DATASET[
                                                                             'SCAN_TARGETS'] + ' 임시점유 예약을 시도 합니다.. ' + begin_date + ' ~ ' + end_date + ' / 경과 시간 : ' + str(
                                                        run_cnt) + '시간')
                                                    run_cnt = run_cnt + 1

                                                if DATASET['SHOW_WORKS']:
                                                    #print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' 대상 SCAN 중 ' + DATASET['TARGET_MAX_CNT'] + ' ' + str(target_type_list['site_name']) + ' => ' + str(DATASET['FCLTYTYCODE']) + ' / ' + str(DATASET['FROM_DATE']) + ' ~ ' + str(DATASET['TO_DATE']))
                                                    DATASET = mm.message2(DATASET,
                                                                          '대상 SCAN 중 ' + copy_max_no + ' ' + str(
                                                                              target_type_list[
                                                                                  'site_name']) + ' => ' + str(
                                                                              type_no_txt) + ' / ' + str(
                                                                              DATASET['FROM_DATE']) + ' ~ ' + str(
                                                                              DATASET['TO_DATE']))

                                if DATASET['TEMPORARY_HOLD']:
                                    break
                            idx = idx + 1
                        if DATASET['TEMPORARY_HOLD']:
                            break
        except Exception as ex:
            print(traceback.format_exc())
            mm.message(DATASET, ' EXCEPTION!! ====>  ' + str(ex))
            error(DATASET)
            continue


def reservation_list(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectChildFcltyList.do"
    dict_data = {
        'trrsrtCode': str(DATASET['LIST_TRRSRTCODE']),
        'fcltyCode': str(DATASET['LIST_FCLTYCODE']),
        'resveNoCode': str(DATASET['LIST_RESVENOCODE']),
        'resveBeginDe': str(DATASET['LIST_FROM_DATE']),
        'resveEndDe': str(DATASET['LIST_TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False)
            if not 'login' in response.text:
                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    if not DATASET['TEMPORARY_HOLD']:
                        DATASET['RESERVATION_LIST'] = {**dict_meta, **response.json()}
                        if DATASET['RESERVATION_LIST']['value'] is not None:
                            DATASET = reservation_filter(DATASET)
                        if DATASET['RESERVATION_LIST']['message']:
                            if '예약취소 후 2시간동안 동일한 시설은 예약을 할 수 없습니다.' in DATASET['RESERVATION_LIST']['message']:
                                new_msg = mu.replaceAll(str(DATASET['RESERVATION_LIST']['message']), '\n')
                                print('######################진행 불가 계정 : ' + new_msg)
                                exit()
                        return DATASET
                else:
                    if response.status_code == 500:
                        print('통신 에러 (2개 이상의 취소 패널티 등이 원인) 시스템 종료')
            else:  # 문자열 형태인 경우
                mm.message(DATASET, '로그인 TIMEOUT 발생, 재로그인 시도')
                DATASET = login(DATASET)
            return DATASET
        except requests.exceptions.RequestException as ex:
            continue


def reservation_filter(DATASET):
    DATASET['CURRENT_PROCESS'] = 'reservationList_filter'
    target_list = DATASET['RESERVATION_LIST']['value']['childFcltyList']
    AVAILABLE_NAME_LIST = []
    CANCEL_NAME_LIST = []
    for target in target_list:
        _target_no = str(target['fcltyCode'])
        if _target_no in DATASET['LIST_TARGET_NO']:
            _availableYn = str(target['resveAt'])
            _cancelYn = str(target['canclYn'])
            if _availableYn == 'Y':
                if _cancelYn == 'Y':
                    DATASET['AVAILABLE_TARGET_LIST'].append(target)
                    DATASET['AVA_FROM_DATE_LIST'].append(str(DATASET['LIST_FROM_DATE']))
                    DATASET['AVA_TO_DATE_LIST'].append(str(DATASET['LIST_TO_DATE']))
                    AVAILABLE_NAME_LIST.append(str(target['fcltyNm']))
                else:
                    DATASET['CANCEL_TARGET_LIST'].append(target)
                    DATASET['CAN_FROM_DATE_LIST'].append(str(DATASET['LIST_FROM_DATE']))
                    DATASET['CAN_TO_DATE_LIST'].append(str(DATASET['LIST_TO_DATE']))
                    CANCEL_NAME_LIST.append(str(target['fcltyNm']))
    if len(AVAILABLE_NAME_LIST) > 0:
        DATASET['AVAILABLE_NAME_TXT'] = DATASET['AVAILABLE_NAME_TXT'] + '\n' + str(
            DATASET['LIST_FROM_DATE']) + ' ~ ' + str(DATASET['LIST_TO_DATE']) + ' ' + str(
            DATASET['LIST_TARGET_NAME']) + ' => ' + str(AVAILABLE_NAME_LIST)
    if len(CANCEL_NAME_LIST) > 0:
        DATASET['CANCEL_NAME_TXT'] = DATASET['CANCEL_NAME_TXT'] + '\n' + str(DATASET['LIST_FROM_DATE']) + ' ~ ' + str(
            DATASET['LIST_TO_DATE']) + ' ' + str(DATASET['LIST_TARGET_NAME']) + ' => ' + str(AVAILABLE_NAME_LIST)
    return DATASET


def get_facility(DATASET, CURRENT_DICT):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(CURRENT_DICT['TRRSRTCODE']),
        'fcltyCode': str(CURRENT_DICT['FCLTYCODE']),
        'resveNoCode': str(CURRENT_DICT['RESVENOCODE']),
        'resveBeginDe': str(CURRENT_DICT['FROM_DATE']),
        'resveEndDe': str(CURRENT_DICT['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False)
            if 'Content-Type' in response.headers:
                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    DATASET['RELAY_RESULT'] = {**dict_meta, **response.json()}
                    if DATASET['RELAY_RESULT']['status_code'] == 200 and DATASET['RELAY_RESULT']['preocpcEndDt'] is not None:
                        DATASET['TEMPORARY_HOLD'] = True

                        DATASET['FCLTYCODE'] = CURRENT_DICT['FCLTYCODE']
                        DATASET['FCLTYTYCODE'] = CURRENT_DICT['FCLTYTYCODE']
                        DATASET['TARGET_MAX_CNT'] = CURRENT_DICT['TARGET_MAX_CNT']
                        DATASET['FINAL_TYPE_NAME'] = CURRENT_DICT['FINAL_TYPE_NAME']
                        DATASET['RESVENOCODE'] = CURRENT_DICT['RESVENOCODE']
                        DATASET['TRRSRTCODE'] = CURRENT_DICT['TRRSRTCODE']
                        DATASET['registerId'] = DATASET['CURRENT_USER']['rid']  # 로그인 아이디 초기값 하드코딩
                        DATASET['rsvctmNm'] = DATASET['CURRENT_USER']['user_name']  # 사용자 이름 초기값 하드코딩
                        DATASET['rsvctmEncptMbtlnum'] = DATASET['CURRENT_USER']['rphone']  # 전화번호
                        DATASET['encptEmgncCttpc'] = DATASET['CURRENT_USER']['rphone']  # 긴급전화번호
                        DATASET['FROM_DATE'] = CURRENT_DICT['FROM_DATE']
                        DATASET['TO_DATE'] = CURRENT_DICT['TO_DATE']

                        DATASET['RESULT'] = DATASET['RESULT'] = DATASET['RELAY_RESULT']
                        #필요 파라메터 맵핑
                        DATASET['FINAL_TRRSRTCODE'] = DATASET['RESULT']['trrsrtCode']
                        DATASET['FINAL_FCLTYCODE'] = DATASET['RESULT']['fcltyCode']
                        #한옥만 기존 faltycode를 사용한다. 매칭되지 않음. 망상만든 솔루션 쓰레기.
                        if DATASET['FINAL_TYPE_NAME'] == '전통한옥':
                            DATASET['FINAL_FCLTYCODE'] = CURRENT_DICT['FCLTYCODE']
                        DATASET['FINAL_FCLTYTYCODE'] = DATASET['RESULT']['fcltyTyCode']
                        DATASET['FINAL_PREOCPCFCLTYCODE'] = DATASET['RESULT'][
                            'fcltyCode']  #fcltyCode 랑 같은 데이터로 추정 DATASET['RESULT']['preocpcFcltyCode']
                        DATASET['FINAL_RESVENOCODE'] = DATASET['RESULT']['resveNoCode']
                        DATASET['FINAL_RESVEBEGINDE'] = DATASET['RESULT']['resveBeginDe']
                        DATASET['FINAL_RESVEENDDE'] = DATASET['RESULT']['resveEndDe']
                        DATASET['FINAL_RESVENO'] = DATASET['RESULT']['resveNo']
                        DATASET['FINAL_REGISTERID'] = DATASET['registerId']  #로그인 아이디 초기값 하드코딩
                        DATASET['FINAL_RSVCTMNM'] = DATASET['rsvctmNm']  #사용자 이름 초기값 하드코딩
                        DATASET['FINAL_RSVCTMENCPTMBTLNUM'] = DATASET['rsvctmEncptMbtlnum']  #전화번호
                        DATASET['FINAL_ENCPTEMGNCCTTPC'] = DATASET['encptEmgncCttpc']  #긴급전화번호
                        DATASET['FINAL_RSVCTMAREA'] = '1005'  #거주지역
                        DATASET['FINAL_ENTRCEDELAYCODE'] = '1004'  #입실시간 해당없음.
                        DATASET['FINAL_DSPSNFCLTYUSEAT'] = 'N'  #장애인시설 사용여부
                        DATASET['JUST_RESERVED'] = False
                        return DATASET
                else:  # 문자열 형태인 경우
                    DATASET['RESULT'] = {**dict_meta, **{'text': response.text}}
                    return DATASET
            else:
                print('error = > ' + str(response))
            return DATASET
        except requests.exceptions.RequestException as ex:
            continue


def get_facility_relay(DATASET):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(DATASET['TRRSRTCODE']),
        'fcltyCode': str(DATASET['FCLTYCODE']),
        'resveNoCode': str(DATASET['RESVENOCODE']),
        'resveBeginDe': str(DATASET['FROM_DATE']),
        'resveEndDe': str(DATASET['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False)
            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                DATASET['RELAY_RESULT'] = {**dict_meta, **response.json()}
                if DATASET['RELAY_RESULT']['status_code'] == 200 and DATASET['RELAY_RESULT']['preocpcEndDt'] is not None:
                    DATASET['TEMPORARY_HOLD'] = True

                    DATASET['RESULT'] = DATASET['RELAY_RESULT']
                    #필요 파라메터 맵핑
                    DATASET['FINAL_TRRSRTCODE'] = DATASET['RESULT']['trrsrtCode']
                    DATASET['FINAL_FCLTYCODE'] = DATASET['RESULT']['fcltyCode']
                    DATASET['FINAL_FCLTYTYCODE'] = DATASET['RESULT']['fcltyTyCode']
                    # 한옥만 기존 faltycode를 사용한다. 매칭되지 않음. 망상만든 솔루션 쓰레기.
                    if DATASET['FINAL_TYPE_NAME'] == '전통한옥':
                        DATASET['FINAL_FCLTYCODE'] = CURRENT_DICT['FCLTYCODE']
                    DATASET['FINAL_PREOCPCFCLTYCODE'] = DATASET['RESULT'][
                        'fcltyCode']  #fcltyCode 랑 같은 데이터로 추정 DATASET['RESULT']['preocpcFcltyCode']
                    DATASET['FINAL_RESVENOCODE'] = DATASET['RESULT']['resveNoCode']
                    DATASET['FINAL_RESVEBEGINDE'] = DATASET['RESULT']['resveBeginDe']
                    DATASET['FINAL_RESVEENDDE'] = DATASET['RESULT']['resveEndDe']
                    DATASET['FINAL_RESVENO'] = DATASET['RESULT']['resveNo']
                    DATASET['FINAL_REGISTERID'] = DATASET['registerId']  #로그인 아이디 초기값 하드코딩
                    DATASET['FINAL_RSVCTMNM'] = DATASET['rsvctmNm']  #사용자 이름 초기값 하드코딩
                    DATASET['FINAL_RSVCTMENCPTMBTLNUM'] = DATASET['rsvctmEncptMbtlnum']  #전화번호
                    DATASET['FINAL_ENCPTEMGNCCTTPC'] = DATASET['encptEmgncCttpc']  #긴급전화번호
                    DATASET['FINAL_RSVCTMAREA'] = '1005'  #거주지역
                    DATASET['FINAL_ENTRCEDELAYCODE'] = '1004'  #입실시간 해당없음.
                    DATASET['FINAL_DSPSNFCLTYUSEAT'] = 'N'  #장애인시설 사용여부
                    DATASET['JUST_RESERVED'] = False
                    DATASET['STAND_BY_TIME'] = None
                    DATASET = mm.message4(DATASET, '임시 점유 완료 ' + DATASET['TARGET_MAX_CNT'] + ' ' + str(
                        DATASET['RESVENOCODE']) + ' => ' + str(DATASET['FINAL_FCLTYCODE']) + ' / ' + str(
                        DATASET['FINAL_RESVEBEGINDE']) + ' ~ ' + str(DATASET['FINAL_RESVEENDDE']))
                else:
                    DATASET = mm.message4(DATASET, ' 임시 점유 실패 예약 시도를 계속 합니다.')
                #    CHECK_TIME_STR = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                #    CHECK_TIME = datetime.strptime(CHECK_TIME_STR, '%Y-%m-%d %H:%M:%S')
                #    LIMIT_TIME = datetime.strptime(DATASET['RESULT']['preocpcEndDt'], '%Y-%m-%d %H:%M:%S') + timedelta(seconds=10)
                #    if CHECK_TIME > LIMIT_TIME:
                #        DATASET = mm.message(DATASET, ' 임시 점유 실패 다시 탐색을 시작 합니다.')
                #        DATASET['TEMPORARY_HOLD'] = False
                return DATASET
            else:  # 문자열 형태인 경우
                DATASET['RESULT'] = {**dict_meta, **{'text': response.text}}
                return DATASET
            return DATASET
        except requests.exceptions.RequestException as ex:
            continue


def final_reservation(DATASET):
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertresve.do"
    dict_data = {
        'trrsrtCode': str(DATASET['FINAL_TRRSRTCODE']),
        'fcltyCode': str(DATASET['FINAL_FCLTYCODE']),
        'fcltyTyCode': str(DATASET['FINAL_FCLTYTYCODE']),
        'preocpcFcltyCode': str(DATASET['FINAL_PREOCPCFCLTYCODE']),
        'resveNoCode': '',
        'resveBeginDe': str(DATASET['FINAL_RESVEBEGINDE']),
        'resveEndDe': str(DATASET['FINAL_RESVEENDDE']),
        'resveNo': str(DATASET['FINAL_RESVENO']),
        'registerId': str(DATASET['FINAL_REGISTERID']),
        'rsvctmNm': str(DATASET['FINAL_RSVCTMNM']),
        'rsvctmEncptMbtlnum': str(DATASET['FINAL_RSVCTMENCPTMBTLNUM']),
        'encptEmgncCttpc': str(DATASET['FINAL_ENCPTEMGNCCTTPC']),
        'rsvctmArea': str(DATASET['FINAL_RSVCTMAREA']),
        'entrceDelayCode': str(DATASET['FINAL_ENTRCEDELAYCODE']),
        'dspsnFcltyUseAt': str(DATASET['FINAL_DSPSNFCLTYUSEAT'])
    }
    response = ''
    while response == '':
        try:
            if DATASET['TEMPORARY_HOLD']:
                response = requests.post(url=url, data=dict_data, cookies=DATASET['COOKIE'], verify=False, headers={
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Connection': 'keep-alive',
                    'Content-Length': '320',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Host': 'www.campingkorea.or.kr',
                    'Origin': 'https://www.campingkorea.or.kr',
                    'Referer': 'https://www.campingkorea.or.kr/user/reservation/BD_reservationInfo.do',
                    'Sec-Ch-Ua': '"Google Chrome";v="138", "Chromium";v="138", "Not-A.Brand";v="8"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'User-Agent': str(generate_user_agent(os='win', device_type='desktop')),
                    'X-Requested-With': 'XMLHttpRequest'})

                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    DATASET['FINAL_RESULT'] = {**dict_meta, **response.json()}
                    return DATASET
                else:  # 문자열 형태인 경우
                    DATASET['FINAL_RESULT'] = {**dict_meta, **{'text': response.text}}
                    return DATASET
            return DATASET
        except requests.exceptions.RequestException as ex:
            time.sleep(10)
            continue


def login(DATASET):
    DATASET['CURRENT_PROCESS'] = 'login'

    rid = DATASET['CURRENT_USER']['rid']
    rpwd = DATASET['CURRENT_USER']['rpwd']

    driver = DATASET['LOGIN_BROWSER']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)

    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(rid)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(rpwd)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "banner")))
    CHECK_LOAD = False
    _bannerList = []
    while not CHECK_LOAD:
        try:
            _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
            isDone = driver.find_elements(By.CLASS_NAME, 'jsBtnClose2')
            if len(isDone) == len(_bannerList):
                CHECK_LOAD = True
                for banner in _bannerList:
                    banner.find_element(By.TAG_NAME, 'button').click()
        except Exception:
            CHECK_LOAD = False
            continue

    DATASET['LOGIN_TIME'] = time.time()

    _cookies = DATASET['LOGIN_BROWSER'].get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
    DATASET['COOKIE'] = cookie_dict

    return DATASET


def pingpong1_login(DATASET):
    DATASET['CURRENT_PROCESS'] = 'login1'

    prid1 = DATASET['PINGPONG_USER1']['rid']
    prpwd1 = DATASET['PINGPONG_USER1']['rpwd']

    driver = DATASET['LOGIN_BROWSER1']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)

    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(prid1)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(prpwd1)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "banner")))
    CHECK_LOAD = False
    _bannerList = []
    while not CHECK_LOAD:
        try:
            _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
            isDone = driver.find_elements(By.CLASS_NAME, 'jsBtnClose2')
            if len(isDone) == len(_bannerList):
                CHECK_LOAD = True
                for banner in _bannerList:
                    banner.find_element(By.TAG_NAME, 'button').click()
        except Exception:
            CHECK_LOAD = False
            continue

    DATASET['LOGIN_TIME1'] = time.time()

    _cookies = DATASET['LOGIN_BROWSER1'].get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
    DATASET['COOKIE1'] = cookie_dict

    return DATASET


def pingpong2_login(DATASET):
    DATASET['CURRENT_PROCESS'] = 'login2'

    prid2 = DATASET['PINGPONG_USER2']['rid']
    prpwd2 = DATASET['PINGPONG_USER2']['rpwd']

    driver = DATASET['LOGIN_BROWSER2']
    url = "https://www.campingkorea.or.kr/login/BD_loginForm.do"
    driver.get(url)

    wait = WebDriverWait(driver, 1000)
    wait.until(EC.visibility_of_element_located((By.ID, "userId"))).send_keys(prid2)
    wait.until(EC.visibility_of_element_located((By.ID, "userPassword"))).send_keys(prpwd2)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mBtn2"))).click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "banner")))
    CHECK_LOAD = False
    _bannerList = []
    while not CHECK_LOAD:
        try:
            _bannerList = driver.find_elements(By.CLASS_NAME, "banner")
            isDone = driver.find_elements(By.CLASS_NAME, 'jsBtnClose2')
            if len(isDone) == len(_bannerList):
                CHECK_LOAD = True
                for banner in _bannerList:
                    banner.find_element(By.TAG_NAME, 'button').click()
        except Exception:
            CHECK_LOAD = False
            continue

    DATASET['LOGIN_TIME2'] = time.time()

    _cookies = DATASET['LOGIN_BROWSER2'].get_cookies()
    cookie_dict = {}
    for cookie in _cookies:
        cookie_dict[cookie['name']] = cookie['value']
    DATASET['COOKIE2'] = cookie_dict

    return DATASET


def error(DATASET):
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ERROR INFO ::: ' + str(DATASET))
