import struct
from binascii import crc32

def _crc_32_update(c, b):
    '''
    CRC-32(IEEE)를 1바이트 b로 증분 갱신
    - c: 현재 CRC 값(32비트 정수)
    - b: 0~255 정수(1바이트)
    - c를 seed로 쓰고, 바이트 b를 사용해 새로운 CRC 계산
    - & 0xffffffff로 32비트 정규화
    - ZipCrypto 키 스케줄에서 k0, k2를 갱신할 때 사용
    '''
    return (crc32(bytes([b]), c) & 0xffffffff)


def _init_keys(pwd: bytes):
    '''
    비밀번호로 초기 키 상태 생성
    - k0, k1, k2 초기값은 ZipCrypto 스펙에 고정되어 있음
    '''
    k0, k1, k2 = 0x12345678, 0x23456789, 0x34567890
    for ch in pwd:
        # 비번이 들어올 수록 k0 누적 반영
        k0 = _crc_32_update(k0, ch)
        # k0의 하위 1바이트를 k1에 섞음
        # & 0xffffffff는 % 2**32와 같다.
        # & 0xffffffff는 값의 하위 32비트만 남기고 나머지를 버리는 마스크.
        # - 32비트 부호 없는 정수 환경을 강제로 재현하는 스위치
        # - 파이썬 정수는 무한 정밀도라서 덧셈/곱셈에 오버플라우가 없다 -> '초과하면 하위 32비트만 남는다'가 불가능
        # - ZipCrypto는 모든 중간값을 32비트로 잘라내므로, 연산마다 사용
        k1 = (k1 + (k0 & 0xff)) & 0xffffffff
        # 선형합동법(LCG)로 k1을 의사난수적으로 확산
        # 134775813: 곱셈 상수. ZipCrypto 스펙
        # 1: 덧셈 상수. ZipCrypto 스펙
        # 0xffffffff(2 ^ 32): module, ZipCrypto 스펙
        k1 = (k1 * 134775813 + 1) & 0xffffffff
        # k1의 상위 1바이트를 사용하여 k2 갱신
        k2 = _crc_32_update(k2, (k1 >> 24) & 0xff)
    return [k0, k1, k2]


def _decrypt_byte(keys):
    '''
    키스트림 바이트 1개 생성
    '''
    # k2의 하위 16비트만 사용
    # | 2: 최소한 비트1을 1로 만듬 -> t가 0이나 1같은 값이 되는 것을 막는다.
    # t가 0이나 1이면 t * (t ^ 1)을 하는 의미가 없다.
    t = ((keys[2] & 0xffff) | 2)
    # t * (t ^ 1): t와 t^1(t의 최하위 비트만 반전) 곱
    # t가 짝수(LSB=0)면 t ^ 1 = t+1
    # t가 홀수(LSB=1)면 t ^ 1 = t-1
    # 즉, t * (t ^ 1)은 항상 이웃한 수끼리의 곱
    # → 짝수면 t*(t+1) = t² + t, 홀수면 t*(t-1) = t² - t
    # 단순 XOR/덧셈에 비해 제곱(곱셈)이 들어가면서 비트 간 상호작용이 훨씬 크다.
    # 곱셈은 비트 곱과 덧셈(캐리 포함)의 합성
    # 각 비트끼리 곱해서 나온 부분곱들을 더할 때 캐리(carry, 자리올림) 가 생기고, 이 캐리는 상위 비트로 전파.
    # 그래서 아랫쪽 비트 하나(예: LSB)만 바뀌어도, 곱셈 결과의 여러 상위 비트가 달라질 수 있어요.
    # 덧셈은 캐리가 있지만 여전히 곱셈보다는 상호작용이 제한적.
    # 여기서는 t와 단 1비트만 다른 값(t±1) 을 곱하므로, 그 1비트 차이가 곱셈 과정 전반에 퍼져서 결과의 많은 비트를 건드린다.
    # 이게 “비선형 혼합”과 “확산”이 강하다고 말하는 이유.

    # >> 8: 8비트 오른쪽 시프트 -> 상위 바이트를 아래로
    # 곱셈 결과의 아래쪽 8비트는 부분곱이 직접 겹치는 자리라 통계적 편향(bias)가 클 수 있으므로,
    # 중상위 바이트는 여러 자리에서 올라온 캐리가 섞여서 분포가 고르다.
    # 그래서 중상위 바이트를 사용하기 위해 >> 8로 바이트 영역을 내린다.
    # & 0xff: 1바이트(0~255)만 남김
    return ((t * (t ^ 1)) >> 8) & 0xff


