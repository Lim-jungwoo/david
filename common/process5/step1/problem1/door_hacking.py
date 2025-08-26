# from zipfile import ZipFile, BadZipFile
import pyzipper
import zlib
import time
from datetime import datetime
import multiprocessing

# ZIP_PATH = 'emergency_storage_key.zip'
ZIP_PATH = 'test.zip'
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

    # for i in range(length, 0, -1):
    #     if i == 1:
    #         password += CHARSET[count % len(CHARSET)]
    #     else:
    #         index = (int)(count / (len(CHARSET) ** (i - 1)))
    #         if index >= len(CHARSET):
    #             index %= len(CHARSET)
    #         password += CHARSET[index]


def unlock_zip():
    count = 0
    start_time = time.time()
    last_report = start_time
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        while count < LIMIT:
            password = make_password(count, PASSWORD_LENGTH)
            count += 1
            # if password == TEST_PASSWORD:
            #     break

            now = time.time()
            if now - last_report >= 1:
                elasped = now - start_time
                print(f'시작 시간: {started_at} | 진행 시간: {elasped:8.2f}s | 반복 횟수: {count:12d} | 비밀번호: {password:6s}')
                last_report = now

            try:
                with pyzipper.AESZipFile(ZIP_PATH) as zf:
                    zf.pwd = password.encode('utf-8')
                    zf.extractall(EXTRACT_PATH)

                with open(PASSWORD_PATH, 'w', encoding='utf-8') as f:
                    f.write(password)
                break
            except (RuntimeError, pyzipper.BadZipFile, zlib.error):
                continue
    except KeyboardInterrupt:
        print('\n시스템 종료\n')
        exit(0)

    total_elasped = time.time() - start_time
    print(f'\n종료: 반복횟수: {count}, 진행 시간: {total_elasped:.2f}, 비밀번호: {password}')


def multi_process(stop_process_event: multiprocessing.context.BaseContext.Event):
    num_cores = multiprocessing.cpu_count()

    processes = []
    # for i in range(num_cores):
        # p = multiprocessing.Process(target=worker, args=(i,))
        # processes.append(p)
        # p.start()

    for p in processes:
        p.join(timeout=TIME_OUT)
    for p in processes:
        if p.is_alive():
            p.terminate()
    for p in processes:
        p.join()


def main():
    try:
        unlock_zip()
    # except KeyboardInterrupt:
    #     print('\n시스템 종료\n')
    except Exception as e:
        print(f'[ERROR]: {e}')
        print(f'{e.__class__}')


if __name__ == '__main__':
    main()