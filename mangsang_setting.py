import mangsang_user
import mangsang_facility
from datetime import datetime, timedelta

def dataset():
    dict_data = {
        'USER_INFO': mangsang_user._list(),
        'FACILITY_INFO': mangsang_facility._list(),
        'TARGET_LIST': [],
        'TEMPORARY_HOLD': False,
        'CURRENT_PROCESS': 'START',
        'MESSAGE': 'SYSTEM MAIN MSG',
        'MESSAGE2': 'SYSTEM SENCONDARY MSG',
        'MESSAGE3': 'SYSTEM THIRD MSG',
        'MESSAGE4': 'SYSTEM FOURTH MSG',
        'MESSAGE5': 'SYSTEM FIFTH MSG',
        'MESSAGE6': 'SYSTEM SIXTH MSG',
        'MESSAGE7': 'SYSTEM SEVENTH MSG',
        'MESSAGE8': 'SYSTEM EIGHTH MSG',
        'MESSAGE9': 'SYSTEM NINETH MSG',
        'TRY_RESERVE': False,
        'THREAD_FLAG': True,
        'SECOND_THREAD_FLAG': True,
        'AVAILABLE_TARGET_LIST': [],
        'CANCEL_TARGET_LIST': [],
        'AVAILABLE_NAME_TXT': '',
        'CANCEL_NAME_TXT': '',
        'JUST_RESERVED': False,
        'BOT_STARTING_DELAY': 0,
        'SHOW_WORKS': False,
        'CHECK_DELAY': 60,
        'STAND_BY_TIME': None,
        'WAITING_SLOW': False,
        'POST_TYPE_CODE': '',
        'MULTIPLE_BOT': 2,
        'DELAY_TIME': datetime.now(),
        'OPEN_TIME': datetime.strptime(((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d") + ' 10:59:59'), '%Y-%m-%d %H:%M:%S'),
        'LIMIT_TIME': datetime.strptime(((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")), '%Y-%m-%d')

    }
    return dict_data