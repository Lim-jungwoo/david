import zlib
import random
import os

# 다항식 (ZIP/PNG 표준)
POLY = 0xEDB88320

MASK_32 = 0xFFFFFFFF

CRC_TABLE = None

def crc32_bitwise(data: bytes, crc: int = 0) -> int:
    '''비트 단위 CRC32 (가장 단순한 구현, 매 바이트당 8번 루프하므로 느리다.)'''
    crc ^= MASK_32
    for b in data:
        crc ^= b
        for _ in range(8):  # 8비트 처리
            if crc & 1:
                crc = ((crc >> 1) ^ POLY) & MASK_32
            else:
                crc = (crc >> 1) & MASK_32

    return crc ^ MASK_32


def _make_crc_table():
    '''256개 CRC 테이블 생성'''
    table = []
    for i in range(256):
        crc = i
        # CRC(Cyclic Redundancy Check)는 데이터 블록을 다항식 나눗셈으로 본다.
        # 8번 반복 -> 바이트 단위로 처리
        for _ in range(8):
            # 최하위 비트가 1일 때
            # 최하위 비트가 1이면, 다항식 나눗셈 과정에서 나눠떨어지지 않는다는 뜻
            # -> 다항식(0xEDB88320)을 XOR 연산
            # crc >> 1: 나눗셈에서 한 비트 이동
            # XOR POLY: 생성다항식으로 나눌 때, 나머지를 보정
            if crc & 1:
                crc = ((crc >> 1) ^ POLY) & MASK_32
            # 최하위 비트가 0일 때
            # 다항식 나눗셈이 나눠떨어진다.
            # -> 나눗셈에서 한 비트 이동
            else:
                crc = (crc >> 1) & MASK_32
        table.append(crc & MASK_32)
    global CRC_TABLE
    CRC_TABLE = table
    return table


def _make_crc_table_8():
    '''slicing-by-8용 8개 테이블 생성'''
    if CRC_TABLE is None:
        crc_table = _make_crc_table()
    T = [crc_table]
    for k in range(1, 8):
        Tk = [0] * 256
        for i in range(256):
            prev = T[k - 1][i]
            Tk[i] = (crc_table[prev & 0xFF] ^ (prev >> 8)) & MASK_32
        T.append(Tk)
    global CRC_TABLE_8
    CRC_TABLE_8 = T
    global T0, T1, T2, T3, T4, T5, T6, T7
    T0, T1, T2, T3, T4, T5, T6, T7 = T
    return T


def crc32_table(data: bytes, crc: int = 0, zlib: bool = True) -> int:
    '''
    테이블 기반 CRC32 (빠르다)
    zlib: True - zlib.crc32와 동일하게 작동
    zlib: False - 처음, 끝 XOR 연산 없이 작동
    zlib에서는 처음과 끝에 crc에 XOR 연산을 하는데, ZipCrypto에서 crc를 사용해서 key를 만들 때는 crc를 그대로 사용한다.
    그래서 zlib을 False로 주면 ZipCrypto에서 key를 만들 때, crc를 XOR연산 없이 그대로 사용할 수 있다.
    '''
    # crc: 지금까지 누적된 CRC 값
    # data: 새로 추가되는 데이터 바이트
    # CRC_TABLE: 미리 계산해둔 CRC-32 테이블
    # (crc ^ b) & 0xFF: CRC의 하위 8비트와 새 바이트 b를 XOR한 값을 테이블 인덱스로 사용
    # - 새로운 바이트를 기존 CRC의 끝부분과 합쳐서 나눗셈 시작
    # CRC_TABLE[...]: 인덱스를 사용해서 CRC 보정값을 테이블에서 가져온다
    # crc >> 8: CRC를 8비트 오른쪽 시프트 - CRC가 한 바이트 처리된 것과 같은 효과
    # 마지막 ^ 연산: 시프트한 CRC 상위 24비트와 보정값을 XOR -> 새로운 CRC 생성
    if CRC_TABLE is None:
        _make_crc_table()
    if zlib:
        crc = (crc ^ MASK_32) & MASK_32
    for b in data:
        crc = (CRC_TABLE[(crc ^ b) & 0xFF] ^ (crc >> 8)) & MASK_32
    if zlib:
        return (crc ^ MASK_32) & MASK_32
    return crc & MASK_32


def crc32_slicing_by_8(data: bytes, crc: int = 0, zlib: bool = True) -> int:
    '''
    slicing-by-8 CRC-32 (polynomial 0xEDB88320).
    zlib: True - zlib.crc32와 동일하게 작동
    zlib: False - 처음, 끝 XOR 연산 없이 작동
    zlib에서는 처음과 끝에 crc에 XOR 연산을 하는데, ZipCrypto에서 crc를 사용해서 key를 만들 때는 crc를 그대로 사용한다.
    그래서 zlib을 False로 주면 ZipCrypto에서 key를 만들 때, crc를 XOR연산 없이 그대로 사용할 수 있다.
    '''
    if CRC_TABLE is None:
        _make_crc_table_8()

    if zlib:
        crc = (crc ^ MASK_32) & MASK_32
    n = len(data)
    i = 0

    # 8바이트 정렬
    while n - i >= 8:
        b0 = data[i+0]
        b1 = data[i+1]
        b2 = data[i+2]
        b3 = data[i+3]
        b4 = data[i+4]
        b5 = data[i+5]
        b6 = data[i+6]
        b7 = data[i+7]

        # 테이블 룩업 - zlib의 slicing-by-8 접근과 동일 컨셉
        crc = (T7[(crc ^ b0) & 0xFF] ^
               T6[((crc >> 8) ^ b1) & 0xFF] ^
               T5[((crc >> 16) ^ b2) & 0xFF] ^
               T4[((crc >> 24) ^ b3) & 0xFF] ^
               T3[b4] ^ T2[b5] ^ T1[b6] ^ T0[b7]) & MASK_32
        i += 8

    # 남은 바이트 처리 (table-driven)
    while i < n:
        crc = (T0[(crc ^ data[i]) & 0xFF] ^ (crc >> 8)) & MASK_32
        i += 1

    if zlib:
        return (crc ^ MASK_32) & MASK_32
    return crc


if __name__ == '__main__':
    # 테이블 생성
    _make_crc_table_8()

    # 고정 벡터
    for s in [b'', b'hello', b'hello world', b'\x00' * 31 + b'\xff' * 97]:
        # b'': 빈 입력
        # b'hello', b'hello world': 짧은 평문
        # b'\x00' * 31, b'\xff' * 97: 특이패턴(0x00 연속, 0xff 연속)
        a = crc32_table(s)
        b = crc32_slicing_by_8(s)
        c = zlib.crc32(s) & MASK_32
        assert a == b == c, (a, b, c)
    print('fixed tests: OK')

    # 랜덤
    rnd = random.Random(0xC0FFEE)   # 난수 생성기 0xCOFFEE 시드로 초기화
    for _ in range(50):
        s = os.urandom(rnd.randrange(0, 50_000))    # 랜덤 길이의 난수 바이트 열 생성
        a = crc32_slicing_by_8(s)
        b = zlib.crc32(s) & MASK_32
        assert a == b
    print('random tests: OK')

    # 스트리밍(누적), 한 번에 계산한 값과, 2번 계산한 결과가 같은지 확인
    s = os.urandom(100_000)
    one = crc32_slicing_by_8(s)
    mid = len(s) // 2
    acc = crc32_slicing_by_8(s[:mid], 0)
    acc = crc32_slicing_by_8(s[mid:], acc)
    assert one == acc == (zlib.crc32(s) & MASK_32)
    print('streaming tests: OK')