import sys
import os
import cv2 as cv
import numpy as np
import time
import datetime
import mss
import pyautogui
import winsound
import random
from PIL import ImageGrab,ImageOps, Image
from ppadb.client import Client as AdbClient

client  = AdbClient(host="127.0.0.1", port=5037)

device = client.device("127.0.0.1:5555")

# result = device.screencap()
# with open("screen.png", "wb") as fp:
#     fp.write(result)

# shell input touchscreen swipe 675 1780 1350 1500 3000


# # getting the name of the directory
# # where the this file is present.
# current = os.path.dirname(os.path.realpath(__file__))
# # Getting the parent directory name
# # where the current directory is present.
# parent = os.path.dirname(current)
# # adding the parent directory to
# # the sys.path.
# sys.path.append(parent)
sys.path.append('../..')
# from windowcapture import WindowCapture
from vision import Vision

# monster_1 = Vision('monster1.png')
# monster_2 = Vision('monster2.png')
# monster_3 = Vision('monster3.png')
# monster_4 = Vision('monster4.png')
# guardian = Vision('guardian.png')
monster_all_array = ['monster1.png','monster2.png','monster3.png','monster4.png','guardian.png']
# monster_all = Vision(monster_all_array)
monster_1 = Vision(monster_all_array[0])
monster_2 = Vision(monster_all_array[1])
monster_3 = Vision(monster_all_array[2])
monster_4 = Vision(monster_all_array[3])
guardian = Vision(monster_all_array[4])

my_character = Vision('../../../my_characters/met_chicken3.png')

dead = Vision('dead_3.png')

monitor = {"top": 35, "left": 1596, "width": 921, "height": 518}

# black1 = (2467, 526)
# black2 = (2570, 529)

# 화면전환 감지에 쓰이는 좌표
black1 = (2500, 530) # 오른쪽 하단 구석
black2 = (2501, 531)
inven_icon_1 = (2318, 76) # 인벤토리 아이콘
inven_icon_2 = (2319, 77)

# 마우스로 클릭시 사용되는 좌표
# a = (2244,317)
# s = (2344,317)
# d = (2444,317)
# x = (2444,397)
# c = (2344,477)
# spacebar = (2444,477)

# 모바일로 클릭시 사용되는 좌표
a = "655 277"
s = "746 278"
d = "841 279" 
x =  "842 362" 
c =  "745 444"
spacebar =  "844 444"
control =  "674 431"
shift = "744 359"
# 모바일용 방향키 좌표
up = "130 337"
down = "133 437"
left = "80 385"
right = "182 389"
upRight = "174 342"
upLeft = "90 340"
downRight = "174 435"
downLeft = "88 432"

# 기본공격 횟수
stop_shift_count = 0

# 몬스터 잡은 횟수
monster_count = 0

# 각 스킬들의 시전 시간을 담는 변수들 (스킬 쿨타임 측정)
prev_time = 0
prev_time_1 = 0
prev_time_2 = 0
prev_time_3 = 0 
prev_time_4 = 0
prev_time_5 = 0
prev_time_6 = 0
prev_time_7 = 0

# 프로그램 실행시간 저장
start = str(datetime.datetime.now()).split('.')[0]
start_seconds = time.time()
# 사냥중인지 아닌지 설정하는 변수
battle = False
# 마우스 포인터가 모니터 구석에 위치할시 pyautogui가 작동안되는것 방지
pyautogui.FAILSAFE = False

# 화면전환을 감지하는 함수(사냥터 안이나 밖에서)
def screen_change_grab(): 
    # 오른쪽 하단 구석
    box = (black1[0], black1[1], black2[0], black2[1])
    image = ImageGrab.grab(box)
    grayImage = ImageOps.grayscale(image)
    a = np.array(grayImage.getcolors())
    return a.sum()

# 사냥터에서 화면전환을 감지하는 함수
def screen_change_grab2():
    # 인벤토리 아이콘
    box = (inven_icon_1[0], inven_icon_1[1], inven_icon_2[0], inven_icon_2[1])
    image = ImageGrab.grab(box)
    grayImage = ImageOps.grayscale(image)
    a = np.array(grayImage.getcolors())
    return a.sum()

