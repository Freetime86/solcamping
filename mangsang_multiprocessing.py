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
    BOT_DICT = DATASET.copy()
    _bot_name = DATASET['BOT_NAME']
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
            if BOT_DICT['TEMPORARY_HOLD']:
                while not BOT_DICT['JUST_RESERVED']:
                    if 'preocpcEndDt' in BOT_DICT['RESULT']:
                        if BOT_DICT['RESULT']['preocpcEndDt'] is not None:
                            BOT_DICT = mm.message5(BOT_DICT, '점유 시간 ' + BOT_DICT['RESULT']['preocpcBeginDt'] + ' ~ ' +
                                                  BOT_DICT['RESULT']['preocpcEndDt'])
                            CURRENT_TIME_STR = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            CURRENT_TIME = datetime.strptime(CURRENT_TIME_STR, '%Y-%m-%d %H:%M:%S')
                            IN_RESERVED_TIME = datetime.strptime(BOT_DICT['RESULT']['preocpcEndDt'],
                                                                 '%Y-%m-%d %H:%M:%S') - timedelta(seconds=15)
                            #if CURRENT_TIME >= IN_RESERVED_TIME or BOT_DICT['STAND_BY_TIME'] is None:
                            if BOT_DICT['STAND_BY_TIME'] is None:
                                BOT_DICT['RESERVE_TIME'] = datetime.strptime(BOT_DICT['FINAL_RESVEBEGINDE'],
                                                                            '%Y-%m-%d')
                                BOT_DICT['LIVE_TIME'] = datetime.now() + timedelta(days=30)
                                if BOT_DICT['FINAL_RESERVE'] and (
                                        BOT_DICT['LIVE_TIME'] >= BOT_DICT['OPEN_TIME'] or BOT_DICT[
                                    'RESERVE_TIME'] <
                                        BOT_DICT['LIMIT_TIME']):
                                    if not BOT_DICT['TRY_RESERVE']:
                                        #if '임시 점유 실패' not in str(BOT_DICT['MESSAGE']):
                                        BOT_DICT = mm.message(BOT_DICT,
                                                             ' 확정 예약 진행 중... ' + BOT_DICT[
                                                                 'TARGET_MAX_CNT'] + ' ' + str(
                                                                 BOT_DICT['FINAL_TYPE_NAME']) + ' => ' + str(
                                                                 BOT_DICT['FINAL_FCLTYCODE']) + ' / ' + str(
                                                                 BOT_DICT['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                                                 BOT_DICT['FINAL_RESVEENDDE']))
                                        BOT_DICT = final_reservation(BOT_DICT)
                                        if BOT_DICT['FINAL_RESULT']['status_code'] == 200:
                                            if 'message' in BOT_DICT['FINAL_RESULT']:
                                                RESULT_TXT = BOT_DICT['FINAL_RESULT']['message']
                                                if RESULT_TXT == '예약신청이 정상적으로 완료되었습니다.':
                                                    BOT_DICT = mm.message(BOT_DICT, '[' + str(
                                                        BOT_DICT['FINAL_TYPE_NAME']) + '] ' + BOT_DICT[
                                                                             'TARGET_MAX_CNT'] + ' ' + str(
                                                        BOT_DICT['FINAL_FCLTYCODE']) + ' / ' + str(
                                                        BOT_DICT['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                                        BOT_DICT[
                                                            'FINAL_RESVEENDDE']) + ' => ' + ' 예약이 완료되었습니다. ')
                                                    BOT_DICT['TEMPORARY_HOLD'] = False
                                                    BOT_DICT['JUST_RESERVED'] = True
                                                    if DATASET['SYSTEM_OFF']:
                                                        exit()
                                                else:
                                                    if '예약가능 시간은' in BOT_DICT['FINAL_RESULT']['message']:
                                                        BOT_DICT['STAND_BY_TIME'] = datetime.strptime(
                                                            BOT_DICT['FINAL_RESULT']['message'][26:45],
                                                            '%Y-%m-%d %H:%M:%S') - timedelta(seconds=2)
                                                        BOT_DICT = mm.message7(BOT_DICT, BOT_DICT['FINAL_RESULT'][
                                                            'message'] + ' 가능 시간까지 대기상태로 진입합니다.')
                                                    elif '일시적인 장애로' in BOT_DICT['FINAL_RESULT'][
                                                        'message'] or '비정상적인 접근' in BOT_DICT['FINAL_RESULT'][
                                                        'message'] or '예약이 불가능한' in BOT_DICT['FINAL_RESULT'][
                                                        'message']:
                                                        BOT_DICT = mm.message8(BOT_DICT,
                                                                              '(' + BOT_DICT['FINAL_RESULT'][
                                                                                  'message'] + ') 다음과 같은 사유로 예약시도를 계속 합니다.')
                                                        BOT_DICT = get_facility_relay(BOT_DICT)
                                                    else:
                                                        BOT_DICT['TEMPORARY_HOLD'] = False
                                                        mm.message(BOT_DICT, BOT_DICT['FINAL_RESULT']['message'])
                                                        break
                                            else:
                                                BOT_DICT = final_reservation(BOT_DICT)
                                        else:
                                            BOT_DICT = get_facility_relay(BOT_DICT)
                                else:
                                    if CURRENT_TIME >= IN_RESERVED_TIME:
                                        BOT_DICT = get_facility_relay(BOT_DICT)
                            else:
                                if CURRENT_TIME >= IN_RESERVED_TIME:
                                    BOT_DICT = get_facility_relay(BOT_DICT)
                            #else:
                            #    if CURRENT_TIME >= BOT_DICT['STAND_BY_TIME']:
                            #        BOT_DICT['STAND_BY_TIME'] = None
                        else:
                            BOT_DICT = get_facility_relay(BOT_DICT)
                    else:
                        BOT_DICT = get_facility_relay(BOT_DICT)
            else:
                if BOT_DICT['TARGET_MAX_CNT'] == '0':
                    copy_max_no = '전체이용'
                else:
                    copy_max_no = BOT_DICT['TARGET_MAX_CNT'] + '인실'
                type_no_txt = _bot_name.split('_')[0]

                for begin_date in BOT_DICT['SELECT_DATE']:
                    end_date = (datetime.strptime(begin_date, '%Y-%m-%d') + timedelta(days=BOT_DICT['PERIOD'])).strftime("%Y-%m-%d")
                    if not BOT_DICT['TEMPORARY_HOLD']:
                        BOT_DICT['FCLTYCODE'] = type_no_txt
                        BOT_DICT['FCLTYTYCODE'] = BOT_DICT['TARGET_TYPE']
                        BOT_DICT['TARGET_MAX_CNT'] = copy_max_no
                        BOT_DICT['FINAL_TYPE_NAME'] = BOT_DICT['site_name']
                        BOT_DICT['RESVENOCODE'] = BOT_DICT['resveNoCode']
                        BOT_DICT['TRRSRTCODE'] = BOT_DICT['trrsrtCode']
                        BOT_DICT['FROM_DATE'] = begin_date
                        BOT_DICT['TO_DATE'] = end_date

                        if not BOT_DICT['TEMPORARY_HOLD']:
                            BOT_DICT = get_facility(BOT_DICT)
                            if BOT_DICT['TEMPORARY_HOLD']:
                                BOT_DICT = mm.message4(BOT_DICT, '임시 점유 완료 ' + BOT_DICT[
                                    'TARGET_MAX_CNT'] + ' ' + str(
                                    BOT_DICT['RESVENOCODE']) + ' => ' + str(
                                    BOT_DICT['FINAL_FCLTYCODE']) + ' / ' + str(
                                    BOT_DICT['FINAL_RESVEBEGINDE']) + ' ~ ' + str(
                                    BOT_DICT['FINAL_RESVEENDDE']))
                                break
                            else:
                                elapsed_time = time.time() - start_time  # 경과된 시간 계산
                                if elapsed_time >= 3600 * run_cnt:  # 3600초 == 1시간
                                    BOT_DICT = mm.message(BOT_DICT, ' 탐색 지정 대상 ' + DATASET[
                                        'RANGE_TARGETS'] + ' / ' + DATASET[
                                                             'SCAN_TARGETS'] + ' 임시점유 예약을 시도 합니다.. ' + begin_date + ' ~ ' + end_date + ' / 경과 시간 : ' + str(
                                        run_cnt) + '시간')
                                    run_cnt = run_cnt + 1

                                if BOT_DICT['SHOW_WORKS']:
                                    #print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' 대상 SCAN 중 ' + BOT_DICT['TARGET_MAX_CNT'] + ' ' + str(target_type_list['site_name']) + ' => ' + str(BOT_DICT['FCLTYTYCODE']) + ' / ' + str(BOT_DICT['FROM_DATE']) + ' ~ ' + str(BOT_DICT['TO_DATE']))
                                    BOT_DICT = mm.message2(BOT_DICT, str(_bot_name) + ' 대상 SCAN 중 ' + copy_max_no + ' ' + BOT_DICT['site_name'] + ' => ' + str(
                                                              type_no_txt) + ' / ' + str(
                                                              begin_date) + ' ~ ' + str(
                                                              end_date))
                    if BOT_DICT['TEMPORARY_HOLD']:
                        break
                if BOT_DICT['TEMPORARY_HOLD']:
                    break
        except Exception as ex:
            print(traceback.format_exc())
            mm.message(BOT_DICT, ' EXCEPTION!! ====>  ' + str(ex))
            error(BOT_DICT)
            continue


def reservation_list(BOT_DICT):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_selectChildFcltyList.do"
    dict_data = {
        'trrsrtCode': str(BOT_DICT['LIST_TRRSRTCODE']),
        'fcltyCode': str(BOT_DICT['LIST_FCLTYCODE']),
        'resveNoCode': str(BOT_DICT['LIST_RESVENOCODE']),
        'resveBeginDe': str(BOT_DICT['LIST_FROM_DATE']),
        'resveEndDe': str(BOT_DICT['LIST_TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=BOT_DICT['COOKIE'], verify=False)
            if not 'login' in response.text:
                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    if not BOT_DICT['TEMPORARY_HOLD']:
                        BOT_DICT['RESERVATION_LIST'] = {**dict_meta, **response.json()}
                        if BOT_DICT['RESERVATION_LIST']['value'] is not None:
                            BOT_DICT = reservation_filter(BOT_DICT)
                        if BOT_DICT['RESERVATION_LIST']['message']:
                            if '예약취소 후 2시간동안 동일한 시설은 예약을 할 수 없습니다.' in BOT_DICT['RESERVATION_LIST']['message']:
                                new_msg = mu.replaceAll(str(BOT_DICT['RESERVATION_LIST']['message']), '\n')
                                print('######################진행 불가 계정 : ' + new_msg)
                                exit()
                        return BOT_DICT
                else:
                    if response.status_code == 500:
                        print('통신 에러 (2개 이상의 취소 패널티 등이 원인) 시스템 종료')
            else:  # 문자열 형태인 경우
                mm.message(BOT_DICT, '로그인 TIMEOUT 발생, 재로그인 시도')
                BOT_DICT = login(BOT_DICT)
            return BOT_DICT
        except requests.exceptions.RequestException as ex:
            continue


def reservation_filter(BOT_DICT):
    BOT_DICT['CURRENT_PROCESS'] = 'reservationList_filter'
    target_list = BOT_DICT['RESERVATION_LIST']['value']['childFcltyList']
    AVAILABLE_NAME_LIST = []
    CANCEL_NAME_LIST = []
    for target in target_list:
        _target_no = str(target['fcltyCode'])
        if _target_no in BOT_DICT['LIST_TARGET_NO']:
            _availableYn = str(target['resveAt'])
            _cancelYn = str(target['canclYn'])
            if _availableYn == 'Y':
                if _cancelYn == 'Y':
                    BOT_DICT['AVAILABLE_TARGET_LIST'].append(target)
                    BOT_DICT['AVA_FROM_DATE_LIST'].append(str(BOT_DICT['LIST_FROM_DATE']))
                    BOT_DICT['AVA_TO_DATE_LIST'].append(str(BOT_DICT['LIST_TO_DATE']))
                    AVAILABLE_NAME_LIST.append(str(target['fcltyNm']))
                else:
                    BOT_DICT['CANCEL_TARGET_LIST'].append(target)
                    BOT_DICT['CAN_FROM_DATE_LIST'].append(str(BOT_DICT['LIST_FROM_DATE']))
                    BOT_DICT['CAN_TO_DATE_LIST'].append(str(BOT_DICT['LIST_TO_DATE']))
                    CANCEL_NAME_LIST.append(str(target['fcltyNm']))
    if len(AVAILABLE_NAME_LIST) > 0:
        BOT_DICT['AVAILABLE_NAME_TXT'] = BOT_DICT['AVAILABLE_NAME_TXT'] + '\n' + str(
            BOT_DICT['LIST_FROM_DATE']) + ' ~ ' + str(BOT_DICT['LIST_TO_DATE']) + ' ' + str(
            BOT_DICT['LIST_TARGET_NAME']) + ' => ' + str(AVAILABLE_NAME_LIST)
    if len(CANCEL_NAME_LIST) > 0:
        BOT_DICT['CANCEL_NAME_TXT'] = BOT_DICT['CANCEL_NAME_TXT'] + '\n' + str(BOT_DICT['LIST_FROM_DATE']) + ' ~ ' + str(
            BOT_DICT['LIST_TO_DATE']) + ' ' + str(BOT_DICT['LIST_TARGET_NAME']) + ' => ' + str(AVAILABLE_NAME_LIST)
    return BOT_DICT


def get_facility(BOT_DICT):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(BOT_DICT['TRRSRTCODE']),
        'fcltyCode': str(BOT_DICT['FCLTYCODE']),
        'resveNoCode': str(BOT_DICT['RESVENOCODE']),
        'resveBeginDe': str(BOT_DICT['FROM_DATE']),
        'resveEndDe': str(BOT_DICT['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=BOT_DICT['COOKIE'], verify=False)
            if 'Content-Type' in response.headers:
                dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                             'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
                if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                    BOT_DICT['RELAY_RESULT'] = {**dict_meta, **response.json()}
                    if BOT_DICT['RELAY_RESULT']['status_code'] == 200 and BOT_DICT['RELAY_RESULT']['preocpcEndDt'] is not None:
                        BOT_DICT['TEMPORARY_HOLD'] = True
                        BOT_DICT['registerId'] = BOT_DICT['CURRENT_USER']['rid']  # 로그인 아이디 초기값 하드코딩
                        BOT_DICT['rsvctmNm'] = BOT_DICT['CURRENT_USER']['user_name']  # 사용자 이름 초기값 하드코딩
                        BOT_DICT['rsvctmEncptMbtlnum'] = BOT_DICT['CURRENT_USER']['rphone']  # 전화번호
                        BOT_DICT['encptEmgncCttpc'] = BOT_DICT['CURRENT_USER']['rphone']  # 긴급전화번호
                        BOT_DICT['RESULT'] = BOT_DICT['RELAY_RESULT']
                        #필요 파라메터 맵핑
                        BOT_DICT['FINAL_TRRSRTCODE'] = BOT_DICT['RESULT']['trrsrtCode']
                        BOT_DICT['FINAL_FCLTYCODE'] = BOT_DICT['RESULT']['fcltyCode']
                        #한옥만 기존 faltycode를 사용한다. 매칭되지 않음. 망상만든 솔루션 쓰레기.
                        if BOT_DICT['FINAL_TYPE_NAME'] == '전통한옥':
                            BOT_DICT['FINAL_FCLTYCODE'] = BOT_DICT['FCLTYCODE']
                        BOT_DICT['FINAL_FCLTYTYCODE'] = BOT_DICT['RESULT']['fcltyTyCode']
                        BOT_DICT['FINAL_PREOCPCFCLTYCODE'] = BOT_DICT['RESULT'][
                            'fcltyCode']  #fcltyCode 랑 같은 데이터로 추정 BOT_DICT['RESULT']['preocpcFcltyCode']
                        BOT_DICT['FINAL_RESVENOCODE'] = BOT_DICT['RESULT']['resveNoCode']
                        BOT_DICT['FINAL_RESVEBEGINDE'] = BOT_DICT['RESULT']['resveBeginDe']
                        BOT_DICT['FINAL_RESVEENDDE'] = BOT_DICT['RESULT']['resveEndDe']
                        BOT_DICT['FINAL_RESVENO'] = BOT_DICT['RESULT']['resveNo']
                        BOT_DICT['FINAL_REGISTERID'] = BOT_DICT['registerId']  #로그인 아이디 초기값 하드코딩
                        BOT_DICT['FINAL_RSVCTMNM'] = BOT_DICT['rsvctmNm']  #사용자 이름 초기값 하드코딩
                        BOT_DICT['FINAL_RSVCTMENCPTMBTLNUM'] = BOT_DICT['rsvctmEncptMbtlnum']  #전화번호
                        BOT_DICT['FINAL_ENCPTEMGNCCTTPC'] = BOT_DICT['encptEmgncCttpc']  #긴급전화번호
                        BOT_DICT['FINAL_RSVCTMAREA'] = '1005'  #거주지역
                        BOT_DICT['FINAL_ENTRCEDELAYCODE'] = '1004'  #입실시간 해당없음.
                        BOT_DICT['FINAL_DSPSNFCLTYUSEAT'] = 'N'  #장애인시설 사용여부
                        BOT_DICT['JUST_RESERVED'] = False
                        return BOT_DICT
                else:  # 문자열 형태인 경우
                    BOT_DICT['RESULT'] = {**dict_meta, **{'text': response.text}}
                    return BOT_DICT
            else:
                print('error = > ' + str(response))
            return BOT_DICT
        except requests.exceptions.RequestException as ex:
            continue


def get_facility_relay(BOT_DICT):
    # 예약 파라미터 세팅
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertPreocpc.do"
    dict_data = {
        'trrsrtCode': str(BOT_DICT['TRRSRTCODE']),
        'fcltyCode': str(BOT_DICT['FCLTYCODE']),
        'resveNoCode': str(BOT_DICT['RESVENOCODE']),
        'resveBeginDe': str(BOT_DICT['FROM_DATE']),
        'resveEndDe': str(BOT_DICT['TO_DATE'])
    }
    response = ''
    while response == '':
        try:
            response = requests.post(url=url, data=dict_data, cookies=BOT_DICT['COOKIE'], verify=False)
            dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                         'Content-Type': response.headers['Content-Type'], 'cookies': response.cookies}
            if 'json' in str(response.headers['Content-Type']):  # JSON 형태인 경우
                BOT_DICT['RELAY_RESULT'] = {**dict_meta, **response.json()}
                if BOT_DICT['RELAY_RESULT']['status_code'] == 200 and BOT_DICT['RELAY_RESULT']['preocpcEndDt'] is not None:
                    BOT_DICT['TEMPORARY_HOLD'] = True

                    BOT_DICT['RESULT'] = BOT_DICT['RELAY_RESULT']
                    #필요 파라메터 맵핑
                    BOT_DICT['FINAL_TRRSRTCODE'] = BOT_DICT['RESULT']['trrsrtCode']
                    BOT_DICT['FINAL_FCLTYCODE'] = BOT_DICT['RESULT']['fcltyCode']
                    BOT_DICT['FINAL_FCLTYTYCODE'] = BOT_DICT['RESULT']['fcltyTyCode']
                    # 한옥만 기존 faltycode를 사용한다. 매칭되지 않음. 망상만든 솔루션 쓰레기.
                    if BOT_DICT['FINAL_TYPE_NAME'] == '전통한옥':
                        BOT_DICT['FINAL_FCLTYCODE'] = CURRENT_DICT['FCLTYCODE']
                    BOT_DICT['FINAL_PREOCPCFCLTYCODE'] = BOT_DICT['RESULT'][
                        'fcltyCode']  #fcltyCode 랑 같은 데이터로 추정 BOT_DICT['RESULT']['preocpcFcltyCode']
                    BOT_DICT['FINAL_RESVENOCODE'] = BOT_DICT['RESULT']['resveNoCode']
                    BOT_DICT['FINAL_RESVEBEGINDE'] = BOT_DICT['RESULT']['resveBeginDe']
                    BOT_DICT['FINAL_RESVEENDDE'] = BOT_DICT['RESULT']['resveEndDe']
                    BOT_DICT['FINAL_RESVENO'] = BOT_DICT['RESULT']['resveNo']
                    BOT_DICT['FINAL_REGISTERID'] = BOT_DICT['registerId']  #로그인 아이디 초기값 하드코딩
                    BOT_DICT['FINAL_RSVCTMNM'] = BOT_DICT['rsvctmNm']  #사용자 이름 초기값 하드코딩
                    BOT_DICT['FINAL_RSVCTMENCPTMBTLNUM'] = BOT_DICT['rsvctmEncptMbtlnum']  #전화번호
                    BOT_DICT['FINAL_ENCPTEMGNCCTTPC'] = BOT_DICT['encptEmgncCttpc']  #긴급전화번호
                    BOT_DICT['FINAL_RSVCTMAREA'] = '1005'  #거주지역
                    BOT_DICT['FINAL_ENTRCEDELAYCODE'] = '1004'  #입실시간 해당없음.
                    BOT_DICT['FINAL_DSPSNFCLTYUSEAT'] = 'N'  #장애인시설 사용여부
                    BOT_DICT['JUST_RESERVED'] = False
                    BOT_DICT['STAND_BY_TIME'] = None
                    BOT_DICT = mm.message4(BOT_DICT, '임시 점유 완료 ' + BOT_DICT['TARGET_MAX_CNT'] + ' ' + str(
                        BOT_DICT['RESVENOCODE']) + ' => ' + str(BOT_DICT['FINAL_FCLTYCODE']) + ' / ' + str(
                        BOT_DICT['FINAL_RESVEBEGINDE']) + ' ~ ' + str(BOT_DICT['FINAL_RESVEENDDE']))
                else:
                    BOT_DICT = mm.message4(BOT_DICT, ' 임시 점유 실패 예약 시도를 계속 합니다.')
                #    CHECK_TIME_STR = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                #    CHECK_TIME = datetime.strptime(CHECK_TIME_STR, '%Y-%m-%d %H:%M:%S')
                #    LIMIT_TIME = datetime.strptime(BOT_DICT['RESULT']['preocpcEndDt'], '%Y-%m-%d %H:%M:%S') + timedelta(seconds=10)
                #    if CHECK_TIME > LIMIT_TIME:
                #        BOT_DICT = mm.message(BOT_DICT, ' 임시 점유 실패 다시 탐색을 시작 합니다.')
                #        BOT_DICT['TEMPORARY_HOLD'] = False
                return BOT_DICT
            else:  # 문자열 형태인 경우
                BOT_DICT['RESULT'] = {**dict_meta, **{'text': response.text}}
                return BOT_DICT
            return BOT_DICT
        except requests.exceptions.RequestException as ex:
            continue


def final_reservation(BOT_DICT):
    url = "https://www.campingkorea.or.kr/user/reservation/ND_insertresve.do"
    dict_data = {
        'trrsrtCode': str(BOT_DICT['FINAL_TRRSRTCODE']),
        'fcltyCode': str(BOT_DICT['FINAL_FCLTYCODE']),
        'fcltyTyCode': str(BOT_DICT['FINAL_FCLTYTYCODE']),
        'preocpcFcltyCode': str(BOT_DICT['FINAL_PREOCPCFCLTYCODE']),
        'resveNoCode': '',
        'resveBeginDe': str(BOT_DICT['FINAL_RESVEBEGINDE']),
        'resveEndDe': str(BOT_DICT['FINAL_RESVEENDDE']),
        'resveNo': str(BOT_DICT['FINAL_RESVENO']),
        'registerId': str(BOT_DICT['FINAL_REGISTERID']),
        'rsvctmNm': str(BOT_DICT['FINAL_RSVCTMNM']),
        'rsvctmEncptMbtlnum': str(BOT_DICT['FINAL_RSVCTMENCPTMBTLNUM']),
        'encptEmgncCttpc': str(BOT_DICT['FINAL_ENCPTEMGNCCTTPC']),
        'rsvctmArea': str(BOT_DICT['FINAL_RSVCTMAREA']),
        'entrceDelayCode': str(BOT_DICT['FINAL_ENTRCEDELAYCODE']),
        'dspsnFcltyUseAt': str(BOT_DICT['FINAL_DSPSNFCLTYUSEAT'])
    }
    response = ''
    while response == '':
        try:
            if BOT_DICT['TEMPORARY_HOLD']:
                response = requests.post(url=url, data=dict_data, cookies=BOT_DICT['COOKIE'], verify=False, headers={
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
                    BOT_DICT['FINAL_RESULT'] = {**dict_meta, **response.json()}
                    return BOT_DICT
                else:  # 문자열 형태인 경우
                    BOT_DICT['FINAL_RESULT'] = {**dict_meta, **{'text': response.text}}
                    return BOT_DICT
            return BOT_DICT
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


def error(BOT_DICT):
    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ERROR INFO ::: ' + str(BOT_DICT))
