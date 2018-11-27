#!/usr/bin/env python
import time, json, urllib2
import timeit 
import os
import math
import RPi.GPIO as GPIO
from a_star import AStar


a_star = AStar()

def fire():
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(21,GPIO.OUT)

    GPIO.output(21,GPIO.HIGH)
    time.sleep(.1)
    GPIO.output(21,GPIO.LOW)

def grabber():
    response = urllib2.urlopen('http://192.168.137.1:8001/FieldData/GetData')
    source = response.read()
    data = json.loads(source.decode())
    locations = {'bSquare': {'X': data['Blue Team Data']['Square']['Object Center']['X'], 'Y': data['Blue Team Data']['Square']['Object Center']['Y']},
                'bCircle': {'X': data['Blue Team Data']['Circle']['Object Center']['X'], 'Y': data['Blue Team Data']['Circle']['Object Center']['Y']},
                'bTriangle': {'X': data['Blue Team Data']['Triangle']['Object Center']['X'], 'Y': data['Blue Team Data']['Triangle']['Object Center']['Y']},
                'rSquare': {'X': data['Red Team Data']['Square']['Object Center']['X'], 'Y': data['Red Team Data']['Square']['Object Center']['Y']},
                'rCircle': {'X': data['Red Team Data']['Circle']['Object Center']['X'], 'Y': data['Red Team Data']['Circle']['Object Center']['Y']},
                'rTriangle': {'X': data['Red Team Data']['Triangle']['Object Center']['X'], 'Y': data['Red Team Data']['Triangle']['Object Center']['Y']},
                'ball': {'X': data['Ball']['Object Center']['X'], 'Y': data['Ball']['Object Center']['Y']}}

    return locations

def straight(speed):
    mLeft = speed
    sRight = speed
    sSlave = sRight
    encoders = a_star.read_encoders()
    oldencoderL = encoders[0]
    oldencoderR = encoders[1]
    tError = 0
    error = 0
    kp = 2
    ki = 1
    i = 0
    while (i < 10):
        if (i==0):
            a_star.motors(mLeft,sRight)
        encoders = a_star.read_encoders()
        encoderL = encoders[0]
        encoderR = encoders[1]
        dL = encoderL - oldencoderL
        dR = encoderR - oldencoderR

        error = dL - dR

        if error > 1000:
            error = 0

        tError += error
        sSlave += error/kp #+ ki*tError
        
        if (sSlave > 400):
            sSlave = 400
        if (sSlave < -400):
            sSlave = -400 
            
        oldencoderL = encoderL
        oldencoderR = encoderR
        a_star.motors(mLeft,sSlave)
        i = 1 + i
        time.sleep(0.05)

def displacement(right_encoder,left_encoder): #velocity: ft/s, position: ft
    theta_initial = 0.0
    theta_new_unbounded = 0.0
    pi = math.pi
    dist_between_wheels = 0.4791667
    right_wheel_rotations = right_encoder/float(1440)                  
    left_wheel_rotations = left_encoder/float(1440)                    
    right_displacement = right_wheel_rotations*float(2)*pi*.114829     
    left_displacement = left_wheel_rotations*float(2)*pi*.114829
    displacement_middle = (right_displacement + left_displacement)/float(2)
    alpha_left_turn_radians = (left_displacement - right_displacement)/dist_between_wheels
    alpha_left_turn_degrees = alpha_left_turn_radians * float(180)/pi
    theta_new_unbounded = theta_initial + alpha_left_turn_degrees 
    theta_new = theta_new_unbounded % 360                                   
    theta_initial = theta_new 
    return theta_new
                                                                
def point_orientation(our_point_x, our_point_y, desired_point_x, desired_point_y): #calculates the angle between the two points to figure out the correction
    pi = math.pi
    atan2 = math.atan2
    dist_x = float(desired_point_x) - float(our_point_x) #original orientation should be angle from gyro/encoder taken only once at the beginning of the process
    dist_y = float(desired_point_y) - float(our_point_y)
    mag = float(math.sqrt(math.pow(dist_x,2) + math.pow(dist_y,2)))
    angle = atan2(dist_y , dist_x) #can return [-pi,pi]
    angle_degrees = angle * float(180)/pi
    if angle_degrees >= 0:
        orientation_input_unbounded = angle_degrees + float(360)
    else:
        orientation_input_unbounded = float(360) + angle_degrees + float(360)
    orientation_input = orientation_input_unbounded % 360
    return orientation_input, mag

