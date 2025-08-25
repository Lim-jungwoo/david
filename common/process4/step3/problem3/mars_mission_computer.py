import random
from datetime import datetime
import json
import time
import platform
import os
import psutil

SETTING = None

ENV_KEYS = [
    'mars_base_internal_temperature',
    'mars_base_external_temperature',
    'mars_base_internal_humidity',
    'mars_base_external_illuminance',
    'mars_base_internal_co2',
    'mars_base_internal_oxygen'
]
ENV_RANGES = [
    (18, 30),
    (0, 21),
    (50, 60),
    (500, 715),
    (0.02, 0.1),
    (4, 7),
]
DUMMY_SENSOR_LOG_FILE = 'logs/dummy_sensor_log.log'

ENV_INTERVAL_TIME = 5
ENV_AVG_INTERVAL_TIME = 1

SETTING_FILE_PATH = 'setting.txt'


class LogEvent:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'
    EXIT = 'EXIT'


class Banner:
    ENV_5S = '5초 환경 정보 출력'
    ENV_5M = '5분 환경 정보 출력'
    SYSTEM_INFO = '시스템 정보 출력'
    SYSTEM_INFO_ERROR = '시스템 정보 에러'
    SYSTEM_LOAD = '시스템 사용량 출력'
    SYSTEM_LOAD_ERROR = '시스템 사용량 에러'
    SETTING_PARSING_ERROR = 'setting.txt 파일 파싱 에러'


class Message:
    EXIT = 'System stoped···.'


class SystemConfiguration:
    SC_PAGE_SIZE = 'SC_PAGE_SIZE'
    SC_PHYS_PAGES = 'SC_PHYS_PAGES'


def random_value(low: float, high: float, digits: int):
    return round(random.uniform(low, high), digits)


def f3(value: float | str):
    try:
        value = float(value)
    except Exception:
        return value
    return f'{value:.3f}'


def print_env(env: dict):
    for key, value in env.items():
        print(f'{key} -> {f3(value)}')


def print_log(event: str, log: str):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{now}] {event}: {log}')


def print_banner(banner: str):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print('\n' + '=' * 10 + f' {banner} ({now}) ' + '=' * 10 + '\n')


def print_dict_to_json(banner: str, data: dict):
    print_banner(banner)
    json_data = '{\n'
    for key, value in data.items():
        json_data += f'    \"{key}\": {str(f3(value))},\n'
    json_data = json_data[:-2]
    json_data += '\n}'
    print(json_data)

    json.loads(json_data)


def minute_to_second(minute: int):
    return minute * 60


def calculate_average(values: list[float]):
    if not values:
        return None
    return sum(values) / len(values)


def bytes_to_gb(value: float):
    if not value:
        return None
    return value / (1024 ** 3)


def is_str_bool(value: str):
    if value.lower() == 'true':
        return True
    if value.lower() == 'false':
        return False
    raise ValueError(Banner.SETTING_PARSING_ERROR)


