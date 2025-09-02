import os, time, random, statistics, hashlib, itertools, sys
import multiprocessing as mp
from multiprocessing.synchronize import Event as mpEvent
import string
import queue

# ------------- 설정
CHARSET = string.ascii_lowercase + string.digits
BASE = len(CHARSET)
PWD_LEN = 6
TOTAL_CANDIDATES = BASE ** PWD_LEN  # 전체 공간 (36^6 ~= 2.18e9, 실제 벤치는 N으로 제한)
# 벤치마크에서는 N만큼만 검사
N = 30_000

# 검증 비용(해시 반복) - 숫자 높일 수록 CPU-bound 강해짐
PBKDF2_ITER = 1_000
SALT = b'codyssey-demo-salt'

# 코어 수 스윕
P_VALUES = list(range(1, 20)) # 1 ~ 19 코어


TEST_INDEX = 20000

# -------------- 유틸: 인덱스 -> 비밀번호
POW = [BASE ** p for p in range(PWD_LEN)]

def index_to_password(idx: int) -> str:
    '''
    idx (0 .. N-1)을 진법 전개로 PWD_LEN 길이 비번으로 변환
    '''
    out = [None] * PWD_LEN
    rem = idx
    # 큰 자릿수부터 채움
    for i, p in enumerate(range(PWD_LEN - 1, -1, -1)):
        digit, rem = divmod(rem, POW[p])
        out[i] = CHARSET[digit]
    return ''.join(out)


# --------------- 유틸: 검증
def pbkdf2_check(password: str, salt: bytes, target_dk: bytes, iterations: int) -> bool:
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return dk == target_dk


# -------------- Pool 쪽 전역
# 워커에서 사용할 전역
STOP_EVENT: mpEvent = None
G_SALT = None
G_TARGET_DK = None
G_ITERS = None

def pool_init(event, salt, target_dk, iters):
    global STOP_EVENT, G_SALT, G_TARGET_DK, G_ITERS
    STOP_EVENT = event
    G_SALT = salt
    G_TARGET_DK = target_dk
    G_ITERS = iters


def pool_worker(idx: int):
    # 조기 종료 신호 확인
    if STOP_EVENT.is_set():
        return None
    pw = index_to_password(idx)
    if pbkdf2_check(pw, G_SALT, G_TARGET_DK, G_ITERS):
        # 찾으면 이벤트 Set (다른 워커들 중단)
        STOP_EVENT.set()
        return (idx, pw)
    return None


def pool_worker_idx_only(idx: int):
    '''
    조기 종료 없이 끝까지 수행
    '''
    pw = index_to_password(idx)
    # 해시만 수행 (결과는 버림)
    hashlib.pbkdf2_hmac('sha256', pw.encode(), SALT, PBKDF2_ITER)
    return None


# --------------- Process 쪽 워커
## task_q 중앙 큐를 사용하면 무한 대기 상태가 발생할 가능성이 많다.
## 사용하지 않는다.
def proc_worker(stop_event: mpEvent, task_q: mp.Queue, found_q: mp.Queue, salt: bytes, target_dk: bytes, iters: int):
    while True:
        if stop_event.is_set():
            break
        try:
            item = task_q.get(timeout=0.1)
        except queue.Empty:
            continue
        if item is None:
            break
        idx = item
        pw = index_to_password(idx)
        if pbkdf2_check(pw, salt, target_dk, iters):
            # 찾음 -> 알림
            try:
                found_q.put_nowait((idx, pw))
            except queue.Full:
                pass
            stop_event.set()
            break


# ------------ 라운드로빈 워커: 중앙 큐 없이 각자 i=start, i+=P로 탐색
def rr_worker(stop_event: mpEvent, start: int, step: int, N: int, salt: bytes, target_dk: bytes, iters: int, found_q: mp.Queue):
    i = start
    while not stop_event.is_set() and i < N:
        pw = index_to_password(i)
        if pbkdf2_check(pw, salt, target_dk, iters):
            try:
                found_q.put_nowait((i, pw))
            except Exception:
                pass
            stop_event.set()
            break
        i += step