# 몬스터와 내 캐릭터 사이의 거리계산 함수 (최단거리 버전)
def find_shortest_distance(monster, my):
    # 몬스터좌표와 나의 좌표를 뺀값들을 저장할 변수
    subtracted=[]
    # 뺀 값들을 subtracted 변수에 저장
    for i in range(0,len(monster)):
        # 예시: 몬스터(200, 200) 나(100, 100)
        # 저장값: (100, 100)
        subtracted.append(tuple(np.subtract(monster[i], my[0])))
    subtracted=tuple(subtracted)
    # 모든 몬스터와 나의 직선거리를 저장할 변수
    distance = []
    # 모든 몬스터와 내캐릭터의 직선 거리 계산후 distance 변수에 저장
    for i in range(0, len(subtracted)):
        distance.append(round(np.sqrt(pow(subtracted[i][0], 2) + pow(subtracted[i][1],2))))
    # 최단거리를 찾기위해 기준으로 삼을 첫번째 수치를 shortest_distance변수에 저장        
    shortest_distance = distance[0]
    # 최단거리에 해당하는 인덱스를 저장할 변수 생성
    shortest_distance_idx = 0
    # 최단거리와 인덱스를 찾은후 각 변수에 저장
    for i in range(0, len(distance)):
        if(shortest_distance > distance[i]):
            shortest_distance = distance[i]
            shortest_distance_idx = i
    return shortest_distance, shortest_distance_idx

# 몬스터와 내 캐릭터 사이의 거리계산 함수 (최장거리 버전)
def find_longest_distance(monster, my):
    subtracted=[]
    distance = []
    for i in range(0,len(monster)):
        subtracted.append(tuple(np.subtract(monster[i], my[0])))
    subtracted=tuple(subtracted)
    for i in range(0, len(subtracted)):
        distance.append(round(np.sqrt(pow(subtracted[i][0], 2) + pow(subtracted[i][1],2))))
            
    longest_distance = distance[0]
    longest_distance_idx = 0
    for i in range(0, len(distance)):
        if(longest_distance < distance[i]):
            longest_distance = distance[i]
            longest_distance_idx = i
    return longest_distance, longest_distance_idx

# 어느 방향으로 움직여야할지 결정하는 함수
def moveTo(x_axis, y_axis):
    # print('timer : ', timer)
    if(x_axis < 0):
        direction(heading = 'left', distance = x_axis, )
    if(x_axis > 0):
        direction(heading = 'right', distance = x_axis)
    if(y_axis < 0):
        direction(heading = 'up', distance = y_axis)
    if(y_axis > 0):
        direction(heading = 'down', distance = y_axis)

# 특정 시간동안 움직이게하는 함수
def direction(heading, distance):
    # 캐릭터의 속도를 고려하여 주어진 거리를 몇초간 이동할것인지 계산 
    t = round(abs(distance)/300,1)
    # adb shell 에 입력하기위해 string 으로 변환
    moving_time = str(round(t*1000))
    # 거리가 100 이상일경우
    if abs(distance) > 100:
        # 주어진 방향에 따라 계산된 시간동안 이동
        if heading =="up":
            print('위')
            device.shell("input touchscreen swipe "+up+" "+up+" "+moving_time)
        if heading =="down":
            print('아래')
            device.shell("input touchscreen swipe "+down+" "+down+" "+moving_time)
        if heading =="left":
            print('왼쪽')
            device.shell("input touchscreen swipe "+left+" "+left+" "+moving_time)
        if heading =="right":
            print('오른쪽')
            text = "input touchscreen swipe "+right+" "+right+" "+moving_time
            device.shell(text)
    # 내 캐릭터와 목표지점의 거리가 100 이내일경우
    elif abs(distance) <= 100:
        print('목표지점 도달') 

# 가장 가까운 몬스터의 좌표를 리턴하는 함수
def fight_monsters(monsters_locations, my_location):
    # 가장 가까운 거리에 있는 몬스터의 인덱스를찾아 변수에 저장
    shortest_distance, idx = find_shortest_distance(monsters_locations, my_location)
    # 가장 먼 거리에 있는 몬스터의 인덱스를찾아 변수에 저장
    # longest_distance, idx = find_longest_distance(monsters_locations, my_location)

    # 내 캐릭터와 가장 가까운 몬스터의 좌표를 변수에 저장
    monster = monsters_locations[idx]
    # 진행방향을 알기위해 가장 가까이 있는 몬스터의 위치에서 내 캐릭터의 위치를 뺀다
    subtracted = tuple(np.subtract(monster, my_location[0]))
    return subtracted

