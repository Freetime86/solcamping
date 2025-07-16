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
        'THREAD_FLAG': True,
        'AVAILABLE_TARGET_LIST': [],
        'CANCEL_TARGET_LIST': [],
        'AVAILABLE_NAME_TXT': '',
        'CANCEL_NAME_TXT': '',
        'JUST_RESERVED': False,
        'OPEN_TIME': datetime.strptime(((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d") + ' 11:00:00'), '%Y-%m-%d %H:%M:%S'),
        'LIMIT_TIME': datetime.strptime(((datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")), '%Y-%m-%d')

    }
    return dict_data