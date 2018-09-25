import base64
import binascii
import itertools
import time
import sys
import requests
import collections
import xml.etree.ElementTree as ET


VERSION = bytes([4, 0, 7, 0, 0, 12])
EXP = 65537
MOD = [0xbf, 0x40, 0xe2, 0x3e, 0xf8, 0x98, 0xed, 0x1d, 0xf5, 0xe8, 0x2d, 0x55, 0xb6, 0xb1, 0xd2, 0xd4, 0x6a, 0x66, 0xc7, 0xa2, 0x1d, 0xf1, 0x3a, 0x1e, 0x2a, 0x9e, 0x3f, 0xc8, 0x11, 0x5b, 0x7a, 0xaa, 0x7c, 0x90, 0xb6, 0x51, 0xd5, 0x4, 0xdb, 0xc8, 0x32, 0xb6, 0x8, 0x90, 0x23, 0xbb, 0x46, 0x9a, 0x57, 0x2e, 0x83, 0xa, 0x92, 0xc5, 0x98, 0x1d, 0x1e, 0xd6, 0x6e, 0x7e, 0x52, 0x8e, 0xc0, 0xb9]
INFO_PATTERN = 31


Info = collections.namedtuple('Info', ['title', 'patterns', 'xml'])
Pattern = collections.namedtuple('Pattern', ['number', 'title', 'mime_type'])


def _base36(number):
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    if 0 <= number < len(alphabet):
        return alphabet[number]

    result = ''
    while number != 0:
        number, i = divmod(number, len(alphabet))
        result = alphabet[i] + result
    return result


def _parse_type(data):
    code = 1
    secure = 0
    data = data[-16:]
    if data[1] & 1 != 1 or data[2] & 0xc0 != 0xc0:
        raise NotImplementedError()
    version = ((data[2] & 0x1f) << 16) | (data[3] << 8) | data[4]
    if version < 0x19a100:
        code = 2
        if data[2] & 0x20 == 0:
            secure = 1
    return (code, secure)


def parse(data):
    code, secure = _parse_type(data)
    if code == 2:
        top_num = int.from_bytes(data[:-11], byteorder='big')
        top = _base36(top_num % (2 ** 21)).zfill(4)

        bottom_type = ((data[0] & 1) << 2) | (data[1] >> 6)
        bottom_num = int.from_bytes(data[-11:], byteorder='big')
        bottom_shifts = [0, 23, 43, 41, 19, 85, 35]
        bottom_num >>= bottom_shifts[bottom_type]
        bottom = ''
        if bottom_num != 0:
            bottom += str(bottom_num)
        if bottom_type != 0:
            bottom += str(bottom_type)
        if secure == 1:
            bottom += '9'

        return code, secure, top, bottom
    else:
        raise NotImplementedError()


def _encrypt(data, key):
    if key != 0 and key != 1:
        raise NotImplementedError()
    data = int.from_bytes(data, byteorder='big')
    mod = int.from_bytes(MOD, byteorder='big')
    encrypted = pow(data, EXP, mod)
    encrypted_len = (encrypted.bit_length()+7)//8
    return encrypted.to_bytes(encrypted_len, byteorder='big')


def _encode(data):
    data = data[-64:]
    data = b'\0' * (64 - len(data)) + data
    encoded = base64.b64encode(data).decode()
    encoded = encoded.replace('+', '_').replace('/', '-').replace('=', 'A')
    return encoded


def _build_url(data, pattern):
    ms = int(time.time() * 1000)
    ms = ms.to_bytes(6, byteorder='big')
    ver0 = (VERSION[0] & 0xf) << 4 | (VERSION[1] & 0xf)
    ver1 = (VERSION[2] & 0xf) << 4 | (VERSION[5] & 0x1e) >> 1
    ver2 = (VERSION[5] & 1) << 7 | VERSION[4] & 0x7f
    ver = bytes([ver0, ver1, ver2])
    flags = bytes([(1 & 0x7) << 5 | (pattern & 0x1f)])
    packet = data + ms + b'00000000000000000000' + ver + flags
    packet += b'\0' * (64 - len(packet))
    url = 'http://r.beetagg.com/?v='+ver.hex()
    url += '&e=' + _encode(_encrypt(packet, 0))
    return url


def resolve(data, pattern=None):
    url = _build_url(data, INFO_PATTERN if pattern is None else pattern)
    res = requests.get(url, allow_redirects=False)
    if res.status_code in [301, 302]:
        return res.headers['Location']
    elif res.status_code != 200:
        raise RuntimeError()

    xml = ET.fromstring(res.text)

    title = xml.find('./Title')
    if title is not None:
        title = title.text

    patterns = []
    for p in xml.findall('./PatternList/Pattern'):
        patterns.append(Pattern(
            number=int(p.get('number')),
            title=p.find('./Title').text,
            mime_type=p.get('mimetype')))

    return Info(title=title, patterns=patterns, xml=res.text)