# 스킬 시전하는 함수
def start_attack(swap, elapsed_time, prev_time_1, prev_time_2,prev_time_3,prev_time_4, prev_time_5, prev_time_6, prev_time_7, skill_1,skill_2,skill_3,skill_4,skill_5,skill_6):
    # if(swap > 60):
    #     device.shell("input touchscreen tap "+control)
    #     device.shell("input touchscreen tap "+x)
    #     device.shell("input touchscreen tap "+c)
    #     device.shell("input touchscreen tap "+spacebar)
    #     device.shell("input touchscreen tap "+control)
    # #     pyautogui.press('ctrl')
    # #     pyautogui.press('x')
    # #     pyautogui.press('c')
    # #     pyautogui.press('space')
    # #     # pyautogui.click(c)
    # #     # pyautogui.click(spacebar)
    # #     pyautogui.press('ctrl')
    #     prev_time_6 = elapsed_time

    if(skill_1 > 4.2):
        prev_time_1 = elapsed_time
        # pyautogui.click(a)
        device.shell("input touchscreen tap "+a)
    if(skill_2 > 4.2):
        prev_time_2 = elapsed_time
        # pyautogui.click(s)
        device.shell("input touchscreen tap "+s)
    if(skill_3 > 7.2):
        prev_time_3 = elapsed_time
        # pyautogui.click(d)
        device.shell("input touchscreen tap "+d)
    if(skill_6 > 3.2):
        prev_time_7 = elapsed_time
        # pyautogui.click(x)
        device.shell("input touchscreen tap "+x)
    if(skill_4 > 2.2):
        prev_time_4 = elapsed_time
        # pyautogui.click(c)
        device.shell("input touchscreen tap "+c)
    if(skill_5 > 2.7):
        prev_time_5 = elapsed_time
        # pyautogui.click(spacebar)
        device.shell("input touchscreen tap "+spacebar)
    return prev_time_1, prev_time_2,prev_time_3,prev_time_4,prev_time_5,prev_time_6,prev_time_7,swap

# 몬스터나 내 캐릭터가 감지 안됐을시 실행하는 함수
# 2초동안 랜덤한 대각선방향으로 움직이게한다
def move_random():
    print('랜덤 방향으로 이동')
    rand = random.randint(1,4)
    if(round(rand == 1)):
        device.shell("input touchscreen swipe "+upLeft+" "+upLeft+" 2000")
    if(round(rand == 2)):
        device.shell("input touchscreen swipe "+downLeft+" "+downLeft+" 2000")
    if(round(rand == 3)):
        device.shell("input touchscreen swipe "+upRight+" "+upRight+" 2000")
    if(round(rand == 4)):
        device.shell("input touchscreen swipe "+downRight+" "+downRight+" 2000")

