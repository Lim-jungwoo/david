import random
from datetime import datetime
import json
import time

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
ENV_AVG_INTERVAL_TIME = 5


class LogEvent:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'
    EXIT = 'EXIT'


class Banner:
    ENV_5S = '5초 환경 정보 출력'
    ENV_5M = '5분 환경 정보 출력'


class Message:
    EXIT = 'System stoped···.'


def random_value(low: float, high: float, digits: int):
    return round(random.uniform(low, high), digits)


def f3(value: float):
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


class MissionComputer:
    env_values: dict[str, float]
    ds: DummySensor
    env_values_list: dict[str, list[float]]
    sensor_interval_time: int
    avg_start_time: float

    def __init__(self):
        self.env_values = {}
        self.ds = DummySensor()
        self.env_values_list = {}
        self.sensor_interval_time = 0
        self.avg_start_time = time.time()

    def get_sensor_data(self, interval: int):
        start_time = time.time()
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


def main():
    try:
        RunComputer = MissionComputer()
        RunComputer.get_sensor_data(ENV_INTERVAL_TIME)

    except KeyboardInterrupt:
        print('\n' + Message.EXIT)
    except Exception as e:
        print_log(LogEvent.ERROR, e)


if __name__ == '__main__':
    main()
