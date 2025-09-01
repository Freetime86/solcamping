from datetime import datetime
import mangsang_utils as mu
import logging
import sys


handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # ← 여기가 datefmt!
)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.handlers = []  # 기존 핸들러 제거
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger = logging.getLogger()

def message(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message'
    if DATASET['MESSAGE'] != text:
        DATASET['MESSAGE'] = text
        logger.info(str(text))
    return DATASET


def message2(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message2'
    if DATASET['MESSAGE2'] != text:
        DATASET['MESSAGE2'] = text
        logger.info(str(text))
    return DATASET


def message3(DATASET, text, text2):
    text = mu.replaceAll(text, "'")
    text2 = mu.replaceAll(text2, "'")
    DATASET['CURRENT_PROCESS'] = 'message3'
    if DATASET['MESSAGE3'] != text + text2:
        final_text = text + text2
        DATASET['MESSAGE3'] = final_text
        if text == '' or text2 == '':
            logger.info(str(final_text))
        else:
            time_str = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            logger.info(str(text) + '\n' + time_str + ' ' + str(text2))

    return DATASET


def message4(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message4'
    if DATASET['MESSAGE4'] != text:
        DATASET['MESSAGE4'] = text
        logger.info(str(text))
    return DATASET


def message5(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message5'
    if DATASET['MESSAGE5'] != text:
        DATASET['MESSAGE5'] = text
        logger.info(str(text))
        DATASET['TRY_RESERVE'] = False
    return DATASET


def message6(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message6'
    if DATASET['MESSAGE6'] != text:
        DATASET['MESSAGE6'] = text
        logger.info(str(text))
    return DATASET


def message7(DATASET, text):
    text = mu.replaceAll(text, "'")
    DATASET['CURRENT_PROCESS'] = 'message7'
    if DATASET['MESSAGE7'] != text:
        DATASET['MESSAGE7'] = text
        logger.info(str(text))
    return DATASET


def message8(DATASET, text):
    text = mu.replaceAll(text, "'")
    text = mu.replaceAll(text, "\n")
    DATASET['CURRENT_PROCESS'] = 'message8'
    if DATASET['MESSAGE8'] != text:
        logger.info(str(text))
        DATASET['MESSAGE8'] = text
    return DATASET


def message9(DATASET, text):
    text = mu.replaceAll(text, "'")
    text = mu.replaceAll(text, "\n")
    DATASET['CURRENT_PROCESS'] = 'message8'
    if DATASET['MESSAGE8'] != text:
        logger.info(str(text))
        DATASET['MESSAGE8'] = text
    return DATASET
