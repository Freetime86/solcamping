def check(DATASET):
    result = True
    if DATASET['BOT_NUMBER'] < 1:
        print('봇 지정 수 확인')
        result = False
    if  len(DATASET['ROOM_WANTS']) < 1:
        print('룸 선호 정보 확인 (최소 1개의 데이터는 유지 할 것)')
        result = False
    return result


def convert(DATASET):
    # 변경 데이터 KEY
    USER_NO = DATASET['USER_NO']  # 최종 유저
    PINGPONG_NO_1 = DATASET['PIN_PONG_1']  # 최종 유저
    PINGPONG_NO_2 = DATASET['PIN_PONG_2']  # 최종 유저
    FACILITY_LIST = DATASET['ROOM_FACILITY']  # 시설 리스트

    DATASET['CURRENT_USER'] = DATASET['USER_INFO'][USER_NO]
    DATASET['PINGPONG_USER1'] = DATASET['USER_INFO'][PINGPONG_NO_1]
    DATASET['PINGPONG_USER2'] = DATASET['USER_INFO'][PINGPONG_NO_2]

    for index in FACILITY_LIST:
        _target = DATASET['FACILITY_INFO'][index]
        _target_max_list = []
        _target_no_list = []
        _target_ty_list = []
        for _number in DATASET['ROOM_RANGE']:
            _range_list = get_facility_no(_target, _number)
            for _row in _range_list:
                _fcltyInfo = _row.split('|')
                _target_max_list.append(_fcltyInfo[0])
                _target_no_list.append(_fcltyInfo[1])
                _target_ty_list.append(_fcltyInfo[2])
            _target['TARGET_MAX_CNT'] = _target_max_list
            _target['TARGET_NO'] = _target_no_list
            _target['TARGET_TYPE'] = _target_ty_list
        DATASET['TARGET_LIST'].append(_target)

        if DATASET['ROOM_RANGE'] == 0:
            _range_list = get_facility_no(_target, 0)
            for _row in _range_list:
                _fcltyInfo = _row.split('|')
                _target_max_list.append(_fcltyInfo[0])
                _target_no_list.append(_fcltyInfo[1])
                _target_ty_list.append(_fcltyInfo[2])
            _target['TARGET_MAX_CNT'] = _target_max_list
            _target['TARGET_NO'] = _target_no_list
            _target['TARGET_TYPE'] = _target_ty_list
    return DATASET


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
    elif target_code == 'BA':
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