def check(comrade, target):
    locations = grabber()
    mGX = float(locations[target]['X'] - 12)*(float(8/float(394-12)))
    mGY = float(locations[target]['Y'] - 31)*(float(4/float(221-31)))
    mMeX = float(locations[comrade]['X'] - 12)*(float(8/float(394-12)))
    mMeY = float(locations[comrade]['Y'] - 31)*(float(4/float(221-31)))

    null1 ,mag = point_orientation(mMeX,mMeY,mGX,mGY)

    return mag

def run(me, goal):
    locations = grabber()
    if (goal == 'goal'):
        mGX = float(339 - 12)*(float(8/float(394-12))) 
        mGY = float(128 - 31)*(float(4/float(221-31)))       
    else:
        mGX = float(locations[goal]['X'] - 12)*(float(8/float(394-12)))
        mGY = float(locations[goal]['Y'] - 31)*(float(4/float(221-31)))
    
    previousMeX = float(locations[me]['X'] - 12)*(float(8/float(394-12)))
    previousMeY = float(locations[me]['Y'] - 31)*(float(4/float(221-31)))

    if (goal == 'ball'):
        mark = .75
    else:
        mark = 1.25

    while True:
        
        spLeft = 100
        locations = grabber()
        
        mMeX = float(locations[me]['X'] - 12)*(float(8/float(394-12)))
        mMeY = float(locations[me]['Y'] - 31)*(float(4/float(221-31)))
        dMe = mMeX - previousMeX

        if abs(dMe) > 2:
            mMeX = previousMeX
            mMeY = previousMeY
        
        null1 ,mag = point_orientation(mMeX,mMeY,mGX,mGY)

        previousMeX = mMeX
        previousMeY = mMeY
        
        if (mag < mark):
            a_star.motors(0,0)
            break
        else:
            straight(spLeft)

def orient(oLEncoder, oREncoder, compensated_orientation, previous_orientation, me, goal):
    tAngle = previous_orientation
    while True:
        encoders = a_star.read_encoders()
        rEncoder = encoders[1]
        lEncoder = encoders[0]

        pRight = rEncoder - oREncoder
        pLeft  = lEncoder - oLEncoder

        oLEncoder = lEncoder
        oREncoder = rEncoder

        angle = displacement(pRight,pLeft) 
                                  
        tAngle += angle
        cAngle = tAngle % 360
        
        print('difference Angle: %s' % angle)
        print('compensated orientation: %s' % compensated_orientation)
        print('Total angle: %s' % cAngle)

        lA = (cAngle - compensated_orientation) % 360
        rA = (compensated_orientation - cAngle) % 360

        if (((cAngle - 1) <= (compensated_orientation)) and ((compensated_orientation) <= (cAngle + 1))):
            run(me, goal)
            a_star.motors(0,0) 
            break 
        elif (rA > lA):
            a_star.motors(-50,50)
        elif (rA < lA):
            a_star.motors(50,-50)
    return cAngle


def talker(me, goal, previous_orientation):
  
    encoders = a_star.read_encoders()
   
    oldright_encoder = encoders[1]
    oldleft_encoder = encoders[0]
   
    locations = grabber()

    orientation_input, mag = point_orientation(locations[me]['X'],locations[me]['Y'],locations[goal]['X'],locations[goal]['Y'])

    if (orientation_input >= 180):
        angle_error_offset = -5.0
    else:
        angle_error_offset = 5.0
    if ((orientation_input < 5.0) or (orientation_input > 355.0)):
        compensated_orientation = 0.0
    else:
        compensated_orientation = (orientation_input - angle_error_offset) % 360
    
    last_angle = orient(oldleft_encoder,oldright_encoder,compensated_orientation, previous_orientation, me, goal)
    print('the last angle for the first movement was: %s' % last_angle)
    return last_angle
   

def execute():
    last_orientation = talker('rSquare','rTriangle',0.0)
    distance = check('rTriangle','rCircle')
    while (distance > 1):
        distance = check('rTriangle','rCircle')
    end_orientation = talker('rSquare','ball',last_orientation)
    nn = talker('rSquare','bSquare',end_orientation)
    fire()
    

if __name__ == '__main__':
    try:
        execute()
    except KeyboardInterrupt:
        a_star.motors(0,0)