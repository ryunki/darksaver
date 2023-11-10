import sys
import os
import datetime

import mss
from PIL import Image, ImageGrab, ImageOps
import pyautogui

import cv2 as cv
import numpy as np
import time
import winsound
import random
sys.path.append('..')
from vision import Vision

# w, h = pyautogui.size()
# print("PIL Screen Capture Speed Test")
# print("Screen Resolution: " + str(w) + 'x' + str(h))

img = None
t0 = time.time()
n_frames = 1
monitor = {"top": 35, "left": 1596, "width": 921, "height": 518}
# monitor = {"top": 1596, "left": 35, "width": 921, "height": 518}

my_character = Vision('../met_chicken3.png')
dead = Vision('../dead_3.png')
fountain = Vision('../fountain.png')
portal = Vision('../ergion_portal.png')
vacant = Vision('../vacancy.png')
ergion_tile = Vision('../ergion_tile.png')

question_mark = Vision('../question_mark.png')
metchicken_ergion = Vision('../metchicken_ergion.png')

outside_tile = Vision('../outside_tile.png')

# 인벤토리 아이콘의 좌표 (화면전환 감지에 쓰임)
inven_icon_1 = (2318, 76)
inven_icon_2 = (2319, 77)

# 힐링 포션의 좌표
heal=(2244, 397)
hp = (1772, 50) # tactic's hp threshold for 2301 with cross and 500hp (healing 2 potion)
# hp2 = (1788, 50) # tactic's hp threshold for 2844 with cross and 500hp (healing 2 potion)

# 스킬의 좌표들
a = (2247,318)
s = (2342,315)
d = (2441,316)
x = (2443,398)
c = (2345,479)
shift = (2343, 396)
spacebar = (2445,475)

# 빈 사냥터가 몇개인지 저장하는 변수
vacant_room_count = 0
# 방 몇번째 방인지 세는 변수
vacant_room_number = 0
# 사냥터인지 사냥터 밖인지 설정하는 변수
field = True
# 빈방대기실창이 열린후에 움직이는것을 막기위한 변수
room_selection = False

# 마우스 포인터가 모니터 구석에 위치할시 pyautogui가 작동안되는것 방지
pyautogui.FAILSAFE = False

# 각 스킬들의 시전 시간을 담는 변수들 (스킬 쿨타임 측정)
prev_skill_time = 0
prev_skill_time_1 = 0
prev_skill_time_2 = 0
prev_skill_time_3 = 0 
prev_skill_time_4 = 0
prev_skill_time_5 = 0
prev_skill_time_6 = 0
prev_skill_time_7 = 0

# 사냥터에서의 시간을 담는 변수 
field_time = 0
prev_field_time = 0

field_time_over = False
# 움직임 버튼을 한번만 누르게 하기 위한 변수
goDown = False
goUp = False
# 공격방향을 아래로 향하게하기 위한 변수 
pressDown = False
# 사냥터를 몇번 들어갔는지 담기위한 변수
visit_count = 0
# 나의 현재 위치를 담는 변수
my_location = []
# 사냥터의 특정 타일을 담는 변수
field_tile_location = []
# 스킬창 전환하기 위한 변수
swapped = False
open_room_list = False

# 프로그램 시작 시간을 담는 변수들
start = datetime.datetime.now()
start_seconds = time.time()

# 체력바의 특정 좌표에서 얻는 색깔 수치 계산 (예: 하얀색 255, 검은색 0)   
def hp_grab():
    # box = (hp2[0],hp2[1],hp2[0]+2,hp2[1]+2)
    box = (hp[0],hp[1],hp[0]+2,hp[1]+2)
    image = ImageGrab.grab(box)
    grayImage = ImageOps.grayscale(image)
    b = np.array(grayImage.getcolors())
    return b.sum()

# 물약을 클릭하기위한 함수
def heal_hp():
    pyautogui.click(heal)

