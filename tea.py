'''
tea加解密
'''
from utils import *

DELTA = 0x9e3779b9
# DELTA = -0x61C88647

def tea_encipher(value:List[int], key: List[int], delta: int = None, round: int = None):
    '''
    tea加密 delta为加密常数 round为加密轮数
    '''
    if delta == None:
        delta = DELTA
    if round == None:
        round = 32
    k0, k1, k2, k3 = key[0], key[1], key[2], key[3]
    n = len(value) >> 1  # 组数
    for i in range(n):    # 对每组数据进行处理
        su = 0
        v0, v1 = value[i * 2], value[i * 2 + 1]   # 当前组的2个uint32数据
        for j in range(round):
            su = (su + delta) & 0xffff_ffff
            v0 += ((v1 << 4) + k0) ^ ((v1 >> 5) + k1) ^ (v1 + su)
            v0 &= 0xffff_ffff
            v1 += ((v0 << 4) + k2) ^ ((v0 >> 5) + k3) ^ (v0 + su)
            v1 &= 0xffff_ffff
        value[i * 2], value[i * 2 + 1] = v0, v1

def tea_decipher(value: List[int], key: List[int], delta: int = None, round: int = None):
    '''
    tea解密 delta为解密常数 round为解密轮数
    '''
    if delta == None:
        delta = DELTA
    if round == None:
        round = 32
    k0, k1, k2, k3 = key[0], key[1], key[2], key[3]
    n = len(value) >> 1  # 组数
    for i in range(n):    # 对每组数据进行处理
        su = (delta * round) & 0xffff_ffff # 0xC6EF3720
        v0, v1 = value[i * 2], value[i * 2 + 1]   # 当前组的2个uint32数据
        for j in range(round):
            v1 -= ((v0 << 4) + k2) ^ ((v0 >> 5) + k3) ^ (v0 + su)
            v1 &= 0xffff_ffff
            v0 -= ((v1 << 4) + k0) ^ ((v1 >> 5) + k1) ^ (v1 + su)
            v0 &= 0xffff_ffff
            su = (su - delta) & 0xffff_ffff
        value[i * 2], value[i * 2 + 1] = v0, v1

def xtea_encipher(value: List[int], key: List[int], delta: int = None, round: int = None):
    '''
    xtea加密 delta为加密常数 round为加密轮数
    '''
    if delta == None:
        delta = DELTA
    if round == None:
        round = 32
    n = len(value) >> 1  # 组数
    for i in range(n):    # 对每组数据进行处理
        su = 0
        v0, v1 = value[i * 2], value[i * 2 + 1]   # 当前组的2个uint32数据
        for j in range(round):            
            v0 += (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (su + key[su & 3])
            v0 &= 0xffff_ffff
            su = (su + delta) & 0xffff_ffff
            v1 += (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (su + key[(su >> 11) & 3])
            v1 &= 0xffff_ffff
        value[i * 2], value[i * 2 + 1] = v0, v1

def xtea_decipher(value: List[int], key: List[int], delta: int = None, round: int = None):
    if delta == None:
        delta = DELTA
    if round == None:
        round = 32
    n = len(value) >> 1  # 组数
    for i in range(n):    # 对每组数据进行处理
        su = (delta * round) & 0xffff_ffff # 0xC6EF3720
        v0, v1 = value[i * 2], value[i * 2 + 1]   # 当前组的2个uint32数据
        for j in range(round):            
            v1 -= (((v0 << 4) ^ (v0 >> 5)) + v0) ^ (su + key[(su >> 11) & 3])
            v1 &= 0xffff_ffff
            su = (su - delta) & 0xffff_ffff
            v0 -= (((v1 << 4) ^ (v1 >> 5)) + v1) ^ (su + key[su & 3])
            v0 &= 0xffff_ffff
        value[i * 2], value[i * 2 + 1] = v0, v1

def xxtea_encipher(value: List[int], key: List[int], delta: int = None, round: int = None):
    n = len(value)
    if delta == None:
        delta = DELTA
    if round == None:
        round = 6 + 52 // n
    su = 0
    z = value[n - 1]
    while round > 0:
        su = (su + delta) & 0xffff_ffff
        e = (su >> 2) & 3
        for i in range(n - 1):
            y = value[i + 1]
            value[i] += ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((su ^ y) + (key[(i & 3) ^ e] ^ z))
            value[i] &= 0xffff_ffff
            z = value[i]
        y = value[0]
        value[n - 1] += ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((su ^ y) + (key[((n - 1) & 3) ^ e] ^ z))
        value[n - 1] &= 0xffff_ffff
        z = value[n - 1]
        round -= 1

def xxtea_decipher(value: List[int], key: List[int], delta: int = None, round: int = None):
    n = len(value)
    if delta == None:
        delta = DELTA
    if round == None:
        round = 6 + 52 // n
    su = (round * delta) & 0xffff_ffff
    y = value[0]
    while round > 0:
        e = su >> 2 & 3
        for i in range(n - 1, 0, -1):
            z = value[i-1]
            value[i] -= ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((su ^ y) + (key[(i & 3) ^ e] ^ z))
            value[i] &= 0xffff_ffff
            y = value[i]
        z = value[n - 1]
        value[0] -= ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4)) ^ ((su ^ y) + (key[(0 & 3) ^ e] ^ z))
        value[0] &= 0xffff_ffff
        y = value[0]
        su = (su - delta) & 0xffff_ffff
        round -= 1

if __name__ == '__main__':
    data = [1, 2, 1, 2]
    key = [2, 2, 3, 4]
    tea_encipher(data, key)
    print(data)
    tea_decipher(data, key)
    print(data)
    xtea_encipher(data, key)
    print(data)
    xtea_decipher(data, key)
    print(data)

    data = [1, 2]

    xxtea_encipher(data, key)
    print(data)
    xxtea_decipher(data, key)
    print(data)

    