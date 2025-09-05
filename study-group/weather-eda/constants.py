
# 강릉 강수일수 파일
PRECIP_DAYS_YEARLY = ['연도', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월', '연합계', '순위']
PRECIP_DAYS_SEASON = ['연도', '봄(3~5월)', '여름(6~8월)', '가을(9~11월)', '겨울(12~익년2월)']
PRECIP_DAYS_DAILY = ['연도', '날짜', '지점', '관측값']

# 강릉 강수일수 파일 섹션
AVG_DAYS_PRECIP_EN = 'avg_days_precip'
AVG_DAYS_PRECIP_KR = '평균 강수일수'
AVG_SEASON_PRECIP_EN = 'avg_season_precip'
AVG_SEASON_PRECIP_KR = '평균 계절별 강수일수'
PRECIP_DAYS_OBSERVATION_EN = 'precip_days_observation'
PRECIP_DAYS_OBSERVATION_KR = '강수일수 관측값'

# 강릉 강수량 파일
PRECIP_AMOUNT = ['년월', '지점', '강수량(mm)']

# 강릉 장마 파일
RAINY_SEASON = ['지점번호', '지점명', '시작일', '종료일', '장마일수', '강수일수', '합계강수량']

# 강릉 온도 파일
TEMPERATURE = ['년월', '지점', '평균기온(℃)', '평균최저기온(℃)', '평균최고기온(℃)']


# 매핑
COLUMN_MAP = {
    '연도': 'year',
    '1월': 'january',
    '2월': 'february',
    '3월': 'march',
    '4월': 'april',
    '5월': 'may',
    '6월': 'june',
    '7월': 'july',
    '8월': 'august',
    '9월': 'september',
    '10월': 'october',
    '11월': 'november',
    '12월': 'december',
    '연합계': 'total_days',
    '순위': 'rank',
    '봄(3~5월)': 'spring',
    '여름(6~8월)': 'summer',
    '가을(9~11월)': 'fall',
    '겨울(12~익년2월)': 'winter',
    '날짜': 'month_day',
    '지점': 'station_id',
    '관측값': 'observations',
    '년월': 'year_month',
    '강수량(mm)': 'precip_amount',
    '지점번호': 'station_id',
    '지점명': 'station_name',
    '시작일': 'start_date',
    '종료일': 'end_date',
    '장마일수': 'rainy_season_days',
    '강수일수': 'precip_days',
    '합계강수량': 'rainy_season_precip_amount',
    '평균기온(℃)': 'avg_temp',
    '평균최저기온(℃)': 'min_temp',
    '평균최고기온(℃)': 'max_temp'
}
