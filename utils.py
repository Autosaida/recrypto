from typing import List, Literal
import struct

'''
字符串 -> 字节序列 
整型 -> 整型列表
大小端序
'''

def long2bytes(number: int, byteorder: Literal['little', 'big'] = 'big', length: int = None) -> bytes:
    '''
    整数number 按指定字节序byteorder、字节数length 转换为字节序列bytes
    若缺省长度则按最小长度
    缺省字节序则按大端序
    '''
    if length == None:
        length = len(hex(number)) - 2
        if length & 1 == 1:
            length = (length >> 1) + 1
        else:
            length = length >> 1
    return number.to_bytes(length, byteorder)


def bytes2long(b: bytes, blocksize: int = 0, byteorder: Literal['little', 'big'] = 'big') -> List[int]:
    '''
    字节序列s 按指定块大小blocksize、字节序byteorder 转换为整数列表
    若缺省块大小则转换为一个整数
    缺省字节序则按大端序
    '''
    fmt = ''
    dic = {1:'B', 2:'H', 4:'I', 8:'Q'}

    if blocksize == 0:
        return [int.from_bytes(b, byteorder)]
    if len(b) % blocksize != 0:
        raise Exception('length error')
    
    if byteorder == 'big':
        fmt += '>'
    elif byteorder == 'little':
        fmt += '<'
    else:
        raise Exception('byteorder must be big or little')
    
    if blocksize in dic:
        length = len(b) // blocksize
        fmt += str(length)
        fmt += dic[blocksize]
        return list(struct.Struct(fmt).unpack(b))
    else:
        raise Exception('blocksize must be 1, 2, 4 or 8')


def hexstr2bytes(s: str) -> bytes:
    '''
    将16进制形式的字符串 转换为 字节序列
    '31323334'  -> (b'1234' | b'\x31\x32\x33\x34')
    '''
    if len(s) & 1 != 0:
        raise Exception('length must be even number')
    return bytes.fromhex(s)

def bytes2hexstr(b: bytes) -> bytes:
    '''
    将字节序列 转换为 16进制形式的字符串
    (b'1234' | b'\x31\x32\x33\x34') -> '31323334'
    '''
    #if len(b) & 1 != 0:
    #    raise Exception('length must be even number')
    return b.hex()

def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    '''
    对等长的两个字节序列进行异或
    '''
    if len(b1) != len(b2):
        raise Exception('length is not equal')
    return b''.join(map(lambda x,y: long2bytes(x^y), b1, b2))

if __name__ == '__main__':
    print(long2bytes(0x31323334,byteorder='big'))
    print(bytes2long(b'12345678',4))
    print(hexstr2bytes('31323334'))
    print(bytes2hexstr(b'\x31\x32\x33\x34'))
    print(xor_bytes(b'12',b'12'))

