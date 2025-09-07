import base64
import hashlib
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from binascii import unhexlify
from wcwidth import wcswidth, wcwidth
import re
import unicodedata


def replaceAll(text, target):
    return text.replace(target, '', 99999)


# 1) 유니코드 정규화 + 공백/제로폭 통일
SPACE_RE = re.compile(r'[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000]')  # NBSP/각종 얇은공백/전각공백
ZW_RE = re.compile(r'[\u200B-\u200D\u2060]')  # zero-width, ZWJ/ZWNJ


def normalize_text(s: str) -> str:
    s = '' if s is None else str(s)
    s = unicodedata.normalize('NFKC', s)  # 전각기호/숫자/기호를 반각으로 정규화
    s = ZW_RE.sub('', s)  # 제로폭 제거
    s = SPACE_RE.sub(' ', s)  # 모든 특수공백 → 일반 공백
    s = re.sub(r'\s+', ' ', s).strip()  # 연속공백 1칸으로
    return s


def ljust_display(s: str, width: int, fill: str = ' ') -> str:
    s = '' if s is None else str(s)
    disp = wcswidth(s)
    if disp < 0:  # 제어문자 등 예외
        disp = len(s)
    return s + (fill * max(0, width - disp))


def cut_display(s: str, width: int) -> str:
    # 표시폭 기준으로 잘라내기(길면 ... 없이 자름)
    s = '' if s is None else str(s)
    out, acc = [], 0
    for ch in s:
        w = wcwidth(ch)
        if w < 0:
            w = 0
        if acc + w > width:
            break
        out.append(ch)
        acc += w
    return ''.join(out)


def get_all_day_holidays():
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=30)

    saturdays = []
    current_day = today

    while current_day <= end_date:
        if current_day.weekday() == 5:  # 토요일
            if current_day != today:  # 오늘이 토요일이면 제외
                saturdays.append(current_day.strftime('%Y-%m-%d'))
        current_day += datetime.timedelta(days=1)

    return saturdays


def op_encrypt(plain_text: str) -> str:
    # Constants (from JS function)
    PASS_SALT = "97f2fde29cd4493f199c2f3e9b7df120"
    PASS_IV = "4c1f89c42e9f06036385e90aadd7389f"
    PASS_PHRASE = "v4.0"
    PASS_ITERATION = 1000
    PASS_KEY_SIZE = 16  # 128 bits = 16 bytes

    # Convert hex strings to bytes
    salt = unhexlify(PASS_SALT)
    iv = unhexlify(PASS_IV)

    # Derive key using PBKDF2 (SHA1 by default to match CryptoJS)
    key = hashlib.pbkdf2_hmac(
        hash_name='sha1',
        password=PASS_PHRASE.encode(),
        salt=salt,
        iterations=PASS_ITERATION,
        dklen=PASS_KEY_SIZE
    )

    # AES encrypt using CBC mode and PKCS7 padding
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(plain_text.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded_data)

    # Return base64-encoded string
    return base64.b64encode(encrypted).decode('utf-8')
