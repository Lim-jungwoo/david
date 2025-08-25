import random
from datetime import datetime

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


class LogEvent:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'


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


class DummySensor:
    env_values: dict

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


def main():
    ds = DummySensor()
    ds.set_env()
    env = ds.get_env()


if __name__ == '__main__':
    main()
