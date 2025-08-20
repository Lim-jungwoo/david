import math
import signal
import sys


MARS_GRAVITY = 0.38

MATERIAL_DENSITY = {
    'glass': 2.4,
    'aluminum': 2.7,
    'carbon_steel': 7.85
}
'''
재료별 밀도 (g/cm^3)

- 유리 (glass): 2.4 g/cm^3
- 알루미늄 (aluminum): 2.7 g/cm^3
- 탄소강 (carbon_steel): 7.85 g/cm^3
'''
MATERIAL_KR_TO_EN_DICTIONARY = {
    '유리': 'glass',
    '알루미늄': 'aluminum',
    '탄소강': 'carbon_steel'
}
MATERIAL_EN_TO_KR_DICTIONARY = {
    'glass': '유리',
    'aluminum': '알루미늄',
    'carbon_steel': '탄소강'
}

EXIT_COMMAND = ['exit', 'quit', 'q', '종료', '끝내기']


def is_valid_number(value: str) -> bool:
    invalid_values = ['inf', '-inf', 'nan']

    if value.lower() in invalid_values:
        return False

    try:
        float(value)
    except ValueError:
        return False

    return True


def is_valid_diameter(diameter: str) -> bool:
    if not is_valid_number(diameter) or float(diameter) <= 0:
        return False
    return True


def is_valid_material(material: str) -> bool:
    return MATERIAL_KR_TO_EN_DICTIONARY.get(material) or MATERIAL_EN_TO_KR_DICTIONARY.get(material)


def is_valid_thickness(thickness: str) -> bool:
    if not is_valid_number(thickness) or float(thickness) <= 0:
        return False
    return True


def calculate_half_outer_surface_area(diameter: float) -> float:
    radius = diameter / 2
    outer_surface_area = (4 * math.pi * ((radius) ** 2)) / 2
    return outer_surface_area


def calculate_half_volume(diameter: float, thickness: float) -> float:
    'diameter, thickness는 m 단위로 입력받음'

    outer_volume = ((4/3) * math.pi * ((diameter / 2) ** 3)) / 2
    inner_volume = ((4/3) * math.pi * (((diameter / 2) - thickness) ** 3)) / 2
    half_volume = outer_volume - inner_volume
    return half_volume


def calculate_half_weight(diameter: float, thickness: float, material: str) -> float:
    'diameter, thickness는 m 단위로 입력받음'

    density = MATERIAL_DENSITY[material]

    half_volume = calculate_half_volume(diameter, thickness)
    half_weight = half_volume * density
    return half_weight


def calculate_mars_weight(weight: float) -> float:
    return weight * MARS_GRAVITY


def sphere_area(diameter: float, material: str, thickness: float) -> {float, float}:
    'diameter, thickness는 m 단위로 입력받음'

    outer_surface_area = calculate_half_outer_surface_area(diameter)
    half_weight = calculate_half_weight(diameter, thickness, material)
    mars_half_weight = calculate_mars_weight(half_weight)

    return outer_surface_area, mars_half_weight


def f3(value: float) -> str:
    '''소수점 셋째 자리까지 반올림하여 문자열로 반환'''
    return f'{value:.3f}'


def is_exit_command(command: str) -> bool:
    '''종료 명령어인지 확인'''
    return command.lower() in EXIT_COMMAND


def signal_handler(sig, frame):
    print('\n프로그램을 종료합니다.')
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C 시 종료 핸들러 설정
    while True:
        diameter = input('지름(diameter)를 입력하세요 (단위 m): ')
        if is_exit_command(diameter):
            print('프로그램을 종료합니다.')
            break
        if not is_valid_diameter(diameter):
            print('\n지름(diameter)는 0보다 큰 숫자여야 합니다.\n')
            continue
        diameter = float(diameter)

        print('\n')
        material = input(
            '재료(material)를 입력하세요 (유리(glass), 알루미늄(aluminum), 탄소강(carbon_steel)): ')
        if is_exit_command(material):
            print('프로그램을 종료합니다.')
            break
        if not is_valid_material(material):
            print(
                '\n재료(material)는 유리(glass), 알루미늄(aluminum), 탄소강(carbon_steel) 중 하나여야 합니다.\n')
            continue
        if MATERIAL_KR_TO_EN_DICTIONARY.get(material):
            material = MATERIAL_KR_TO_EN_DICTIONARY[material]

        print('\n')
        thickness = input('두께(thickness)를 입력하세요 (단위 cm): ')
        if is_exit_command(thickness):
            print('프로그램을 종료합니다.')
            break
        if not is_valid_thickness(thickness):
            print('\n두께(thickness)값이 유효하지 않으므로 기본값 1cm로 설정합니다.\n')
            thickness = 1.0
        else:
            thickness = float(thickness)
        thickness /= 100  # cm to m

        try:
            outer_surface_area, mars_half_weight = sphere_area(
                diameter, material, thickness)
            material_kr = MATERIAL_EN_TO_KR_DICTIONARY[material]
            print(f'재질 => {material_kr}, 지름 => {f3(diameter)}, 두께 => {f3(thickness * 100)}, 면적 => {f3(outer_surface_area)}, 무게 => {f3(mars_half_weight)}kg')
        except Exception as e:
            print(f'오류 발생: {e}')
            continue


if __name__ == '__main__':
    main()