with mss.mss() as sct:
    while(True):
        # 현재 시간 저장
        end_seconds = time.time()
        # 프로그램 시작한지 몇초 지났는지 담은 변수
        elapsed_time = round(end_seconds-start_seconds,1)

        ### adb 사용해서 스크린캡쳐하기 ###
        # result = device.screencap()
        # with open("screen.png", "wb") as fp:
        #     # print(fp)
        #     fp.write(result)
        # img = Image.open('screen.png')
        # screenshot = np.array(img)

        # 모니터에서 스크린샷 값을 담은 변수
        screenshot = sct.grab(monitor)
        # 스크린샷의 픽셀값를 담은 array 변수
        screenshot = np.array(screenshot)  
        # 화면전환을 감지 (사냥터에서 나가거나 들어올때)
        change = screen_change_grab()
        # 사냥터에 들어와있는상태
        if battle == True:
            # 기본공격횟수 초기화
            stop_shift_count = 0
            # 사망할때 뜨는 메세지 감지
            death = dead.find_monster(screenshot, 0.8, 'rectangles')
            
            # 사망 메세지가 감지되면 프로그램 종료
            if (len(death) > 0):
                print('사망')
                # 사망시간 기록해서 출력
                # end = datetime.datetime.now().strftime("%H:%M:%S")
                end = str(datetime.datetime.now()).split('.')[0]
                print(start)
                print(end)
                break

            # 사냥터에 들어왔을시 
            if(change == 1): # 화면 우측 하단 구석이 검은색일때
                # 범위 넓은 스킬 두개 시전
                device.shell("input touchscreen tap "+s)
                device.shell("input touchscreen tap "+spacebar)
                # 5가지 종류의 몬스터 감지
                monster_locations_1 = monster_1.find_monster(screenshot, 0.5, 'rectangles')
                monster_locations_2 = monster_2.find_monster(screenshot, 0.5, 'rectangles')
                monster_locations_3 = monster_3.find_monster(screenshot, 0.5, 'rectangles')
                monster_locations_4 = monster_4.find_monster(screenshot, 0.5, 'rectangles')
                guardian_n = guardian.find_monster(screenshot, 0.5, 'rectangles')
                monsters_locations = monster_locations_1+monster_locations_2+monster_locations_3+monster_locations_4+guardian_n
                # 내 캐릭터 감지
                my_location = my_character.find_monster(screenshot, 0.38, 'points')
                # 내 캐릭터와 몬스터가 감지됐을시
                if(len(my_location) > 0 and len(monsters_locations) > 0):
                    # 나의 좌표와 몬스터의 좌표를 뺀 값을 result 변수에 저장
                    result = fight_monsters(monsters_locations, my_location)
                    # 내 캐릭터가 몬스터 방향으로 일정 시간만큼 움직여주게하는 함수
                    moveTo(result[0], result[1])
                    # 기본공격하기
                    device.shell("input touchscreen tap "+shift)
                # 내 캐릭터의 좌표만 감지됐을경우 (몬스터는 아직 사냥터에 남아있는경우)
                elif len(my_location) > 0:
                    print('몬스터 감지안됨')
                    # y axis : 211 is the middle
                    # set it between 208 and 214
                    # 사냥터에서 y축 중앙을 기준으로 나의 캐릭터가 위에 있을경우 아래로 1.2초간 움직이게한다 
                    if my_location[0][1] < 211:
                        device.shell("input touchscreen swipe "+down+" "+down+" 1200")
                    # 사냥터에서 y축 중앙을 기준으로 나의 캐릭터가 아래에 있을경우 위로 1.2초간 움직이게한다 
                    elif my_location[0][1] >= 211:
                        device.shell("input touchscreen swipe "+up+" "+up+" 1200")
                # 나의 캐릭터나 몬스터 둘다 감지 안됐을경우
                else:
                    # 랜덤한 대각선방향으로 2초간 움직이는 함수 실행
                    move_random()

                # 각 변수는 스킬의 쿨타임을 재는 용도
                # 현재 시간 (elapsed_time) 에서 마지막에 스킬을 시전했던 시간 (prev_time_n)을 뺀다
                hit = elapsed_time - prev_time
                skill_1 = elapsed_time - prev_time_1
                skill_2 = elapsed_time - prev_time_2
                skill_3 = elapsed_time - prev_time_3
                skill_4 = elapsed_time - prev_time_4
                skill_5 = elapsed_time - prev_time_5
                swap = elapsed_time - prev_time_6
                skill_6 = elapsed_time - prev_time_7
                # 스킬시전하는 함수 실행후 시전했던 스킬들의 시간들을 리턴한다
                times = start_attack(swap, elapsed_time, prev_time_1, prev_time_2,prev_time_3,prev_time_4, prev_time_5, prev_time_6, prev_time_7, skill_1,skill_2,skill_3,skill_4,skill_5,skill_6)
                # 마지막 스킬 시전 시간을 저장하는 변수값 갱신
                prev_time_1 = times[0]
                prev_time_2 = times[1]
                prev_time_3 = times[2]
                prev_time_4 = times[3]
                prev_time_5 = times[4]
                prev_time_6 = times[5]
                prev_time_7 = times[6]
                swap = times[7]   
            # 우측 하단 구석이 검은색이 아니라면 사냥터 밖의 코드 실행
            else: 
                battle = False
                # 몬스터 사냥끝낸 기록
                monster_count += 1
        # 사냥터 밖에 있을시 
        if battle == False:
            pyautogui.keyUp('up')
            pyautogui.keyUp('right')
            pyautogui.keyUp('left')
            pyautogui.keyUp('down')
            # 사냥터 바깥에있는 상태
            if(change > 1): 
                print('몬스터 잡은 횟수 : ', monster_count)
            # 사냥터 안에 있는상태
            elif change == 1:
                # 사냥터 코드 실행하도록한다
                battle = True
            # 4가지 종류의 몬스터감지 
            monster_locations_1 = monster_1.find_monster(screenshot, 0.5, 'rectangles')
            monster_locations_2 = monster_2.find_monster(screenshot, 0.5, 'rectangles')
            monster_locations_3 = monster_3.find_monster(screenshot, 0.5, 'rectangles')
            monster_locations_4 = monster_4.find_monster(screenshot, 0.5, 'rectangles')
            monsters_locations = monster_locations_1+monster_locations_2+monster_locations_3+monster_locations_4
            # 나의 캐릭터 감지
            my_location = my_character.find_monster(screenshot, 0.38, 'points')
            # 몬스터가 하나 이상이면
            if len(monsters_locations) > 0:
                # 기본공격으로 사냥터 진입
                device.shell("input touchscreen tap "+shift)
                # 기본공격횟수 추가저장
                stop_shift_count += 1
                # 기본공격횟수 10회 넘기면 프로그램 종료 
                if stop_shift_count > 5 :
                    break
        
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break
                