def _update_keys(keys, ch):
    '''
    _init_keys와 같은 규칙을 평문 바이트(ch)에 적용
    ZipCrypto는 평문 바이트로 키를 업데이트하므로, 다음 바이트의 키스트림은 이전까지의 평문 내용에 의존
    그러므로 암호화, 복호화가 동기화되고, 키스트림이 계속 변한다.
    '''
    keys[0] = _crc_32_update(keys[0], ch)
    keys[1] = (keys[1] + (keys[0] & 0xff)) & 0xffffffff
    keys[1] = (keys[1] * 134775813 + 1) & 0xffffffff
    keys[2] = _crc_32_update(keys[2], (keys[1] >> 24) & 0xff)


def _decrypt_header12(enc12: bytes, pwd: bytes) -> bytes:
    '''
    12바이트 암호 헤더 복호화
    '''
    # 비번으로 초기 키 생성
    keys = _init_keys(pwd)
    out = bytearray(12)
    # 12바이트를 순차적으로 복호화
    for i, c in enumerate(enc12):
        # 현재 키 상태로 키스트림 1바이트 생성
        k = _decrypt_byte(keys)
        # 암호문 c XOR 키스트림 = 평문 b
        b = c ^ k
        # 평문 저장
        out[i] = b
        # 평문(b)로 키 상태 갱신
        _update_keys(keys, b)
    # 복호화된 12바이트 반환
    return bytes(out)