# 화면전환되는 순간을 감지하는 함수 (다른곳으로 이동시 화면이 깜빡인다)
def screen_change():
    box = (inven_icon_1[0], inven_icon_1[1], inven_icon_2[0], inven_icon_2[1])
    image = ImageGrab.grab(box)
    grayImage = ImageOps.grayscale(image)
    a = np.array(grayImage.getcolors())
    return a.sum()

# 모든 keyDown상태 해제하는 함수
def deactivate_keyDown():
    pyautogui.keyUp('down')
    pyautogui.keyUp('up')
    pyautogui.keyUp('right')
    pyautogui.keyUp('left')

with mss.mss() as sct:
    while True:
        # t = datetime.datetime.now().strftime("%H:%M")
        # print(t)
        # 6시되면 멈추기
        # if(t == '06:00'):
        #     break

        # 현재시간 갱신하는 변수
        end_seconds = time.time()
        # 프로그램 시작한지 몇초 지났는지 담은 변수
        elapsed_time = round(end_seconds-start_seconds,1)
        # 모니터에서 스크린샷 값을 담은 변수
        img = sct.grab(monitor)
        # 스크린샷의 픽셀값를 담은 array 변수
        img = np.array(img)
        # 현재 마우스의 위치 저장
        prev_mouse_position = pyautogui.position()
        
        # 사냥터에 들어와있는상태
        if field == True:
            # 입장할 방의 선택여부를 False 로 초기화
            room_selection = False
            # 평타치기
            pyautogui.press('shift')
            # 화면전환을 감지 (사냥터에서 나갔을때)
            quit = screen_change()
            if(quit <= 250 and field == True):
                # 필드변수에 True가 없으면 방 입장시 화면 어두워지기때문에 포션 클릭됨
                print('사냥터 밖으로')
                # keyDown 해제
                deactivate_keyDown()
                # 사냥터 밖의 조건으로 전환
                field = False
                continue
            # 사냥터 바깥의 타일을 감지
            out_tile = outside_tile.find_image(img, 0.8, 'rectangles')
            if len(out_tile) > 0:
                field = False
                # keyDown 해제
                deactivate_keyDown()
                continue
            # 죽을때 뜨는 메세지를 감지
            death = dead.find_image(img, 0.8, 'rectangles')
            # 체력바의 특정 좌표의 값을 담은 변수
            hp_check = hp_grab()
            # 죽음 메세지 감지했을경우
            if (len(death) > 0):
                print('죽음')
                # keyDown 해제
                deactivate_keyDown()
                end = datetime.datetime.now()
                print(start)
                print(end)
                # 사냥터 밖의 조건으로 전환
                field = False
                continue
            # 죽지 않았을경우 체력바가 특정 좌표에서 색깔변화가 감지되면 
            # 포션 클릭
            elif(hp_check < 50 and field == True):
                print('포션 클릭')
                prev_mouse_position = pyautogui.position()
                heal_hp()
            # 사냥터 안에서 흘러간 시간을 담은 변수
            field_time = elapsed_time - prev_field_time
            # 사냥터 입장후 보스한테 접근후 잡는데 걸리는 시간 18 ~ 19초
            boss_death_time = random.randint(18,19)
            # 사냥터 입장후 6 ~ 7초후와 random_time 사이동안 실행
            if field_time > random.randint(6,7) and field_time < boss_death_time:
                # 사냥터 안에서 딱 한번만 공격방향 아래로 향하게함
                if pressDown == False:
                    # print('pressDown activate: ', field_time, elapsed_time)
                    pyautogui.keyUp('up')
                    pyautogui.press('down')
                    pressDown = True
                # pyautogui.click(a)
                # pyautogui.click(s)
                # pyautogui.click(d)
                # pyautogui.click(x)
                # pyautogui.click(c)
                # pyautogui.click(spacebar)
                # pyautogui.moveTo(prev_mouse_position[0], prev_mouse_position[1])
                # continue
            # 사냥터에서 보스몹 죽는 시간이 됐거나 19초가 지났을때
            # field_time >= 19 조건을 넣은이유는 나머지값이 0이 안될때가 있음
            # boss_death_time이 고정값이 아니라 18이나 19중 랜덤값이기 때문
            if field_time % boss_death_time == 0 or field_time >= 19:
                # 아래로 움직이는 버튼 한번만 누르게한다
                if goDown == False:
                    print('아래로 움직임: ', round(field_time,1))
                    pyautogui.keyDown('down')
                    goDown = True

            # 사냥터에서 26초가 지났을때 좌우로 움직이기
            if field_time >= 26:
                # 사냥터 정중앙에 있는 타일 좌표값
                tile = ergion_tile.find_image(img, 0.7, 'rectangles')
                # 내 캐릭터 좌표값
                me = metchicken_ergion.find_image(img, 0.6, 'rectangles')
                # 내 캐릭터의 좌표와 사냥터 타일이 감지된경우
                if len(tile) > 0 and len(me) > 0:
                    # 내 좌표의 x 값을 담은 변수
                    my_location = me[0][0]
                    # 타일 좌표의 x 값을 감은 변수
                    field_tile_location = tile[0][0]
                    # 타일이 내 위치보다 오른쪽에 위치했을경우 오른쪽으로 움직인다
                    if field_tile_location > my_location:
                        print('오른쪽으로')
                        pyautogui.keyUp('left')
                        pyautogui.keyDown('right')
                    # 타일이 내 위치보다 왼쪽에 위치했을경우 왼쪽으로 움직인다
                    elif field_tile_location < my_location:
                        print('왼쪽으로')
                        pyautogui.keyUp('right')
                        pyautogui.keyDown('left')

            # 각 변수는 스킬의 쿨타임을 재는 용도
            # 현재 시간에서 마지막에 스킬을 시전했던 시간을 뺀다
            hit = elapsed_time - prev_skill_time
            skill_1 = elapsed_time - prev_skill_time_1
            skill_2 = elapsed_time - prev_skill_time_2
            skill_3 = elapsed_time - prev_skill_time_3
            skill_4 = elapsed_time - prev_skill_time_4
            skill_5 = elapsed_time - prev_skill_time_5
            swap = elapsed_time - prev_skill_time_6
            skill_6 = elapsed_time - prev_skill_time_7
            # print(skill_1)
            if(swap > 60):
                swapped = True
                pyautogui.press('ctrl')
                pyautogui.press('c')
                pyautogui.press('space')
                pyautogui.press('ctrl')
                prev_skill_time_6 = elapsed_time
            # 스킬 스왑이 제대로 안됐을경우
            if swapped == True:
                question = question_mark.find_image(img, 0.6, 'rectangles')
                if len(question) > 0:
                    pyautogui.press('ctrl')
                    swapped = False

            # 각 스킬의 쿨타임이 지났을때 스킬 시전
            if(skill_1 > 5.2):
                skill_a = True
                prev_skill_time_1 = elapsed_time
                pyautogui.click(a)
                # pyautogui.moveTo(prev_mouse_position[0], prev_mouse_position[1])
            if(skill_2 > 7.2):
                skill_s = True
                prev_skill_time_2 = elapsed_time
                pyautogui.click(s)
                # pyautogui.moveTo(prev_mouse_position[0], prev_mouse_position[1])
            if(skill_3 > 7.2):
                skill_d = True
                prev_skill_time_3 = elapsed_time
                pyautogui.click(d)
                # pyautogui.moveTo(prev_mouse_position[0], prev_mouse_position[1])
            if(skill_6 > 4.7):
                skill_x = True
                prev_skill_time_7 = elapsed_time
                pyautogui.click(x)
                # pyautogui.moveTo(prev_mouse_position[0], prev_mouse_position[1])
            if(skill_4 > 2.2):
                skill_c = True
                prev_skill_time_4 = elapsed_time
                pyautogui.click(c)
                # pyautogui.moveTo(prev_mouse_position[0], prev_mouse_position[1])
            if(skill_5 > 3.7):
                skill_space = True
                prev_skill_time_5 = elapsed_time
                pyautogui.click(spacebar)
                # pyautogui.moveTo(prev_mouse_position[0], prev_mouse_position[1])

        # 사냥터 밖에서 포탈입장하는 상태
        if field == False:
            print(elapsed_time)
            # 한시간뒤에 프로그램 종료
            if elapsed_time > 3500:
                break
            # 포탈 감지   
            portal_ = portal.find_image(img, 0.8, 'rectangles')
            #   room_selection 은 빈방대기실창이 열린후에 내 캐릭터가 움직이는것을 막기위한 변수
            if (len(portal_) > 0 and room_selection == False):
                # 포탈을 향해 움직여 대기실창을 연다
                pyautogui.keyDown('up')
                time.sleep(0.1)
                pyautogui.keyDown('left')
                time.sleep(0.05)
                pyautogui.keyUp('up')
                pyautogui.keyUp('left')
            #   다른 사람이 1~4번 방을 사용중일때 나는 5~9번방 사용하기위한 마우스 드래그
            #   pyautogui.moveTo(2070, 411)
            #   pyautogui.dragTo(2070, 80, 0.2, button='left')
                room_selection = True

            # 약간의 딜레이를 주어 대기실 선택창이 완전히 열리도록한다
            time.sleep(0.2)
            # 빈 방들의 좌표를 담은 변수
            vacancy = vacant.find_image(img, 0.8, 'rectangles')
            # 빈 방이 존재하는경우
            if (len(vacancy) > 0 and room_selection == True):
                print('---------------------------')
                print('빈방 개수: ',len(vacancy))
                # 이전 대기실창의 빈방 개수가 현재 빈방 개수와 다를경우
                # (예: 현재 2번 방에 다른 유저가 들어가있을경우) 
                if vacant_room_count != len(vacancy):
                    # 첫번째 방으로 초기화
                    vacant_room_number = 0
                print(vacant_room_number+1, '번방 입장') 
                # n번째 방을 클릭한다
                pyautogui.click(vacancy[vacant_room_number][0]+1350, vacancy[vacant_room_number][1]+40)
                # 클릭 한순간 사냥터로 진입후 보스한테 접근하기위해 위로 움직이는 버튼을 누름
                pyautogui.keyDown('up')
                # 화면전환 끝날때까지 기다리는 시간
                time.sleep(0.5)
                # 사냥터 진입후 대기실창이 한번더 뜨는 버그가 있기때문에 취소버튼을 누름
                pyautogui.press('t')
                # 대기실창 다 없어질때까지 기다리는 시간
                time.sleep(0.7)
                # 사냥터 한번 들어갔을때마다 기록
                visit_count += 1
                print('방 입장 횟수: ', visit_count)
                # 현재의 빈 사냥터 방 개수를 저장
                vacant_room_count = len(vacancy)
                # 현재 들어간 사냥터 방이 마지막 방일경우
                if vacant_room_number == len(vacancy)-1 :
                    print('마지막방에 도달')
                    # 다음번에 첫번째 방으로 들어갈수있도록 초기화 
                    vacant_room_number = 0
                else:
                    # 마지막 방이 아닐경우 다음 방으로 들어갈수있도록한다
                    vacant_room_number += 1
                # 사냥터 코드 실행하도록 설정
                field = True
                # 사냥터에서 쓰일 현재 시간 저장
                prev_field_time = elapsed_time
                # 사냥터에서 True로 설정된 변수 False로 초기화
                goDown = False
                goUp = False
                pressDown = False
                # 내 위치 초기화
                my_location = []
                # print('started at: ',start)
                # print(datetime.datetime.now())
                print('------------------------------')

        # Break loop and end test
        if cv.waitKey(1) == ord('q'):
            break