class Setting:
    def __init__(self, path: str):
        self.fields: dict[str, bool] = {}
        self.load_setting(path)

    def load_setting(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        header = [h.strip().lower() for h in lines[0].strip().split(',')]
        for i, line in enumerate(lines):
            if i == 0:
                continue

            parts = [p.strip() for p in line.strip().split(',')]
            if len(header) != len(parts):
                raise ValueError(Banner.SETTING_PARSING_ERROR)

            field = parts[0].lower()
            enabled = is_str_bool(parts[1])

            self.fields.setdefault(field, enabled)

        return self.fields


class DummySensor:
    env_values: dict[str, float]

    def set_env(self):
        self.env_values = {
            key: random_value(low, high, 3) for key, (low, high) in zip(ENV_KEYS, ENV_RANGES)
        }

    def get_env(self):
        self.save_log(DUMMY_SENSOR_LOG_FILE)
        return self.env_values

    def save_log(self, file_path: str):
        with open(file_path, 'a', encoding='utf-8') as f:
            now = datetime.now().astimezone().isoformat(timespec='seconds')
            f.write(f'[{now}] {str(self.env_values)}\n')
        print_log(LogEvent.INFO, f'file saved -> {file_path}')


class SystemInfo:
    os_name = platform.system()
    os_version = platform.version()
    '''
    - 유닉스 커널 버전 메이저.마이너.패치
    - 커널이 빌드된 시간
    - 커널의 소스 트리/리비전 식별자(XNU 소스 버전 태그)
    - 빌드 타입: RELEASE(일반 사용자용 릴리스 빌드)
    - 아키텍쳐: ARM64(Apple Silicon 64비트 ARM)
    - 하드웨어 태그: T6031
    '''
    os_version1 = platform.mac_ver()
    '''
    - macOS 릴리스 버전
    - versioninfo - (version, dev_stage, non_release_version) 사실상 사용 안됨
    - 머신 아키텍쳐 - Apple Silicon은 arm64, intel은 x86_64
    '''
    cpu_type = platform.machine()
    '''
    머신 아키텍쳐
    '''
    cpu_type1 = platform.processor()
    '''
    프로세서 설명 문자열, 플랫폼마다 제각각이라 신뢰성이 낮다
    '''
    cpu_core = os.cpu_count()
    sc_page_size = os.sysconf(SystemConfiguration.SC_PAGE_SIZE)
    '''
    가상 메모리의 페이지 크기, 보통 4096바이트
    '''
    sc_phys_pages = os.sysconf(SystemConfiguration.SC_PHYS_PAGES)
    '''
    가상 메모리의 페이지 개수
    '''
    memory_gb = bytes_to_gb(sc_page_size * sc_phys_pages)
    '''
    총 메모리의 크기(단위 gb)
    '''


class SystemLoad:
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    '''
    - total: 총 메모리
    - available: 즉시 사용 가능한 메모리
    - percent: 사용 중인 비율
    - used: 사용 중인 메모리
    - free: 완전히 free 상태인 메모리
    - active: 활성 메모리(최근에 쓰여서 빨리 다시 쓸 수 있는 메모리)
    - inactive: 비활성 메모리(캐시로 잡혀있지만 필요하면 반환 가능한 메모리)
    - wired: 커널이 반드시 유지해야 하는 고정 메모리
    '''
    memory_usage = memory.percent
    memory_used_gb = bytes_to_gb(memory.used)
    memory_total_gb = bytes_to_gb(memory.total)


def tuple_to_json(value):
    if isinstance(value, tuple) or isinstance(value, list):
        return '[' + ', '.join(tuple_to_json(v) for v in value) + ']'
    elif isinstance(value, str):
        return f'"{value}"'
    elif value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def print_system_info_to_json(banner: str):
    print_banner(banner)
    json_data = '{\n'
    for key, value in SystemInfo.__dict__.items():
        if key.startswith('_') or key not in SETTING.fields or not SETTING.fields.get(key):
            continue
        json_data += f'    \"{key}\": {tuple_to_json(f3(value))},\n'
    if json_data != '{\n':
        json_data = json_data[:-2]
    json_data += '\n}'
    print(json_data)

    json.loads(json_data)


def print_system_load_to_json(banner: str):
    print_banner(banner)
    json_data = '{\n'
    for key, value in SystemLoad.__dict__.items():
        if key.startswith('_') or key not in SETTING.fields or not SETTING.fields.get(key):
            continue
        json_data += f'    \"{key}\": {tuple_to_json(f3(value))},\n'

    if json_data != '{\n':
        json_data = json_data[:-2]
    json_data += '\n}'
    print(json_data)

    json.loads(json_data)


class MissionComputer:
    env_values: dict[str, float]
    ds: DummySensor
    env_values_list: dict[str, list[float]]
    sensor_interval_time: int
    avg_start_time: float
    system_info: SystemInfo
    system_load: SystemLoad

    def __init__(self):
        self.env_values = {}
        self.ds = DummySensor()
        self.env_values_list = {}
        self.sensor_interval_time = 0
        self.avg_start_time = time.time()

        try:
            self.system_info = SystemInfo()
        except Exception:
            print_banner(Banner.SYSTEM_INFO_ERROR)
        try:
            self.system_load = SystemLoad()
        except Exception:
            print_banner(Banner.SYSTEM_LOAD_ERROR)

    def get_sensor_data(self, interval: int):
        next_run = time.time()
        self.sensor_interval_time = interval

        while True:
            self.ds.set_env()
            self.env_values = self.ds.get_env()
            print_dict_to_json(Banner.ENV_5S, self.env_values)

            self.calculate_env_average(ENV_AVG_INTERVAL_TIME)

            next_run += self.sensor_interval_time
            sleep_time = max(0, next_run - time.time())
            time.sleep(sleep_time)

    def save_env_values(self):
        if not self.env_values_list:
            for key, value in self.env_values.items():
                self.env_values_list.setdefault(key, []).append(value)
        else:
            for key, value in self.env_values.items():
                self.env_values_list[key].append(value)

    def calculate_env_average(self, period: int):
        self.save_env_values()
        period = minute_to_second(period)

        now = time.time()

        # test
        # period = 10

        if period <= now - self.avg_start_time:
            avg_env_values: dict[str, float] = {}
            for key, values in self.env_values_list.items():
                avg = calculate_average(values)
                avg_env_values.setdefault(key, avg)

            print_dict_to_json(Banner.ENV_5M, avg_env_values)
            self.env_values_list.clear()

            self.avg_start_time += period
            while now - self.avg_start_time >= period:
                self.avg_start_time += period

    def get_mission_computer_info(self):
        if not self.system_info:
            try:
                self.system_info = SystemInfo()
            except Exception:
                print_banner(Banner.SYSTEM_INFO_ERROR)
                return
        print_system_info_to_json(Banner.SYSTEM_INFO)

    def get_mission_computer_load(self):
        if not self.system_load:
            try:
                self.system_load = SystemLoad()
            except Exception:
                print_banner(Banner.SYSTEM_LOAD_ERROR)
                return
        print_system_load_to_json(Banner.SYSTEM_LOAD)


def main():
    try:
        # ds = DummySensor()
        # ds.set_env()
        # env = ds.get_env()

        runComputer = MissionComputer()
        global SETTING
        SETTING = Setting(SETTING_FILE_PATH)

        runComputer.get_mission_computer_info()
        runComputer.get_mission_computer_load()

    except KeyboardInterrupt:
        print('\n' + Message.EXIT)
    except Exception as e:
        print_log(LogEvent.ERROR, e)
        print(e.__class__)


if __name__ == '__main__':
    main()
