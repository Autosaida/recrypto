'''
base编码与解码
'''
import struct
from utils import *

charset_base32 = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
charset_base36 = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
charset_base58 = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
charset_base62 = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
charset_base64 = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
charset_base85 = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~'
charset_base91 = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"'

def b64encode(b: bytes, charset: bytes = None) -> bytes:
    '''
    base64
    根据提供的charset进行base64编码
    缺省则为默认字符集
    6 bit -> 1 char
    3 byte -> 4 char
    '''
    if charset == None:
        charset = charset_base64
    assert len(charset) == len(charset_base64)

    left = len(b) % 3
    if left:
        b += b'\0' * (3 - left)
    encoded = bytearray()
    for i in range(0, len(b), 3):
        encoded += long2bytes(charset[b[i] >> 2])
        encoded += long2bytes(charset[((b[i] & 0x3) << 4) | (b[i + 1] >> 4)])
        encoded += long2bytes(charset[((b[i + 1] & 0xf) << 2) | (b[i + 2] >> 6)])
        encoded += long2bytes(charset[b[i + 2] & 0x3f])
    if left == 1:
        encoded[-2:] = b'=='
    if left == 2:
        encoded[-1:] = b'='
    return bytes(encoded)
    
def b64decode(b: bytes, charset: bytes = None) -> bytes:
    '''
    base64
    根据提供的charset进行base64解码
    缺省则为默认字符集
    1 char -> 6 bit
    4 char -> 3 byte
    '''
    if charset == None:
        charset = charset_base64
    assert len(charset) == len(charset_base64)

    charset_rev = {value: pos for pos, value in enumerate(charset)}

    l = len(b) 
    b = b.rstrip(b'=')
    padlen = l - len(b)
    b += long2bytes(charset[0]) * padlen   # MTIzNDU= -> MTIzNDU?
    
    decoded = bytearray()
    for i in range(0, len(b), 4):
        decoded += long2bytes((charset_rev[b[i]] << 2) | (charset_rev[b[i + 1]] >> 4))
        decoded += long2bytes(((charset_rev[b[i + 1]] & 0xf) << 4) | (charset_rev[b[i + 2]] >> 2))
        decoded += long2bytes(((charset_rev[b[i + 2]] & 0x3) << 6)  | (charset_rev[b[i + 3]]))
    
    if padlen:
        decoded = decoded[:-padlen]
    return bytes(decoded)

def b32encode(b: bytes, charset: bytes = None) -> bytes:
    '''
    base32
    根据提供的charset进行base32编码
    缺省则为默认字符集
    5 bit -> 1 char
    5 byte -> 8 char
    '''
    if charset == None:
        charset = charset_base32
    assert len(charset) == len(charset_base32)
    
    left = len(b) % 5
    if left:
        b = b + b'\0' * (5 - left)
    
    encoded = bytearray()
    for i in range(0, len(b), 5):
        c = bytes2long(b[i: i + 5])[0]
        encoded += (long2bytes(charset[(c >> 35) & 0x1f]) +
                    long2bytes(charset[(c >> 30) & 0x1f]) +
                    long2bytes(charset[(c >> 25) & 0x1f]) +
                    long2bytes(charset[(c >> 20) & 0x1f]) +
                    long2bytes(charset[(c >> 15) & 0x1f]) +
                    long2bytes(charset[(c >> 10) & 0x1f]) +
                    long2bytes(charset[(c >> 5) & 0x1f])  +
                    long2bytes(charset[c & 0x1f]) )
    if left == 1:
        encoded[-6:] = b'======'
    elif left == 2:
        encoded[-4:] = b'===='
    elif left == 3:
        encoded[-3:] = b'==='
    elif left == 4:
        encoded[-1:] = b'='
    return bytes(encoded)

def b32decode(b: bytes, charset: bytes = None) -> bytes:
    '''
    base32
    根据提供的charset进行base32解码
    缺省则为默认字符集
    1 char -> 5 bit
    8 char -> 5 byte
    '''
    if charset == None:
        charset = charset_base32
    assert len(charset) == len(charset_base32)

    charset_rev = {value: pos for pos, value in enumerate(charset)}

    l = len(b)
    b = b.rstrip(b'=')
    padlen = l - len(b)

    decoded = bytearray()
    for i in range(0, len(b), 8):
        s = b[i: i + 8]
        acc = 0
        for c in s:
            acc = (acc << 5) + charset_rev[c]
        decoded += long2bytes(acc)

    padmap = {1: 4, 3: 3, 4: 2, 6: 1}
    if padlen:
        acc <<= 5 * padlen
        last = long2bytes(acc)
        left = padmap[padlen]
        decoded[-5:] = last[:left]
    return bytes(decoded)

