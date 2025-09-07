from datetime import datetime, timedelta
import random


def check(DATASET):

    if DATASET['BOT_NUMBER'] < 1:
        print('현재 작업자 수(' + str(DATASET['BOT_NUMBER']) + ') 작업자 배정 수를 확인하세요.')
        return False

    #if int(DATASET['PERIOD']) == 0 or int(DATASET['PERIOD']) > 3:
    #    print('연박 수 지정이 잘못되었습니다. 최소/최대 1~3박 까지만 지정 가능합니다.')
    #    return False

    for _date in DATASET['SELECT_DATE']:
        try:
            datetime.strptime(_date, "%Y-%m-%d")
        except ValueError:
            print('(' + str(_date) + ')' + ' 날짜 형식이 잘못되었습니다. 올바른 방식은 yyyy-mm-dd 입니다.')
            return False
        #_to_date = int((datetime.strptime(_date, '%Y-%m-%d') + timedelta(days=DATASET['PERIOD']-1)).strftime("%Y%m%d"))
        #_t_date = int(_date.replace('-', '', 2))
#
        #error_date = []
        #for _str_date in DATASET['SELECT_DATE']:
        #    int_date = int(_str_date.replace('-', '', 2))
        #    if _t_date != int_date and _t_date < int_date <= _to_date:
        #        error_date.append(_str_date)
        #if len(error_date) > 0:
        #    print('(' + str(_date) + ')' + ' 현재 날짜의 연박 수 [' + str(DATASET['PERIOD']) + '] (' + str(error_date).replace("'", '',999).replace('[', '').replace(']', '') + ') 가 지정 날짜에 포함되어 있습니다.')
        #    return False

    if len(DATASET['ROOM_FACILITY']) < 1:
        print('시설 타입 정보가 없습니다.')
    else:
        for _facility in DATASET['ROOM_FACILITY']:
            if not _facility.isdigit() and len(_facility) != 2:
                print('(' + str(_facility) + ')' + ' 시설 타입 정보가 잘못되었습니다.')
                return False
            if _facility in ['01', '02', '03'] and len(DATASET['ROOM_RANGE']) == 0:
                print('든바다, 난바다, 허허바다의 경우 인실을 지정해야 합니다.')
                return False
                
    for _range in DATASET['ROOM_RANGE']:
        if not _range.isdigit():
            print('(' + str(_range) + ') 인실 정보가 잘못되었습니다. 숫자만 입력 가능 합니다.')
            return False

    #for _expt in DATASET['ROOM_EXPT']:
    #    if not int(_expt).isdigit():
    #        print('(' + str(_expt) + ') 제외 대상 정보가 잘못되었습니다. 숫자만 입력 가능 합니다.')
    #        return False
    return True


