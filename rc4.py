'''
rc4加解密
'''
from utils import *

def rc4_init(key: bytes) -> List[int]:
    '''
    使用密钥key 生成s盒
    '''
    s = [0] * 256
    t = [0] * 256
    j = 0
    # 初始化256字节的s向量与t向量
    for i in range(256):
        s[i] = i
        t[i] = key[i % len(key)]
    # 根据t向量置换s向量得到s盒
    for i in range(256):
        j = (j + s[i] + t[i]) % 256
        s[i], s[j] = s[j], s[i]
    return s

def rc4_keystream(key: bytes, length: int) -> bytes:
    '''
    根据密钥key 生成指定长度密钥流 rc4密钥流
    '''
    # 生成s盒
    s = rc4_init(key)   
    keystream = b''
    i = j = 0
    for k in range(length):
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]     # 每轮置换s盒
        pos = (s[i] + s[j]) % 256
        # s[pos]为密钥流中的一个字节，构成的向量即为密钥流
        keystream +=  long2bytes(s[pos])
    return keystream

def rc4_xor(data: bytes, key: bytes) -> bytes:
    '''
    根据密钥key 对数据data进行rc4加密/解密
    '''
    # 生成密钥流
    keystream = rc4_keystream(key, len(data))
    # 明密文与密钥流异或
    return xor_bytes(data, keystream)

    
if __name__ == '__main__':
    m = b'12345'
    key = b'key'
    c = rc4_xor(m, key)
    print(bytes2hexstr(c))
    print(rc4_xor(c, key))
    
