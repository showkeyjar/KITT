#! /usr/bin/python
# coding=utf-8

import time
import select
import sys
import os
import RPi.GPIO as GPIO
import numpy as np
import picamera
import picamera.array
import matplotlib.pyplot as plt
import time
import cv2

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import os

from car import Car
from car import selfcontrol
from lane_lines import *

krate_sum=[10]

def krate(line):
    # compute the sign of the slop of the line
    rate = (line[0] - line[2]) / (line[1] - line[3]) 
    return round(rate, 4)

def kratesum(lines):
    global krate_sum
    rsum = krate(lines[0]) + krate(lines[1])
    del krate_sum[0]
    krate_sum.append(rsum)
    result=np.fft.fft(krate_sum)
    return(result)

def change_speed(lines):
    try:
        if abs(kratesum(lines)) <= 0.5:
            v1 = 40
            v2 = 40       
        if kratesum(lines) < -0.5:
            v1 = 60
            v2 = -30
        if kratesum(lines) > 0.5:
            v1 = -30 
            v2 = 60
    except:
        v1 = v2 = 40
    return v1, v2

def forward(car):
    car.set_speed(60, 60)
    time.sleep(3)
    car.set_speed(0, 0)

def find_left(car):
    car.set_speed(60, -60)
    time.sleep(1)
    car.set_speed(0, 0)

def find_left(car):
    car.set_speed(-60, 60)
    time.sleep(1)
    car.set_speed(0, 0)
    
if __name__ == '__main__':
    car = Car()
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.start_preview()
    # Camera warm-up time
    time.sleep(2)
    v1, v2 = 0, 0
    while 1:
        image = np.empty((640 * 480 * 3,), dtype=np.uint8)
        camera.capture(image, 'bgr')
        image = image.reshape((640, 480, 3))
        # TODD: Detect
        try:
            lines = selfcontrol(image)
            print(krate(lines[0]), krate(lines[1]), v1, v2)
            v1, v2 = change_speed(lines)
        except:
            v1, v2 = 0, 0
            print("Find Error")
        # TODO: ROS 
        car.set_speed(v1, v2)