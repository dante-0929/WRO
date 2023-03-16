#!/usr/bin/env python3
from ev3dev.ev3 import *
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent, MoveTank, MediumMotor
import ev3dev2.sensor as INPORT_1
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from time import sleep
from ev3dev2.display import Display
import ev3dev2.fonts as fonts
from ev3dev2.button import Button
import csv
import math


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.


# Create your objects here.

# Write your program here.


# ====================================
# 回転の計算
# ====================================
def rotation(a, b, c):
    t = a * math.pi
    r = b * math.pi / c
    rs = r / t
    return rs


# ====================================
# 指定範囲移動
# ====================================
def rotation_motor(a, b):
    t = a * math.pi
    rs = b / t
    return rs


# ====================================
# pid LINEトレース
# ====================================
def line_trace(a):
    global m, m1, e, e1, e2, y_list, y2_list, y3_list, p_list, i_list, d_list, m_list
    kp = 0.02
    ki = 0.00000003
    kd = 0.8
    goal = 55
    color_raw = max(color_sensor.raw)
    m1 = m
    e2 = e1
    e1 = e
    e = goal - color_raw
    powr = 40
    p = kp * e
    i = ki * (e + e1)
    d = kd * ((e - e1) + (e1 - e2))
    m = p + i + d
    r = powr + m
    l = powr - m
    p_list.append(p)
    i_list.append(i)
    d_list.append(d)
    m_list.append(m)
    if 0 == powr:
        print(20, 20)
    elif -100 <= r <= 100 and -100 <= l <= 100:
        y_list.append(round(r, 5))
        y2_list.append(round(l, 5))
        y3_list.append(color_raw)
        if a == "right":
            motor_tank.on(r, l)
        elif a == "left":
            motor_tank.on(l, r)


# ====================================
# うしろむく
# ====================================
def face_back():
    motor_tank.on_for_rotations(-50, 50, rotation(4, 8, 4))
    motor_tank.on_for_rotations(30, 30, rotation_motor(4, 0.7))
    motor_tank.on_for_rotations(-50, 50, rotation(4, 8, 4))
    motor_tank.on(0, 0)


# ====================================
# 指定距離lineトレース
# ====================================
def count_distance():
    specified_distance = rotation_motor(4, 0.5)
    motor_b = LargeMotor(OUTPUT_B)
    motor_a = LargeMotor(OUTPUT_A)
    motor_a.command = 'reset'
    while True:
        motor_count = motor_a.full_travel_count
        motor_count = motor_count / 360
        if specified_distance <= motor_count:
            break
        line_trace("right")


# ====================================
# ブロック持ち上げるミッション
# ====================================
def b_mission():
    motor_tank.on_for_rotations(50, 50, rotation_motor(4, 2.4))
    motor_tank.on(0, 0)
    sleep(0.5)
    m_motor.on(-20)
    sleep(1)
    motor_tank.on_for_rotations(30, 30, rotation_motor(4, 7.5))
    sleep(0.3)
    m_motor.on(30)
    sleep(0.7)
    motor_tank.on_for_rotations(-50, -50, rotation_motor(4, 11))


# ====================================
# カラーブロックを読むミッション
# ====================================
def c_mission():
    global sheet, tile_color, next_tile
    motor_tank.on_for_rotations(30, 30, rotation_motor(4, 8))
    motor_tank.on_for_rotations(30, 30, rotation_motor(4, 2))
    sleep(0.2)
    tile_color = color_sensor.color
    next_tile = tile_color
    print("next" + str(next_tile))
    motor_tank.on_for_rotations(-30, -30, rotation_motor(4, 3))
    sleep(0.2)
    sheet = color_sensor.color
    print("next" + str(sheet))
    motor_tank.on_for_rotations(-30, -30, rotation_motor(4, 7))