def convert(DATASET):
    # 변경 데이터 KEY
    USER_NO = DATASET['USER_NO']  # 최종 유저
    PINGPONG_NO_1 = DATASET['PIN_PONG_1']  # 최종 유저
    PINGPONG_NO_2 = DATASET['PIN_PONG_2']  # 최종 유저
    FACILITY_LIST = DATASET['ROOM_FACILITY']  # 시설 리스트

    DATASET['CURRENT_USER'] = DATASET['USER_INFO'][USER_NO]
    DATASET['PINGPONG_USER1'] = DATASET['USER_INFO'][PINGPONG_NO_1]
    DATASET['PINGPONG_USER2'] = DATASET['USER_INFO'][PINGPONG_NO_2]

    if len(DATASET['ROOM_WANTS']) == 0:
        DATASET['ROOM_WANTS'].append('ALL')

    for index in FACILITY_LIST:
        _target = DATASET['FACILITY_INFO'][index]
        _target_max_list = []
        _target_no_list = []
        _target_ty_list = []

        if index == '04':
            new_room_List = []
            for wants in DATASET['ROOM_WANTS']:
                if len(wants) < 4:
                    if str(wants) != 'ALL':
                        new_room_List.append(str(int(wants) + 1100))
                    else:
                        new_room_List.append(str(wants))
            DATASET['ROOM_WANTS'] = new_room_List

        elif index == '06':
            new_room_List = []
            for wants in DATASET['ROOM_WANTS']:
                if len(wants) < 4:
                    if str(wants) != 'ALL':
                        new_room_List.append(str(int(wants) + 1600))
                    else:
                        new_room_List.append(str(wants))
            DATASET['ROOM_WANTS'] = new_room_List
        # 든바다난바다허허바다전용
        elif index == '01' or index == '02' or index == '03':
            for _number in DATASET['ROOM_RANGE']:
                _range_list = get_facility_no(_target, _number)
                for _row in _range_list:
                    _fcltyInfo = _row.split('|')
                    new_text = ''
                    for idx in range(len(_fcltyInfo[1])):
                        if _fcltyInfo[1][idx].isdigit():
                           new_text = new_text + _fcltyInfo[1][idx]
                    if new_text in DATASET['ROOM_WANTS']:
                        DATASET['ROOM_WANTS'].remove(new_text)
                        DATASET['ROOM_WANTS'].append(_fcltyInfo[1])
                    if new_text in DATASET['ROOM_EXPT']:
                        DATASET['ROOM_EXPT'].remove(new_text)
                        DATASET['ROOM_EXPT'].append(_fcltyInfo[1])
                    _target_max_list.append(_fcltyInfo[0])
                    _target_no_list.append(_fcltyInfo[1])
                    _target_ty_list.append(_fcltyInfo[2])
                if len(_target_max_list) == 0 and index != '02' and index != '03':
                    _target_max_list.append('ALL')
                else:
                    _target['TARGET_MAX_CNT'] = _target_max_list
                _target['TARGET_NO'] = _target_no_list
                _target['TARGET_TYPE'] = _target_ty_list
        if index == '04' or index == '05' or index == '06':
            _range_list = get_facility_no(_target, 0)
            for _row in _range_list:
                _fcltyInfo = _row.split('|')
                _target_max_list.append(_fcltyInfo[0])
                _target_no_list.append(_fcltyInfo[1])
                _target_ty_list.append(_fcltyInfo[2])
            _target['TARGET_MAX_CNT'] = _target_max_list
            _target['TARGET_NO'] = _target_no_list
            _target['TARGET_TYPE'] = _target_ty_list
        DATASET['TARGET_LIST'].append(_target)
        if index == '04':
            _new_target_list = DATASET['TARGET_LIST'].copy()
            for i in range(8):
                _bind_target = {}
                _new_seq = 0
                for target in DATASET['TARGET_LIST']:
                    _bind_target = target.copy()
                    if _bind_target['site_name'] == '전통한옥':
                        _target_no = str(1101 + i)
                        if i == 0:
                            del _new_target_list[_new_seq]
                            if '4' in DATASET['ROOM_RANGE']:
                                _bind_target['TARGET_MAX_CNT'] = [_bind_target['TARGET_MAX_CNT'][0]]
                                _bind_target['TARGET_TYPE'] = [_bind_target['TARGET_TYPE'][0]]
                                _bind_target['TARGET_NO'] = [_target_no]
                                _new_target_list.append(_bind_target)
                        else:
                            _isPass = False
                            #1001은 이미 초반에 입력하였다.
                            if _target_no == '1102' and '4' in DATASET['ROOM_RANGE']:
                                _bind_target['resveNoCode'] = 'HC'
                                _isPass = True
                            elif _target_no == '1103' and '4' in DATASET['ROOM_RANGE']:
                                _bind_target['resveNoCode'] = 'HD'
                                _isPass = True
                            elif _target_no == '1104' and '4' in DATASET['ROOM_RANGE']:
                                _bind_target['resveNoCode'] = 'HE'
                                _isPass = True
                            elif _target_no == '1105' and '4' in DATASET['ROOM_RANGE']:
                                _bind_target['resveNoCode'] = 'HF'
                                _isPass = True
                            elif _target_no == '1106' and '6' in DATASET['ROOM_RANGE']:
                                _bind_target['resveNoCode'] = 'HG'
                                _isPass = True
                            elif _target_no == '1107' and '6' in DATASET['ROOM_RANGE']:
                                _bind_target['resveNoCode'] = 'HH'
                                _isPass = True
                            elif _target_no == '1108' and '2' in DATASET['ROOM_RANGE']:
                                _bind_target['resveNoCode'] = 'HM'
                                _isPass = True
                            if _isPass:
                                _bind_target['TARGET_MAX_CNT'] = [_bind_target['TARGET_MAX_CNT'][0]]
                                _bind_target['TARGET_TYPE'] = [_bind_target['TARGET_TYPE'][0]]
                                _bind_target['TARGET_NO'] = [_target_no]
                                _new_target_list.append(_bind_target)
                    else:
                        _new_target_list.append(target)
                    _new_seq = _new_seq + 1
            DATASET['TARGET_LIST'] = _new_target_list
    return DATASET



