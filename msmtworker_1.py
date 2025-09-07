import mangsang_setting as ms
import mangsang_multiprocessing_spot as processor

# 기초 데이터 PARSING
DATASET = ms.dataset()

# 시스템 설정 최소 값 1
DATASET['BOT_NUMBER'] = 1

# 사용자 설정 USER_NO : 최종예약자, PING_PONG_1 = 첫번째 홀더, PING_PONG_2 두번째 홀더
DATASET['USER_NO'] = '06'
DATASET['PIN_PONG_1'] = '00'
DATASET['PIN_PONG_2'] = '01'

# 감시모드 설정
DATASET['PROXY'] = False # 실시간 가능 리스트 적용 유무
DATASET['SHOW_RESERVATION'] = False
DATASET['MULTIPLE_BOT'] = 1
DATASET['USER_RANDOM'] = True
DATASET['ALL_HOLIDAY_SEARCH'] = True    #현재 일 기준 가용가능한 (+30일) 까지 모든 토요일 주말 날짜 취하기
DATASET['SUNDAY_MINUS_DAY_CNT'] = 3    #현재 일 기준 가용가능한 (+30일) 까지 모든 토요일 주말 날짜 취하기
DATASET['GROUP'] = ['A', 'B']
DATASET['OVERWRITE_RESERVATION'] = True    #ACTIVE 그룹에 속한 예약 정보를 전부 갱신 후 다시 등록!! 주의 절때 멈추지 말것


print('프록시 서버 ON -> ' + str(DATASET['PROXY']))
print('예약현황 체크 -> ' + str(DATASET['SHOW_RESERVATION']))
print('다중 봇 사용 -> ' + str(DATASET['MULTIPLE_BOT']))

# 숙박 설정
# ALL DAY SEARCH 시 SELECT DATE 는 OVERWRITE 가 됨
DATASET['SELECT_DATE'] = ['2025-10-07']    # 지정일 기준 * 연박 ex) 2025-08-14 + 2박 => 2025-08-14 ~ 2025-08-16
DATASET['PERIOD'] = ['1']  # 연박 수
# 01:든바다, 02:난바다, 03:허허바다, 04:전통한옥, 05:캐라반, 06:자동차야영장, 07:글램핑A 08:글램핑B, 09:캐빈하우스
DATASET['ROOM_FACILITY'] = ['01', '02', '03']
# 바다 숙소 : 인실정보 적용 2인실, 4인실, 6인실, 8인실, 10인실  없을 경우 PASS 자동차야영장 등등은 없음.
# 한옥 : 인실정보 적용 2인실, 4인실, 6인실
DATASET['ROOM_RANGE'] = ['4', '6', '8', '10']
# 선호 방 번호 (선호 대상이 없을 경우 그 외 대상을 선택하도록 함)
#['ROOM_WANTS'] = ['101', '109', '115']
DATASET['ROOM_WANTS'] = []

# 제외 대상 설정
# 고정 빈방 STATIC
DATASET['ROOM_EXPT'] = ['DG106', 'DC109', 'DD115']

if DATASET['SHOW_RESERVATION']:
    DATASET['ROOM_FACILITY'] = ['01', '02', '03']
    DATASET['ROOM_RANGE'] = ['2', '4', '6', '8', '10']
    DATASET['ROOM_EXPT'] = []


processor.worker(DATASET)