def zipcrypto_password_valid(zip_path: str, password: str, entry_index: int = 0) -> bool:
    '''
    ZipCrypto 암호화된 Zip 파일 비밀번호 검증
    - entry_index 엔트리의 로컬 헤더만 읽고 12바이트 헤더를 해제해서 검증
    - AES-Zip, 비암호 Zip은 False 반환
    '''

    pwd = password.encode()
    with open(zip_path, 'rb') as f:
        # ZIP 파일의 각 엔트리 앞에는 고정된 형태의 로컬 파일 헤더가 있다.
        # 괄호 숫자는 바이트 크기

        # [Local File Header] signature(4) ver(2) flag(2) comp(2) time(2) date(2) crc32(4) comp_size(4) uncomp_size(4) fname_len(2) extra_len(2)
        # 고정 바이트: 30 bytes(시그니처(4) + 나머지(26)
        # 다음 바이트는 가변
        # 바이트 순서: 파일명(fname_len) -> 엑스트라(extra_len) -> 실제 파일 데이터 순서

        # signature(4): 항상 PK\x03\x04(리틀엔디언 0x04034b50), 로컬 헤더 시작 표지

        # ver(2): 파일을 풀기 위해 필요한 최소 ZIP 버전

        # flag(2): 일반 목적 비트 플래그
        # - bit0 = 1이면 암호화됨
        # - bit3 = 1이면 데이터 디스크립터(Data Descriptor) 사용.
        # -- bit 3 = 1이면 로컬 헤더만 보고는 데이터 길이를 정확히 알 수 없으므로, 데이터 디스크립터를 읽거나 중앙 디렉터리(Central Directory)를 참고해야 다음 엔트리로 건너뛸 수 있다.
        # 데이터 디스크립터: ZIP 파일에서 파일(엔트리) 데이터가 끝난 직후에 붙는 작은 요약 블록.
        # - 파일을 쓰는 순간엔 크기/CRC를 모를 수 있기에 먼저 0으로 설정하고, 나중에 데이터가 끝난 뒤에 데이터 디스크립터에 진짜 값을 적는다.
        # - crc32, comp_size, uncomp_size가 0일 수 있고, 정확한 값은 데이터 디스크립터에 기록된다.
        # - 데이터 디스크립터에 4바이트 시그니처를 붙일 수도 있고, 안 붙일 수도 있다.
        # - 데이터 디스크립터 시그니처: PK\x07\x08(0x08074b50)
        # - 그러므로 데이터 디스크립터의 처음 4바이트의 값이 PK\x07\x08면 다음 바이트부터 crc32, comp_size, uncomp_size이고,
        # - 처음 4바이트 값이 PK\x07\x08가 아니면, 처음 4바이트부터 crc32, comp_size, uncomp_size이다.

        # comp(2): 압축 방식.
        # - 0 = STORE(무압축)
        # - 8 = DEFLATE(손실 없는 압축 알고리즘)
        # - 99 = AES(Advanced Encryption Standard, 대칭키 블록 암호)
        # time(2): MS-DOS(Microsoft Disk Operating System) 압축 시각
        # date(2): MS-DOS 압축 날짜
        # crc32(4): 원본 데이터의 CRC-32(비트 오류 검출용). flag bit3 = 1이면 0일 수 있다.
        # comp_size(4): 압축(또는 암호화 포함)된 크기. flag bit3 = 1이면 0일 수 있다.
        # uncomp_size(4): 압축 풀린 원본 크기. flag bit3 = 1이면 0일 수 있다.
        # fname_len(2): 바로 뒤에 오는 파일명 길이
        # extra_len(2): 그 다음에 오는 엑스트라 필드 길이(AES 정보 등 확장 메타가 여기에 들어간다)

        # struct: <IHHHHHIIIHH
        # IHHHHHIIIHH: struct 모듈의 포맷 문자열
        # <: 리틀엔디언(작은바이트순)
        # I: 4바이트 unsigned int(signature, crc32, comp_size, uncomp_size)
        # H: 2바이트 unsigned short(ver, flag, comp, time, date, fname_len, extra_len)
        # <I    H    H    H     H     H     I      I          I           H          H
        # sig, ver, flag, comp, time, date, crc32, comp_size, uncomp_size, fname_len, extra_len

        # ZIP엔 보통 여러 파일(엔트리)이 들어 있으니 원하는 엔트리까지 이동하기 위해 entry_index만큼 건너뛰기
        # 1. 시그니처(4) == PK\x03\x04 확인
        # 2. 고정부(26) 바이트 확인
        # 3. 비트0(암호화) 확인
        offset = 0
        for _ in range(entry_index + 1):
            f.seek(offset)
            sig = f.read(4)
            if sig != b'PK\x03\x04':
                return False # 로컬 헤더 아님
            hdr = f.read(26)
            if len(hdr) < 26:
                return False
            ver, flag, comp, time, date, crc32, csize, usize, nlen, xlen = struct.unpack('<IHHHHHIIIHH', hdr)

            # 비트0(암호화)이 켜져 있는지 확인
            encrypted = bool(flag & 0x0001)
            # AES-Zip은 local extra에 0x9901이 붙지만, 여기서는 간단히 comp=99(0x63)로 거르는 편법 가능
            # 엄밀한 판별은 extra 파싱 필요
            if not encrypted:
                return False    # 비암호
            if comp == 99:      # 일반적으로 AES-Zip은 method=99
                return False    # AES-Zip
            
            # 파일명/엑스트라 스킵하고 encrypted data 시작 위치로
            f.seek(nlen + xlen, 1)
            # 첫 12바이트 읽기(ZipCrypto header)
            enc12 = f.read(12)
            if len(enc12) < 12:
                return False
            
            # 해제
            dec12 = _decrypt_header12(enc12, pwd)

            # 검증 바이트 계산(1바이트만 검증, 우연히 맞을 확률 1/256 존재 -> 확실하지 않음)
            # 검증 바이트: bit3 = 0 - time 상위 8비트(1바이트), bit3 = 1 - CRC의 상위 8비트(1바이트)
            if flag & 0x0008:
                check_byte = (time >> 8) & 0xff
            else:
                check_byte = (crc32 >> 24) & 0xff
            
            return dec12[-1] == check_byte
        
        return False