def random_useragent():
    result = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.171 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",

        # ✅ Windows - Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",

        # ✅ Windows - Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36 Edg/116.0.1938.54",

        # ✅ macOS - Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",

        # ✅ macOS - Chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Safari/537.36",

        # ✅ macOS - Firefox
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1; rv:116.0) Gecko/20100101 Firefox/116.0",

        # ✅ Android - Chrome
        "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.92 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; SM-G996B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.138 Mobile Safari/537.36",

        # ✅ iPhone - Safari
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.4 Mobile/15E148 Safari/604.1",

        # ✅ iPad - Safari
        "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",

        # ✅ Linux - Chrome
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Safari/537.36",

        # ✅ Linux - Firefox
        "Mozilla/5.0 (X11; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:116.0) Gecko/20100101 Firefox/116.0"
    ])
    return result

# 든바다
# 2인실 ['104','105', '107', '108', '113', '114', '117', '118']
# 4인실 ['120', '121', '122', '123', '103', '109', '116', '102', '111']
# 6인실 ['112', '115', '119']
# 8인실 ['101', '110']
# 10인실 ['106']
# 난바다
# 4인실 ['103', '104', '107', '108', '111', '112']
# 6인실 ['105', '102', '110', '114']
# 8인실 ['101', '109', '113']
# 10인실 ['106', '115']
# 허허바다
# 4인실 ['106', '107', '104', '103']
# 6인실 ['105']
# 8인실 ['102']
# 10인실 ['101', '108']
# 자동차야영장 1~41번까지
# 앞열 5~13
# 취사장 가까운 열 1~4

