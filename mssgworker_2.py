import mangsang_setting as ms
import mssgprocessor as proc

# 기초 데이터 PARSING
DATASET = ms.dataset()
#폐기
DATASET['USER_NO'] = '00'
DATASET['PIN_PONG_1'] = '00'  # 최종 유저
DATASET['PIN_PONG_2'] = '00'  # 최종 유저
    
# 시스템 설정 최소 값 1
DATASET['BOT_NUMBER'] = 10

# 감시모드 설정
DATASET['PROXY'] = False  # 실시간 가능 리스트 적용 유무

# 사용자 설정 USER_NO : 최종예약자
DATASET['CUSTOMER'] = '07'
DATASET['HOLDER'] = '03'

# 숙박 설정
DATASET['SELECT_DATE'] = ['2025-10-09']    # 지정일 기준 * 연박 ex) 2025-08-14 + 2박 => 2025-08-14 ~ 2025-08-16
DATASET['PERIOD'] = ['3']  # 연박 수
# 01:든바다, 02:난바다, 03:허허바다, 04:전통한옥, 05:캐라반, 06:자동차야영장, 07:글램핑A 08:글램핑B, 09:캐빈하우스
DATASET['ROOM_FACILITY'] = ['02']
# 바다 숙소 : 인실정보 적용 2인실, 4인실, 6인실, 8인실, 10인실  없을 경우 PASS 자동차야영장 등등은 없음.
# 한옥 : 인실정보 적용 2인실, 4인실, 6인실
DATASET['ROOM_RANGE'] = ['4', '6', '8', '10']
# 선호 방 번호 (선호 대상이 없을 경우 그 외 대상을 선택하도록 함)
#['ROOM_WANTS'] = ['101', '109', '115']
DATASET['ROOM_WANTS'] = []

#사용하지 않음
DATASET['ROOM_EXPT'] = []

if 1 < len(DATASET['ROOM_WANTS']) == 0:
    print('CHECK ROOM_WANTS')
    exit()
if 1 < len(DATASET['ROOM_RANGE']) == 0:
    print('CHECK ROOM_RANGE')
    exit()
if 1 < len(DATASET['ROOM_FACILITY']) == 0:
    print('CHECK ROOM_FACILITY')
    exit()
if 1 < len(DATASET['SELECT_DATE']) == 0:
    print('CHECK SELECT_DATE')
    exit()
if 1 < len(DATASET['PERIOD']) == 0:
    print('CHECK PERIOD')
    exit()

if DATASET['CUSTOMER'] == '':
    print('CHECK CUSTOMER')
    exit()
if DATASET['HOLDER'] == '':
    print('CHECK HOLDER')
    exit()


proc.worker(DATASET)