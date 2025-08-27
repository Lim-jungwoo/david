from __future__ import annotations

# from zipfile import ZipFile, BadZipFile
import pyzipper
import zlib
import time
from datetime import datetime
import multiprocessing
from multiprocessing.synchronize import Event as EventClass
from multiprocessing.sharedctypes import Synchronized
from multiprocessing import Process, Value

ZIP_PATH = 'emergency_storage_key.zip'
# ZIP_PATH = 'test.zip'
EXTRACT_PATH = 'extract'
PASSWORD_PATH = 'password.txt'
PASSWORD_LENGTH = 6
TEST_PASSWORD = 'aaaaaa'

DIGITS = '0123456789'
LOW_ALPHA = 'abcdefghijklmnopqrstuvwxyz'

CHARSET = DIGITS + LOW_ALPHA

POW = [len(CHARSET) ** p for p in range(PASSWORD_LENGTH - 1, -1, -1)]

LIMIT = len(CHARSET) ** PASSWORD_LENGTH

TIME_OUT = 3

def make_password(count: int, length: int) -> str:
    password = []
    rem = count
    for p in range(length):
        digit, rem = divmod(rem, POW[p])
        password.append(CHARSET[digit])
    return ''.join(password)


def unlock_zip(count: Synchronized[int], stop_event: EventClass):
    start_time = time.time()
    last_report = start_time
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    repeat = 0

    try:
        while count.value < LIMIT:
            if stop_event.is_set():
                raise KeyboardInterrupt()
            
            with count.get_lock():
                count.value += 1
                repeat = count.value - 1

            password = make_password(repeat, PASSWORD_LENGTH)


                
            # test
            # if password == TEST_PASSWORD:
            #     break

            now = time.time()
            if now - last_report >= 1:
                elasped = now - start_time
                print(f'{multiprocessing.current_process().name}, 시작 시간: {started_at} | 진행 시간: {elasped:8.2f}s | 반복 횟수: {repeat:12d} | 비밀번호: {password:6s}')
                last_report = now


            try:
                with pyzipper.AESZipFile(ZIP_PATH) as zf:
                    zf.pwd = password.encode('utf-8')
                    zf.extractall(EXTRACT_PATH)

                with open(PASSWORD_PATH, 'w', encoding='utf-8') as f:
                    f.write(password)

                stop_event.set()

                break
            except (RuntimeError, pyzipper.BadZipFile, zlib.error):
                continue
            except KeyboardInterrupt:
                raise KeyboardInterrupt()
    except KeyboardInterrupt:
        print(f'{multiprocessing.current_process()}시스템 종료')
        return

    total_elasped = time.time() - start_time
    print(f'\n{multiprocessing.current_process()} 종료: 반복횟수: {repeat}, 진행 시간: {total_elasped:.2f}, 비밀번호: {password}')


def multi_process(stop_process_event: EventClass):
    num_cores = multiprocessing.cpu_count()

    processes: list[Process] = []
    count: Synchronized[int] = Value('i', 0)
    for i in range(num_cores):
        p = multiprocessing.Process(target=unlock_zip, args=(count, stop_process_event,))
        processes.append(p)
        p.start()

    return processes


def main():
    try:
        # unlock_zip()

        stop_process_event = multiprocessing.Event()
        processes = multi_process(stop_process_event)

        while True:
            time.sleep(0.2)

    except KeyboardInterrupt:
        print('\n시스템 종료\n')
    except Exception as e:
        print(f'[ERROR]: {e}')
        print(f'{e.__class__}')
    finally:
        stop_process_event.set()
        for p in processes:
            p.join(timeout=TIME_OUT)
        for p in processes:
            if p.is_alive():
                p.terminate()
        for p in processes:
            p.join()


if __name__ == '__main__':
    try:
        ctx = multiprocessing.get_context('spawn')

        count: Synchronized[int] = ctx.Value('i', 0)
        stop_event: EventClass = ctx.Event()

        procs: list[Process] = [
            ctx.Process(target=unlock_zip, args=(count, stop_event))
            for _ in range(ctx.cpu_count())
        ]

        for p in procs: p.start()

        while True:
            if stop_event.wait(0.2):
                break

    except KeyboardInterrupt:
        print('\n메인 프로세스 종료\n')
    finally:
        stop_event.set()
        for p in procs: p.join()

