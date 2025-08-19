from datetime import datetime
import json


def load_logs(path='mission_computer_main.log') -> list:
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        raise ValueError('파일이 비어 있습니다.')

    header = lines[0].strip().split(',')
    required_columns = ['timestamp', 'event', 'message']
    if not all(col in header for col in required_columns):
        raise ValueError(f'파일에 필요한 컬럼이 없습니다: {header}')

    idx_map = {col: header.index(col) for col in required_columns}

    logs = []
    for lineno, line in enumerate(lines[1:], start=2):
        parts = line.strip().split(',')

        if len(parts) < len(header):
            raise ValueError(f'파일의 {lineno}번째 줄에 컬럼이 부족합니다: {parts}')

        timestamp_raw = parts[idx_map['timestamp']].strip()
        event_raw = parts[idx_map['event']].strip()
        message_raw = parts[idx_map['message']].strip()

        try:
            timestamp = datetime.strptime(timestamp_raw, '%Y-%m-%d %H:%M:%S')
        except Exception:
            raise ValueError(
                f'파일의 {lineno}번째 줄에 잘못된 날짜 형식이 있습니다: {timestamp_raw}')

        if not event_raw.isupper():
            raise ValueError(
                f'파일의 {lineno}번째 줄에 잘못된 이벤트 형식이 있습니다: {event_raw}')

        logs.append((timestamp, event_raw, message_raw))

    return logs


def print_banner(text: str, width: int = 30) -> None:
    print('\n' + '*' * width)
    print('*' * width)
    print(text.center(width))
    print('*' * width)
    print('*' * width + '\n')


def main():
    path = 'mission_computer_main.log'
    try:
        logs = load_logs(path)

        print('\n=======로그 파일 출력=======\n')
        for timestamp, event, log in logs:
            print(f'{timestamp} - {event}: {log}')

        print('\n\n=======로그 파일 시간 역순 출력=======\n')
        sorted_logs = sorted(logs, key=lambda x: x[0], reverse=True)
        for timestamp, event, log in sorted_logs:
            print(f'{timestamp} - {event}: {log}')

        sorted_logs_dict = {}
        for idx, (timestamp, event, log) in enumerate(sorted_logs, start=1):
            key = f'{timestamp.strftime('%Y-%m-%d %H:%M:%S')}#{idx}'
            sorted_logs_dict[key] = (event, log)

        print('\n\n=======로그 파일 딕셔너리 형태 출력=======\n')
        for timestamp, (event, log) in sorted_logs_dict.items():
            print(f'{timestamp} -> ({event}, {log})')

        with open('mission_computer_main.json', 'w', encoding='utf-8') as f:
            json.dump(sorted_logs_dict, f, ensure_ascii=False, indent=4)

        print('\n\n=======mission_computer_main.json 파일 저장 완료=======\n')

        print_banner('보너스')

        with open('mission_computer_main.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        lines = lines[1:]
        sorted_lines = sorted(
            lines, key=lambda x: x.split(',')[0], reverse=True)
        print('=======보너스 로그 역순 출력=======\n')
        for line in sorted_lines:
            print(line.strip())

        dangerous_keywords = ['explosion', 'leak', 'spill',
                              'fire', 'hot', 'oxygen', 'unstable', 'powered down']
        dangerous_logs = []
        for line in lines:
            log = line.strip().split(',')[2]
            if any(keyword in log.lower() for keyword in dangerous_keywords):
                dangerous_logs.append(line)

        with open('mission_computer_dangerous.log', 'w', encoding='utf-8') as f:
            for log in dangerous_logs:
                f.write(log)

        print('\n\n=======위험 키워드 포함 로그 mission_computer_dangerous.log 파일 저장 완료=======\n')

        while True:
            user_input = input('\n검색할 문자열을 입력하세요(종료는 exit): ')
            print('\n')
            if user_input.lower() == 'exit':
                print('프로그램을 종료합니다.')
                break

            found_logs = [
                line for line in lines if user_input.lower() in line.lower()]
            if found_logs:
                print(f'검색 결과: {len(found_logs)}개 로그가 발견되었습니다.')
                for log in found_logs:
                    print(log.strip())
            else:
                print('검색 결과가 없습니다.')

    except OSError as e:
        print(f'파일 에러: {e}')
    except ValueError as e:
        print(f'파일 파싱 에러: {e}')


if __name__ == '__main__':
    main()
