import multiprocessing as mp
from multiprocessing.synchronize import Event as mpEvent
import string, time, itertools
from check_zip_crypto import *
import zipfile, zlib



CHARSET = string.digits + string.ascii_lowercase
PWD_LENGTH = 6
N = 36 ** (PWD_LENGTH - 5)

# ZIP_PATH = 'test.zip'
ZIP_PATH = 'emergency_storage_key.zip'

POW = [len(CHARSET) ** p for p in range(PWD_LENGTH - 1, -1, -1)]


def comp_make_password(ntries):
    j = ''.join
    start_itertools = time.perf_counter()
    for tup in itertools.islice(itertools.product(CHARSET, repeat=PWD_LENGTH), ntries):
        password = j(tup)
    itertools_time = ntries / (time.perf_counter() - start_itertools)

    start_index = time.perf_counter()
    for rem in range(ntries):
        password = []
        for p in range(PWD_LENGTH):
            digit, rem = divmod(rem, POW[p])
            password.append(CHARSET[digit])
        password = ''.join(password)
    index_time = ntries / (time.perf_counter() - start_index)
    return itertools_time, index_time


def bench(ntries):
    j = ''.join
    t0 = time.perf_counter()
    for tup in itertools.islice(itertools.product(CHARSET, repeat=PWD_LENGTH), ntries):
        password = j(tup)
        zipcrypto_password_valid(ZIP_PATH, password)

    

    return ntries / (time.perf_counter() - t0)

if __name__ == '__main__':
    # spawn: 완전히 새 파이썬 인터프리터 프로세스를 띄운 뒤, 필요한 객체만 직렬화(pickle)해서 전달
    # 부모 상태를 거의 복제하지 않음 - 안전하지만 느리다
    # if __name__ == '__main__'를 사용하지 않으면 무한 재귀로 터진다.
    # force: 다른 start method가 설정되어 있어도 강제로 spawn으로 바꾼다.
    # 새 프로세스를 무조건 spawn 방식으로 만든다.
    # 전역 설정
    mp.set_start_method('spawn', force=True)

    # 컨텍스트(context): 멀티프로세싱에서 프로세스, 큐, 락 등 IPC(Inter Process Communication, 프로세스 간 통신) 객체를 start method 규약에 맞춰 생성, 관리할지를 캡슐화한 객체
    # multiprocessing에서 spwan으로 동작하는 컨텍스트 객체를 가져온다.
    # 지역 설정
    ctx = mp.get_context('spawn')


    max_core = 0
    max_total = 0
    # 비밀번호 생성 및 검증 최적 코어 개수 계산
    # 코어 개수 5 ~ 6이 최고 성능
    # for P in range(1, 20):
    #     with ctx.Pool(P) as pool:
    #         rates = pool.map(bench, [N]*P)
    #     total = sum(rates)
    #     max_core = P if max_total < total else max_core
    #     max_total = total if max_total < total else max_total
    #     print(f'{P} workers: {total:.0f} tries/s (per-core {total/P:.0f})')
    # print(f'Best Core Count: {max_core}, {max_total:.0f} tries/s')

    # 비밀번호 생성 함수 성능 비교
    # itertools 사용 vs index 사용
    # itertools가 압도적으로 성능이 좋다.
    for P in range(1, 20):
        with ctx.Pool(P) as pool:
            result = pool.map(comp_make_password, [N]*P)
        total_itertools_time = 0
        total_index_time = 0
        for p in range(P):
            total_itertools_time += result[p][0]
            total_index_time += result[p][1]
        print(f'\n{P} workers itertools: {total_itertools_time:.0f} tries/s (per-core {total_itertools_time/P:.0f})')
        print(f'{P} workers index: {total_index_time:.0f} tries/s (per-core {total_index_time/P:.0f})\n')
    # password = '012345'
    # password = 'mars06'
    # result = zipcrypto_password_valid(ZIP_PATH, password)
    # print(result)

