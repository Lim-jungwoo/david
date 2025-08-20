import pickle

DATA_BASE = '../data/Mars_Base_Inventory_list.csv'
FLAMMABILITY = 'Flammability'
FLAMMABILITY_THRESHOLD = 0.7

OUTPUT_CSV = 'output/Mars_Base_Inventory_danger.csv'
OUTPUT_BIN = 'output/Mars_Base_Inventory_List.bin'


def parse_csv(path: str) -> list[list[str]]:
    with open(path, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split(',')
        header = [h.strip() for h in header]

        data: list[list[str]] = []
        data.append(header)
        for lineno, line in enumerate(f, start=2):
            line = line.strip()
            if not line:
                continue
            values = line.split(',')
            values = [v.strip() for v in values]
            if len(values) != len(header):
                raise ValueError(f'{lineno}번째 {line}의 값이 잘못되었습니다.')

            data.append(values)

    return data


def sort_data(data: list[list[str]], key: str) -> list[list[str]]:
    if not data:
        raise ValueError('데이터가 비어 있습니다.')

    header = data[0]
    if key not in header:
        raise ValueError(f'헤더에 {key}가 존재하지 않습니다.')

    key_index = header.index(key)

    sorted_data = sorted(data[1:], key=lambda x: float(
        x[key_index]), reverse=True)
    sorted_data.insert(0, header)

    return sorted_data


def filter_data(data: list[list[str]], key: str, threshold: float) -> list[list[str]]:
    if not data:
        raise ValueError('데이터가 비어 있습니다.')

    header = data[0]
    if key not in header:
        raise ValueError(f'헤더에 {key}가 존재하지 않습니다.')

    key_index = header.index(key)

    filtered_data = [row for row in data[1:]
                     if float(row[key_index]) >= threshold]
    filtered_data.insert(0, header)

    return filtered_data


def print_data(data: list[list[str]]):
    for row in data:
        print(', '.join(map(str, row)))


def save_csv(data: list[list[str]], path: str):
    with open(path, 'w', encoding='utf-8') as f:
        for row in data:
            f.write(','.join(row) + '\n')
    print(f'\n=========={path}파일이 저장되었습니다=========\n')


def save_bin(data: list[list[str]], path: str):
    float_columns = ['Weight (g/cm³)', 'Specific Gravity', 'Flammability']
    float_index = [data[0].index(col)
                   for col in float_columns if col in data[0]]

    for row in data[1:]:
        for index in float_index:
            try:
                row[index] = float(row[index])
            except ValueError:
                pass

    with open(path, 'wb') as f:
        pickle.dump(data, f)
    print(f'\n=========={path}파일이 저장되었습니다=========\n')


def load_bin(path: str) -> list[list[str]]:
    with open(path, 'rb') as f:
        data = pickle.load(f)
    return data


def main():
    try:
        data = parse_csv(DATA_BASE)
        sorted_data = sort_data(data, key=FLAMMABILITY)
        filtered_data = filter_data(
            sorted_data, key=FLAMMABILITY, threshold=FLAMMABILITY_THRESHOLD)

        print(f'\n========인화성 지수가 {FLAMMABILITY_THRESHOLD}이상인 데이터 출력=======\n')
        print_data(filtered_data)

        save_csv(filtered_data, path=OUTPUT_CSV)

        save_bin(sorted_data, path=OUTPUT_BIN)
        loaded_data = load_bin(path=OUTPUT_BIN)
        print(f'\n========{OUTPUT_BIN} 파일에서 데이터 출력=======\n')
        print_data(loaded_data)
    except Exception as e:
        print(f'오류 발생: {e}')


if __name__ == '__main__':
    main()