def rr_worker_full(start: int, step: int, N: int):
    '''
    조기 종료 없이 끝까지 수행
    '''
    for i in range(start, N, step):
        pw = index_to_password(i)
        hashlib.pbkdf2_hmac('sha256', pw.encode(), SALT, PBKDF2_ITER)

# ------------- 실행기: Pool
def run_with_pool(P: int, N: int, target_idx: int, salt: bytes, target_dk: bytes, iters: int):
    ctx = mp.get_context('spawn')
    stop = ctx.Event()
    t0 = time.perf_counter()
    found = None
    try:
        with ctx.Pool(
            processes=P,
            initializer=pool_init,
            initargs=(stop, salt, target_dk, iters)
        ) as pool:
            # 순서 무시, 끝나는 대로 받음 + chunksize 튜닝
            # chunksize = max(1, N // (P * 16))
            chunksize = min(1024, max(32, N // (P * 64)))
            for res in pool.imap_unordered(pool_worker, range(N), chunksize=chunksize):
                if res is not None:
                    found = res
                    # 풀을 즉시 정리
                    pool.terminate()
                    pool.join()
                    break
    except KeyboardInterrupt:
        print('\n[Pool] Ctrl+C detected - stopping...')
        stop.set()
        try:
            pool.terminate()
            pool.join()
        except Exception:
            pass
        raise
    t1 = time.perf_counter()
    return found, (t1 - t0)


def run_with_pool_full(P: int, N: int):
    '''
    조기 종료 없이 끝까지 수행
    '''
    ctx = mp.get_context('spawn')
    t0 = time.perf_counter()
    with ctx.Pool(processes=P) as pool:
        chunksize = min(1024, max(32, N // (P * 64)))
        for _ in pool.imap_unordered(pool_worker_idx_only, range(N), chunksize):
            pass
    return time.perf_counter() - t0

# ---------------- 실행기
def run_with_process(P: int, N: int, target_idx: int, salt: bytes, target_dk: bytes, iters: int):
    ctx = mp.get_context('spawn')
    stop: mpEvent = ctx.Event()

    # # 작업 버퍼 크기 10_000으로 제한
    # # CPU-bound 작업 버퍼는 10_000이면 충분
    ## task를 중앙 큐로 사용하면 무한 대기 발생 확률 높음
    # task_q = ctx.Queue(maxsize=10_000)

    # 값을 찾았을 때 저장하는 버퍼
    # 혹시 여러 워커가 동시에 찾았을 때를 대비해서 버퍼 크기 8로 설정
    found_q = ctx.Queue(maxsize=4)

    procs = [ctx.Process(target=rr_worker, args=(stop, start, P, N, salt, target_dk, iters, found_q)) for start in range(P)]

    t0 = time.perf_counter()
    found = None
    try:
        # 1) 워커 시작
        for p in procs:
            p.start()

        # 결과 대기 (조기 종료 지원 + 안전 타임아웃)
        # 필요하면 per-run timeout(예: 60초)을 걸어 무한 대기 방지
        HARD_TIMEOUT = None # 초 단위. 필요하면 숫자 지정
        deadline = None if HARD_TIMEOUT is None else (time.perf_counter() + HARD_TIMEOUT)

        while True:
            if stop.is_set():
                # 다른 워커가 찾았거나 중단 신호
                try:
                    found = found_q.get_nowait()
                except Exception:
                    pass
                break
            try:
                found = found_q.get(timeout=0.01) # 10ms 폴링
                stop.set()
                break
            except Exception:
                # 워커 모두 종료됐는지 확인
                if not any(p.is_alive() for p in procs):
                    break
                if deadline is not None and time.perf_counter() > deadline:
                    # 안전장치: 너무 오래 걸리면 강제 종료
                    stop.set()
                    break

        # 정리(남아있으면 강제 종료)
        for p in procs:
            p.join(timeout=1.0)
        for p in procs:
            if p.is_alive():
                p.terminate()
        for p in procs:
            p.join()

    except KeyboardInterrupt:
        print('\n[Process] Ctrl+C detected - stopping...')
        stop.set()
        for p in procs:
            try: p.terminate()
            except Exception: pass
        for p in procs:
            try: p.join()
            except Exception: pass
        raise

    t1 = time.perf_counter()
    return found, (t1 - t0)


def run_with_process_full(P: int, N: int):
    '''
    조기 종료 없이 끝까지 수행
    '''
    ctx = mp.get_context('spawn')
    procs = [ctx.Process(target=rr_worker_full, args=(s, P, N)) for s in range(P)]
    t0 = time.perf_counter()
    for p in procs: p.start()
    for p in procs: p.join()
    return time.perf_counter() - t0


def s15(value: str):
    return f'{value:15s}'


def f3s15(value: float):
    return f'{value:<15.3f}'


def b15(value: bool):
    return f'{str(value):<15}'


# -------------- 벤치마크
def benchmark(P_values, N, trials=3, warmups=1):
    '''
    P_values(코어 수)마다 결과를 구한다.
    warmup만큼 먼저 실행하고, trials만큼 실행한 결과의 중앙값을 구한다.
    '''

    # 타겟 비밀번호
    # target_idx = random.randrange(0, N)
    # test용 인덱스
    target_idx = TEST_INDEX
    target_pw = index_to_password(target_idx)
    target_dk = hashlib.pbkdf2_hmac('sha256', target_pw.encode(), SALT, PBKDF2_ITER)

    print(f'Target index: {target_idx}, password: {target_pw}')
    print(f'N={N}, PBKDF2_ITER={PBKDF2_ITER}\n')
    print(f'{s15('P')}{s15('Pool(s)')}{s15('Process(s)')}{s15('Winner')}(found_idx==target?)')

    best_core = 0
    best_method = None
    best_time = sys.maxsize
    for P in P_values:
        pool_times, proc_times = [], []
        pool_found, proc_found = None, None

        for r in range(warmups + trials):
            # Pool
            try:
                # f, t = run_with_pool(P, N, target_idx, SALT, target_dk, PBKDF2_ITER)
                t = run_with_pool_full(P, N)
            except KeyboardInterrupt:
                print('Interruped during Pool run.')
                sys.exit(1)
            if r >= warmups:
                pool_times.append(t)
                # pool_found = f or pool_found

        # pool_med = statistics.median(pool_times)
        # print(pool_med)

            # Process
            try:
                # f2, t2 = run_with_process(P, N, target_idx, SALT, target_dk, PBKDF2_ITER)
                t2 = run_with_process_full(P, N)
            except KeyboardInterrupt:
                print('Interrupted during Process run.')
                sys.exit(1)
            if r >= warmups:
                proc_times.append(t2)
                # proc_found = f2 or proc_found

        # proc_med = statistics.median(proc_times)
        # print(proc_med)

        pool_med = statistics.median(pool_times)
        proc_med = statistics.median(proc_times)

        if best_time > pool_med:
            best_core = P
            best_method = 'Pool'
            best_time = pool_med
        if best_time > proc_med:
            best_core = P
            best_method = 'Process'
            best_time = proc_med
        
        winner = 'Pool' if pool_med < proc_med else 'Process'
        ok = (pool_found and pool_found[0] == target_idx) and (proc_found and proc_found[0] == target_idx)
        print(f'{s15(str(P))}{f3s15(pool_med)}{f3s15(proc_med)}{s15(winner)}{b15(ok)}')

    print(f'\nBest Core: {best_core}, Best Method: {best_method}, Best Time: {f3s15(best_time)}')
    print('\nDone.')


if __name__ == '__main__':
    try:
        benchmark(P_VALUES, N, trials=3, warmups=1)
    except KeyboardInterrupt:
        print('\n[Main] Ctrl+C - exit.')