def get_facility_no(_target, number):
    target_code = _target['resveNoCode']
    result = []
    if target_code == 'MA':  # 든바다
        type = 'D'
        style = '|DEB_'
        if number == '2':
            type = '2|' + type
            result = [type + 'A104' + style + 'A0', type + 'A105' + style + 'A0', type + 'A107' + style + 'A0', type + 'A108' + style + 'A0', type + 'A113' + style + 'A0', type + 'A114' + style + 'A0', type + 'A117' + style + 'A0', type + 'A118' + style + 'A0']
        elif number == '4':
            type = '4|' + type
            result = [type + 'B120' + style + 'B0', type + 'B121' + style + 'B0', type + 'B122' + style + 'B0', type + 'B123' + style + 'B0', type + 'C103' + style + 'C0', type + 'C109' + style + 'C0', type + 'C116' + style + 'C0', type + 'E102' + style + 'E1', type + 'E111' + style + 'E1']
        elif number == '6':
            type = '6|' + type
            result = [type + 'D112' + style + 'D0', type + 'D115' + style + 'D0', type + 'D119' + style + 'D0']
        elif number == '8':
            type = '8|' + type
            result = [type + 'E101' + style + 'E2', type + 'E110' + style + 'E2']
        elif number == '10':
            type = '10|' + type
            result = [type + 'G106' + style + 'G0']
    elif target_code == 'MI':  # 난바다
        type = 'N'
        style = '|NAB_'
        if number == '2':
            type = '2|' + type
            result = []
        elif number == '4':
            type = '4|' + type
            result = [type + 'B103' + style + 'B0', type + 'B104' + style + 'B0', type + 'B107' + style + 'B0', type + 'B108' + style + 'B0', type + 'B111' + style + 'B0', type + 'B112' + style + 'B0']
        elif number == '6':
            type = '6|' + type
            result = [type + 'D105' + style + 'D0', type + 'F102' + style + 'F1', type + 'F110' + style + 'F1', type + 'F114' + style + 'F1']
        elif number == '8':
            type = '8|' + type
            result = [type + 'F101' + style + 'F2', type + 'F109' + style + 'F2', type + 'F113' + style + 'F2']
        elif number == '10':
            type = '10|' + type
            result = [type + 'G106' + style + 'G0', type + 'G115' + style + 'G0']
    elif target_code == 'MB':  # 허허바다
        type = 'H'
        style = '|HHB_'
        if number == '2':
            type = '2|' + type
            result = []
        elif number == '4':
            type = '4|' + type
            result = [type + 'B106' + style + 'B0', type + 'B107' + style + 'B0', type + 'C104' + style + 'C0', type + 'E103' + style + 'E1']
        elif number == '6':
            type = '6|' + type
            result = [type + 'D105' + style + 'D0']
        elif number == '8':
            type = '8|' + type
            result = [type + 'E102' + style + 'E2']
        elif number == '10':
            type = '10|' + type
            result = [type + 'G101' + style + 'G0', type + 'G108' + style + 'G0']
    elif target_code == 'HA':
        for i in range(8):
            value = '0|' + str(1100 + (i + 1)) + '|KH_401'
            result.append(value)
    elif target_code == 'BA':
        result.append('6|1700|1700')
    elif target_code == 'RR':
        for i in range(41):
            value = '0|' + str(1600 + (i + 1)) + '|MA_001'
            result.append(value)
    elif target_code == 'LB':
        if number == '2':
            result = []
        elif number == '4':
            result = []
        elif number == '6':
            result = []
        elif number == '8':
            result = []
        elif number == '10':
            result = []
    elif target_code == 'LA':
        if number == '2':
            result = []
        elif number == '4':
            result = []
        elif number == '6':
            result = []
        elif number == '8':
            result = []
        elif number == '10':
            result = []
    elif target_code == 'CH':
        if number == '2':
            result = []
        elif number == '4':
            result = []
        elif number == '6':
            result = []
        elif number == '8':
            result = []
        elif number == '10':
            result = []
    return result


def get_facility_code(_target, number):
    matches = []
    if _target == '01':
        result2 = ['2|DA104', '2|DA105', '2|DA107',
                   '2|DA108', '2|DA113', '2|DA114',
                   '2|DA117', '2|DA118']
        result4 = ['4|DB120', '4|DB121', '4|DB122',
                   '4|DB123', '4|DC103', '4|DC109',
                   '4|DC116', '4|DE102', '4|ED111']
        result6 = ['6|DD112', '6|DD115', '6|DD119']
        result8 = ['8|DE101', '8|DE110']
        result10 = ['10|DG106']
        merged = result2 + result4 + result6 + result8 + result10
        matches = [x for x in merged if number in x]

    elif _target == '02':
        result4 = ['4|NB103', '4|NB104', '4|NB107',
                   '4|NB108', '4|NB111', '4|NB112']
        result6 = ['6|ND105', '6|NF102', '6|NF110', '6|NF114']
        result8 = ['8|NF101', '8|NF109', '8|NF113']
        result10 = ['10|NG106', '10|NG115']
        merged = result4 + result6 + result8 + result10
        matches = [x for x in merged if number in x]

    elif _target == '03':
        result4 = ['4|HB106', '4|HB107', '4|HC104', '4|HE103']
        result6 = ['6|HD105']
        result8 = ['8|HE102']
        result10 = ['10|HG101', '10|HG108']
        merged = result4 + result6 + result8 + result10
        matches = [x for x in merged if number in x]
    elif _target == '04':
        return
    elif _target == '05':
        return
    elif _target == '06':
        roomNum = 1600 + int(number)
        matches = ['ALL|' + str(roomNum)]
    elif _target == '07':
        return
    elif _target == '08':
        return
    elif _target == '09':
        return
    return matches[0]
