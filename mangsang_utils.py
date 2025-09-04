import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from binascii import unhexlify


def replaceAll(text, target):
    return text.replace(target, '', 99999)


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

