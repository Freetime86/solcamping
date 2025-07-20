from datetime import datetime
import mangsang_utils as mu


def message(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message'
    if DATASET['MESSAGE'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE'] = text
    return DATASET


def message2(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message2'
    if DATASET['MESSAGE2'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE2'] = text
    return DATASET


def message3(DATASET, text, text2):
    text = mu.replaceAll(text, "'")
    text2 = mu.replaceAll(text2, "'")
    DATASET['CURRENT_PROCESS'] = 'message3'
    if DATASET['MESSAGE3'] != text + text2:
        time_str = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if text == '' or text2 == '':
            final_text = text + text2
            print(time_str + ' ' + str(final_text))
        else:
            print(time_str + ' ' + str(text) + '\n' + time_str + ' ' + str(text2))
        DATASET['MESSAGE3'] = text + text2
    return DATASET


def message4(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message4'
    if DATASET['MESSAGE4'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE4'] = text
    return DATASET


def message5(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message5'
    if DATASET['MESSAGE5'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE5'] = text
    return DATASET


def message6(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message6'
    if DATASET['MESSAGE6'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE6'] = text
    return DATASET


def message7(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message7'
    if DATASET['MESSAGE7'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE7'] = text
    return DATASET


def message8(DATASET, text):
    text = mu.replaceAll(text, "'")
    text = mu.replaceAll(text, "\n")
    DATASET['CURRENT_PROCESS'] = 'message8'
    if DATASET['MESSAGE8'] != text:
        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' ' + str(text))
        DATASET['MESSAGE8'] = text
    return DATASET
