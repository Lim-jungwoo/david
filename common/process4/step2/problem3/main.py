import numpy as np
from collections import defaultdict
from typing import List

FILE1 = '../data/mars_base_main_parts-001.csv'
FILE2 = '../data/mars_base_main_parts-002.csv'
FILE3 = '../data/mars_base_main_parts-003.csv'
SAVE_FILE = 'output/parts_to_work_on.csv'

HEADER = ['parts', 'strength']
BASE_DTYPE = np.dtype([
    (f'{HEADER[0]}', 'U32'),
    (f'{HEADER[1]}', 'f4')
])
MERGED_DTYPE = np.dtype([
    (f'{HEADER[0]}', 'U32'),
    (f'{HEADER[1]}', object)
])


def read_csv(file_path: str) -> np.ndarray:
    data = np.genfromtxt(
        file_path,
        delimiter=',',
        dtype=BASE_DTYPE,
        encoding='utf-8',
        skip_header=1
    )
    # genfromtxt가 한 줄만 있으면 shape이 (,)로 나오는 경우 방지
    if data.ndim == 0:
        data = np.array([data], dtype=BASE_DTYPE)

    return data


def save_csv(file_path: str, ndarray: np.ndarray):
    np.savetxt(file_path, ndarray, delimiter=',',
               header=f'{HEADER[0]},{HEADER[1]}', fmt=['%s', '%.3f'], comments='')
    print_banner(f'{file_path} 파일 저장 완료')


def merge_ndarray(ndarray_list: list[np.ndarray]) -> np.ndarray:
    if not ndarray_list:
        raise ValueError('병합할 데이터가 없습니다.')

    parts_dict: dict[str, list[int]] = defaultdict(list)
    for i, ndarray in enumerate(ndarray_list, start=1):
        if ndarray.dtype != BASE_DTYPE:
            raise ValueError(f'{i}번째 데이터의 dtype이 다릅니다.')

        parts = ndarray[f'{HEADER[0]}']
        strengths = ndarray[f'{HEADER[1]}']

        for p, s in zip(parts, strengths):
            parts_dict[str(p)].append(int(s))

    merged_ndarray = np.array(list(parts_dict.items()), dtype=MERGED_DTYPE)
    return merged_ndarray


def calculate_mean(ndarray: np.ndarray) -> np.ndarray:
    parts = []
    strengths = []
    for part, strength in ndarray:
        strength_mean = round(np.mean(strength), 3)
        parts.append(part)
        strengths.append(strength_mean)

    result_ndarray = np.array(list(zip(parts, strengths)), dtype=BASE_DTYPE)
    return result_ndarray


def filter_by_mean(ndarray: np.ndarray, mean: float) -> np.ndarray:
    return ndarray[ndarray[f'{HEADER[1]}'] < mean]


def sort_ndarray(ndarray: np.ndarray) -> np.ndarray:
    return np.sort(ndarray, order=f'{HEADER[1]}')


def f3(value: float) -> str:
    '''소수점 셋째 자리까지 반올림하여 문자열로 반환'''
    return f'{value:.3f}'


def s30(line: str) -> str:
    '''30자까지 공백으로 채움'''
    return f'{line:30s}'


def print_banner(line: str):
    print('\n' + '=' * 10 + f'{line}' + '=' * 10 + '\n')


def print_header():
    print(f'{s30(HEADER[0])} {HEADER[1]}')
    print('-' * 40)


def print_ndarray(ndarray: np.ndarray):
    for part, strength in ndarray:
        print(f'{s30(part)} {f3(strength)}')


def print_object(ndarray: np.ndarray):
    formatted_rows = []
    for row in ndarray:
        formatted_row = []
        for val in row:
            try:
                num = float(val)
                formatted_row.append(f3(num))
            except ValueError:
                formatted_row.append(val)
        formatted_rows.append(formatted_row)
    print(np.array(formatted_rows, dtype=object))


def main():
    try:
        file1 = read_csv(FILE1)
        file2 = read_csv(FILE2)
        file3 = read_csv(FILE3)

        parts = merge_ndarray([file1, file2, file3])
        mean_data = calculate_mean(parts)
        sort_mean_data = sort_ndarray(mean_data)
        formatted_sort_mean_data = np.array(
            sort_mean_data.tolist(), dtype=object)
        print_banner('정렬된 평균 데이터 출력')
        print_header()
        print_ndarray(formatted_sort_mean_data)

        mean = 50
        print_banner(f'평균이 {mean} 미만인 데이터 출력')
        print_header()
        filtered_data = filter_by_mean(sort_mean_data, mean=mean)
        formatted_filtered_data = np.array(
            filtered_data.tolist(), dtype=object)
        print_ndarray(formatted_filtered_data)
        save_csv(SAVE_FILE, filtered_data)

        parts2 = read_csv(SAVE_FILE)
        parts2 = parts2.tolist()
        parts2 = np.array(parts2, dtype=object)
        parts3 = parts2.T

        print_ndarray(parts2)
        print_object(parts3)

    except Exception as e:
        print(f'[ERROR] {e}')


if __name__ == '__main__':
    main()
