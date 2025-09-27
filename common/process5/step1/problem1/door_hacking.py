# brute_force_zip_roundrobin_report.py
from __future__ import annotations
import itertools
import pyzipper
import time
import zlib
from datetime import datetime
from multiprocessing import Process, get_context
from typing import Tuple, List

# 설정값
ZIP_PATH = "emergency_storage_key.zip"
EXTRACT_PATH = "extract"
PASSWORD_PATH = "password.txt"

PWD_LENGTH = 6
DIGITS = "0123456789"
LOW_ALPHA = "abcdefghijklmnopqrstuvwxyz"
CHARSET = DIGITS + LOW_ALPHA
CHARSET = LOW_ALPHA + DIGITS
BASE = len(CHARSET)

UPDATE_BATCH = 1024
UPDATE_SECONDS = 0.5
REPORT_INTERVAL = 5.0

ALL_PREFIXES: List[tuple] = []

def all_prefixes():
    """전체 접두사 생성"""
    global ALL_PREFIXES
    ALL_PREFIXES = list(itertools.product(CHARSET, repeat=1))


def prefixes_for_core_num(P, worker_idx):
    """라운드로빈으로 접두사 할당"""
    return ALL_PREFIXES[worker_idx::P]


def make_password_from_prefix_and_index(prefix: tuple, suffix_idx: int, total_length: int) -> str:
    """
    prefix (tuple of chars) + suffix_idx -> 전체 패스워드 문자열 생성
    suffix는 base-N 숫자를 characters로 변환
    """
    prefix_str = "".join(prefix)
    suffix_len = total_length - len(prefix)
    # suffix_idx를 base-B 문자열로 변환 (뒤에서부터 채우므로 reversed)
    chars = []
    rem = suffix_idx
    for _ in range(suffix_len):
        rem, digit = divmod(rem, BASE)
        chars.append(CHARSET[digit])
    # suffix는 reversed(chars)
    return prefix_str + "".join(reversed(chars))


def worker_process(idx: int, prefixes: list, progress_arr, stop_event):
    """
    각 워커: 주어진 prefixes 리스트에 대해 suffix를 브루트포스
    progress_arr[idx]에 시도한 횟수를 누적
    """
    local_count = 0
    last_update_time = time.time()
    tried_since_update = 0  # 배치 단위 카운터

    try:
        # AESZipFile은 한 번 열어놓고 내부 파일을 매번 open해서 검증
        with pyzipper.AESZipFile(ZIP_PATH) as zf:
            # 보통 첫 파일로 검증하면 충분
            name = zf.namelist()[0]

            for prefix in prefixes:
                # 각 prefix별로 suffix 공간
                suffix_limit = BASE ** (PWD_LENGTH - len(prefix))

                for sidx in range(suffix_limit):
                    if stop_event.is_set():
                        # 다른 프로세스가 찾았음
                        return

                    password = make_password_from_prefix_and_index(prefix, sidx, PWD_LENGTH)
                    tried_since_update += 1
                    local_count += 1

                    try:
                        zf.pwd = password.encode("utf-8")
                        # 최소 읽기(1바이트)로 검증
                        with zf.open(name) as f:
                            f.read(1)

                        # 성공하면 저장하고 종료 신호
                        with open(PASSWORD_PATH, "w", encoding="utf-8") as outf:
                            outf.write(password)
                        stop_event.set()
                        print(f"[WORKER {idx}] Found password: {password}")
                        return

                    except (RuntimeError, pyzipper.BadZipFile, zlib.error):
                        # 틀린 비밀번호 - 무시
                        pass

                    # 주기적 진행도 업데이트 (배치 또는 시간 기준)
                    now = time.time()
                    if tried_since_update >= UPDATE_BATCH or (now - last_update_time) >= UPDATE_SECONDS:
                        # progress_arr는 'q' 타입으로 선언되어 있으므로 안전하게 누적
                        progress_arr[idx] += tried_since_update
                        tried_since_update = 0
                        last_update_time = now

    except Exception:
        # 예외가 발생해도 진행도 반영
        pass
    finally:
        # 종료 시 남은 로컬 카운트 반영
        if tried_since_update:
            progress_arr[idx] += tried_since_update
        # 작업 끝 (정상/중단 모두 여기서 끝남)


def main():
    ctx = get_context("spawn")
    nproc = ctx.cpu_count()
    # nproc = len(CHARSET)
    print(f"CPU count: {nproc}")

    all_prefixes()
    # 전체 검색 공간(LIMIT) 계산 (접두사 수 * 각 접두사의 suffix 공간)
    LIMIT = sum(BASE ** (PWD_LENGTH - len(pref)) for pref in ALL_PREFIXES)

    stop_event = ctx.Event()
    progress_arr = ctx.Array("q", [0] * nproc)  # signed long long

    procs: list[Process] = []
    for i in range(nproc):
        prefixes = prefixes_for_core_num(nproc, i)
        p = ctx.Process(target=worker_process, args=(i, prefixes, progress_arr, stop_event), name=f"worker-{i}")
        p.start()
        procs.append(p)

    # 리포트용 시작 시간
    started_time = time.time()
    started_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        last_total = 0
        last_time = time.time()

        while True:
            # REPORT_INTERVAL 동안 대기, stop_event가 set 되면 즉시 리포트 후 종료
            if stop_event.wait(REPORT_INTERVAL):
                # 누군가 패스워드를 찾았거나 외부에서 중단 신호가 옴
                total = sum(progress_arr[:])
                now = time.time()
                overall_elapsed = now - started_time
                speed = (total - last_total) / (now - last_time) if now > last_time else 0.0
                pct = (total / LIMIT) * 100 if LIMIT > 0 else 0.0

                print(
                    f"[REPORT] 시작: {started_at_str} | 경과: {overall_elapsed:8.1f}s "
                    f"| 총시도: {total:,} | 속도: {speed:,.0f} it/s | 진행률: {pct:6.3f}%"
                )
                break

            # 정기 집계
            total = sum(progress_arr[:])
            now = time.time()
            elapsed = now - started_time
            delta = total - last_total
            interval = now - last_time if now > last_time else 1e-9
            speed = delta / interval
            pct = (total / LIMIT) * 100 if LIMIT > 0 else 0.0

            # 시작 시간과 총 경과 시간을 포함한 리포트 출력
            print(
                f"[REPORT] 시작: {started_at_str} | 경과: {elapsed:8.1f}s "
                f"| 총시도: {total:,} | 속도: {speed:,.0f} it/s | 진행률: {pct:6.3f}%"
            )

            last_total = total
            last_time = now

            # 모든 프로세스가 종료되었으면 루프 탈출
            if not any(p.is_alive() for p in procs):
                break

    except KeyboardInterrupt:
        print("\n[MAIN] KeyboardInterrupt - 종료 신호 전달")
        stop_event.set()
    finally:
        stop_event.set()
        for p in procs:
            p.join(timeout=1.0)
        for p in procs:
            if p.is_alive():
                p.terminate()
        for p in procs:
            p.join()

        total_final = sum(progress_arr[:])
        final_elapsed = time.time() - started_time
        print(f"[MAIN] 최종 총 시도 횟수: {total_final:,} | 총 경과: {final_elapsed:.1f}s")


if __name__ == "__main__":
    main()