# ====================================
# ミッション
# ====================================
def mission():
    global sheet, flag, next_line, now_line, now_tile, next_tile, field_map, line_difference, direction2, direction,  m, m1, e, e1, e2
    m = 0.00
    m1 = 0.00
    e = 0.00
    e1 = 0.00
    e2 = 0.00
    if sheet == 2:
        motor_tank.on_for_rotations(25, -25, rotation(4, 8, 4))
        direction = 1
    if sheet == 4:
        motor_tank.on_for_rotations(-25, 25, rotation(4, 8, 4))
        direction = -1
    motor_tank.on_for_rotations(-50, -50, rotation_motor(4, 4))
    while True:
        line_trace("right")
        color_color = color_sensor.color
        print("color" + str(color_color))
        if color_color == 5 or color_color == 7:
            b_mission()
            break
    face_back()
    while True:
        line_trace("right")
        color_color = color_sensor.color
        if color_color == 5 or color_color == 7:
            c_mission()
            motor_tank.on(0, 0)
            break
    face_back()
    sleep(0.5)
    while True:
        line_trace("right")
        color_color = color_sensor.color
        if color_color == 5 or color_color == 7:
            break
    motor_tank.on_for_rotations(-30, -30, rotation_motor(4, 8))
    for i in field_map:
        if next_tile == i['color']:
            next_line = i['line']
    line_difference = next_line - now_line
    if line_difference > 0:
        direction2 = 1
    elif line_difference < 0:
        line_difference = line_difference * -1
        direction2 = -1
    if direction * direction2 < 0:
        motor_tank.on_for_rotations(25, -25, rotation(4, 8, 4))
    elif direction * direction2 > 0:
        motor_tank.on_for_rotations(-25, 25, rotation(4, 8, 4))


# ====================================
# 最初の処理
# ====================================
def only_first():
    global sheet
    m_motor.on(30)
    sleep(1)
    motor_tank.on(30, 30)
    sleep(0.6)
    while True:
        color_color = color_sensor.color
        print(color_color)
        if color_color == 2 or color_color == 4:
            print(color_color)
            sheet = color_color
            motor_tank.on(0, 0)
            motor_tank.on_for_rotations(30, -30, rotation(4, 8, 4))
            motor_tank.on_for_rotations(50, 50, rotation_motor(4, 2.5))
            break
        line_trace("right")


# ====================================
# 線移動
# ====================================
def line_move():
    global flag, line_difference
    flag = 0
    flag_count = 0
    while True:
        motor_tank.on(80, 80)
        color_color = color_sensor.color
        if color_color == 1:
            flag = 1
        if flag == 1 and color_color == 6:
            flag_count += 1
            flag = 0
        if line_difference == flag_count:
            motor_tank.on(0, 0)
            break


# ====================================
# main
# ====================================
def main():
    only_first()
    while True:
        line_move()
        mission()


# ====================================
# 最初(定義とか)
# ====================================
if __name__ == "__main__":
    color_sensor = ColorSensor(address="in2")
    color_sensor.mode = 'COL-COLOR'
    motor_tank = MoveTank(OUTPUT_B, OUTPUT_A)
    m_motor = MediumMotor(OUTPUT_D)
    flag = 0
    direction = 0
    direction2 = 0
    sheet = 0
    tile_color = 1
    now_tile = 1
    next_tile = 0
    next_line = 0
    now_line = 1
    line_difference = 1
    m = 0.00
    m1 = 0.00
    e = 0.00
    e1 = 0.00
    e2 = 0.00
    y_list = []
    y2_list = []
    y3_list = []
    p_list = []
    i_list = []
    d_list = []
    m_list = []
    btn = Button()
    field_map = [
        {
            'color': 3,
            'line': 1
        },
        {
            'color': 2,
            'line': 2
        },
        {
            'color': 4,
            'line': 3
        },
        {
            'color': 5,
            'line': 4
        }
    ]
    # b_mission()
    # mission()

    while True:
        print('ok')
        if btn.enter:
            break
    
    """
    while True:
        line_trace("right")
        if btn.up:
            f = open('out2.csv', 'w', newline='')
            data = [y_list, y2_list, y3_list, p_list, i_list, d_list, m_list]
            writer = csv.writer(f)
            writer.writerows(data)
            f.close()
            break
    """

    # c_mission()
    main()
