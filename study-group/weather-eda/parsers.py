import pandas as pd
import os
from pathlib import Path
from io import StringIO
from constants import *

DATA_DIR = Path('data')
GANGNEUNG_NUMBER_OF_DAYS_WITH_PRECIPITATION_CSV = 'gangneung_days_with_precipitation.csv'
GANGNEUNG_PRECIPITATION_CSV = 'gangneung_precipitation.csv'
GANGNEUNG_RAINY_SEASON_CSV = 'gangneung_rainy_season.csv'
GANGNEUNG_TEMPERATURE_CSV = 'gangneung_temperature.csv'

ENCODING = 'euc-kr'

GANGNEUNG_NUMBER_OF_DAYS_WITH_PRECIPITATION_SKIP_ROWS = 5
GANGNEUNG_PRECIPITATION_SKIP_ROWS = 7
GANGNEUNG_RAINY_SEASON_SKIP_ROWS = 2
GANGNEUNG_TEMPERATURE_SKIP_ROWS = 7


def strip_string(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    ''''''
    out = df if inplace else df.copy()
    obj = out.select_dtypes(include=['object', 'string'])
    out[obj.columns] = obj.apply(lambda s: s.str.strip())
    return out


def _read_section(lines):
    '''섹션 라인 리스트 -> DataFrame으로 변환'''
    # 위/아래 빈줄 제거
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        raise ValueError('섹션에 데이터가 없습니다.')
    
    buf = StringIO(''.join(lines))

    df = pd.read_csv(buf)
    return df


def load_precip_days(
        file_name: str = GANGNEUNG_NUMBER_OF_DAYS_WITH_PRECIPITATION_CSV,
        encoding: str = ENCODING,
        skiprows: int = GANGNEUNG_PRECIPITATION_SKIP_ROWS,
        header: int = 0) -> pd.DataFrame:
    '''
    강릉 강수일수 CSV 파싱
    - return df[평균 강수일수, 평균 계절별 강수일수, 강수일수 관측값]
    '''
    path = DATA_DIR / file_name

    with open(path, encoding=encoding) as f:
        lines = f.readlines()

    sections = {
        AVG_DAYS_PRECIP_EN: [],          # 평균 강수일수
        AVG_SEASON_PRECIP_EN: [],        # 평균 계절별 강수일수
        PRECIP_DAYS_OBSERVATION_EN: [],  # 강수일수 관측값
    }
    current = None

    for raw in lines:
        s = raw.strip()

        # 섹션 헤더 감지
        if s.startswith(AVG_DAYS_PRECIP_KR):
            current = AVG_DAYS_PRECIP_EN
            continue
        if s.startswith(AVG_SEASON_PRECIP_KR):
            current = AVG_SEASON_PRECIP_EN
            continue
        if s.startswith(PRECIP_DAYS_OBSERVATION_KR):
            current = PRECIP_DAYS_OBSERVATION_EN
            continue

        # 현재 섹션에 라인 누적
        if current:
            sections[current].append(raw)

    # 섹션별 DataFrame 생성
    avg_days_precip_df = _read_section(sections[AVG_DAYS_PRECIP_EN])
    avg_season_precip_df = _read_section(sections[AVG_SEASON_PRECIP_EN])
    precip_days_observation_df = _read_section(sections[PRECIP_DAYS_OBSERVATION_EN])

    # 컬럼 표준화
    avg_days_precip_df = avg_days_precip_df.rename(columns=COLUMN_MAP)
    avg_season_precip_df = avg_season_precip_df.rename(columns=COLUMN_MAP)
    precip_days_observation_df = precip_days_observation_df.rename(columns=COLUMN_MAP)

    # 문자열 공백 제거
    strip_string(avg_days_precip_df, True)
    strip_string(avg_season_precip_df, True)
    strip_string(precip_days_observation_df, True)

    return [avg_days_precip_df, avg_season_precip_df, precip_days_observation_df]


def load_precip_amount(file_name: str = GANGNEUNG_PRECIPITATION_CSV, encoding: str = ENCODING, skiprows: int = GANGNEUNG_PRECIPITATION_SKIP_ROWS, header: int = 0) -> pd.DataFrame:
    '''
    강수량 CSV 파싱
    '''
    path = DATA_DIR / file_name
    df = pd.read_csv(path, encoding=encoding, skiprows=skiprows, header=header)
    df = df.rename(columns=COLUMN_MAP)
    strip_string(df, True)
    return df


def load_rainy_season(file_name: str = GANGNEUNG_RAINY_SEASON_CSV, encoding: str = ENCODING, skiprows: int = GANGNEUNG_RAINY_SEASON_SKIP_ROWS, header: int = 0) -> pd.DataFrame:
    '''
    장마 CSV 파싱
    '''
    path = DATA_DIR / file_name
    df = pd.read_csv(path, encoding=encoding, skiprows=skiprows, header=header)
    df = df.rename(columns=COLUMN_MAP)
    strip_string(df, True)
    return df


def load_temperature(file_name: str = GANGNEUNG_TEMPERATURE_CSV, encoding: str = ENCODING, skiprows: int = GANGNEUNG_TEMPERATURE_SKIP_ROWS, header: int = 0) -> pd.DataFrame:
    '''
    온도 CSV 파싱
    '''
    path = DATA_DIR / file_name
    df = pd.read_csv(path, encoding=encoding, skiprows=skiprows, header=header)
    df = df.rename(columns=COLUMN_MAP)
    strip_string(df, True)
    return df

avg_precip_days, avg_season_precip, precip_days_observation = load_precip_days()
precip_amount = load_precip_amount()
rainy_season = load_rainy_season()
temperature = load_temperature()

print(avg_precip_days.head())
print(avg_season_precip.head())
print(precip_days_observation.head())
print(precip_amount.head())
print(rainy_season.head())
print(temperature.head())