'''
def b58encode(s: bytes, charset: bytes = None) -> bytes:
    if charset == None:
        charset = charset_base58
    assert len(charset) == len(charset_base58)

    encoded = b''
    acc = int.from_bytes(s,'big')
    while acc:
        acc, pos = divmod(acc, 58)
        encoded = charset[pos].to_bytes(1,'little') + encoded
    return encoded

def b58decode(s:bytes,charset:bytes=None)->bytes:
    if charset == None:
        charset = charset_base58
    assert len(charset) == len(charset_base58)

    charset_rev = {value: pos for pos, value in enumerate(charset)}
    decimal = 0
    decoded = bytearray()
    for char in s:
        decimal = decimal * 58 + charset_rev[char]

    while decimal > 0:
        decimal, mod = divmod(decimal, 256)
        decoded += mod.to_bytes(1,'little')

    decoded.reverse()
    return bytes(decoded)

def b85encode(s, charset=None):
    if charset == None:
        charset = charset_base85
    assert len(charset) == len(charset_base85)
    charset2 = [(a.to_bytes(1,'big') + b.to_bytes(1,'big')) for a in charset for b in charset]

    padding = (-len(s)) % 4
    if padding:
        s = s + b'\0' * padding
    words = struct.Struct('!%dI' % (len(s) // 4)).unpack(s)
    encoded = bytearray()
    for word in words:
        #encoded = encoded + charset2[word // 614125] + charset2[word // 85 % 7225] + charset2[word % 85][1:]
        encoded = encoded + charset2[word // 614125] + charset2[word // 85 % 7225] + charset[word % 85].to_bytes(1,'big')
    if padding:
        encoded = encoded[:-padding]
    return bytes(encoded)

def b85decode(s,charset=None):
    if charset == None:
        charset = charset_base85
    assert len(charset) == len(charset_base85)

    charset_rev = {value: pos for pos, value in enumerate(charset)}

    padding = (-len(s)) % 5
    s = s + b'~' * padding
    decoded = []
    packI = struct.Struct('!I').pack
    for i in range(0, len(s), 5):
        chunk = s[i:i + 5]
        acc = 0
        for c in chunk:
            acc = acc * 85 + charset_rev[c]
        decoded.append(packI(acc))

    result = b''.join(decoded)
    if padding:
        result = result[:-padding]
    return result


def b91encode(s:bytes, charset:bytes=None)->bytes:
    if charset == None:
        charset = charset_base91
    assert len(charset) == len(charset_base91)
    acc = 0
    num = 0
    encoded = b''
    for i in range(len(s)):
        byte = s[i]
        acc = (byte << num) + acc
        num += 8
        if num > 13:
            v = acc & 8191
            if v > 88:
                acc >>= 13
                num -= 13
            else:
                v = acc & 16383
                acc >>= 14
                num -= 14
            encoded += charset[v % 91].to_bytes(1, 'big') + charset[v // 91].to_bytes(1, 'big')
    if num != 0:
        encoded += charset[acc % 91].to_bytes(1, 'big')
        if num > 7 or acc // 91 != 0:
            encoded += charset[acc // 91].to_bytes(1, 'big')
    return encoded


def b91decode(s:bytes, charset:bytes=None)->bytes:
    if charset == None:
        charset = charset_base91
    assert len(charset) == len(charset_base91)

    charset_rev = {value: pos for pos, value in enumerate(charset)}

    v = -1
    acc = 0
    num = 0
    decoded = bytearray()
    for i in range(len(s)):
        c = charset_rev[s[i]]
        if (v < 0):
            v = c
        else:
            v += c * 91
            acc |= v << num
            if (v & 8191) > 88:
                num += 13
            else:
                num += 14
            while True:
                decoded += (acc & 0xff).to_bytes(1, 'little')
                acc >>= 8
                num -= 8
                if not num > 7:
                    break
            v = -1
    if v + 1:
        decoded += (((v << num)+ acc) & 0xff).to_bytes(1,'little')
    return bytes(decoded)
'''

if __name__ == '__main__':
    data = b'123'
    encoded64 = b64encode(data)
    print(encoded64)
    print(b64decode(encoded64))

    encoded32 = b32encode(data)
    print(encoded32)
    print(b32decode(encoded32))