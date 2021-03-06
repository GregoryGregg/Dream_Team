#!/usr/bin/env python
#Test
#Code convert geometry/twist msgs to motor commands
#By: Nicholas Gregg

import os
import rospy
import time
from a_star import AStar
from geometry_msgs.msg import Twist


mTOft = 3.28084
a_star = AStar()

#Inspiration from robotc
# def straight(speed):
#     #Store the master speed into values
#     mLeft = speed
#     sRight = speed
#     sSlave = sRight

#     encoders = a_star.read_encoders()
#     oldencoderL = encoders[0]
#     oldencoderR = encoders[1]

#     tError = 0
#     error = 0

#     kp = 2  #proportional constant
#     #ki = 1  #integral constant

#     i = 0

#     while (i < 10):
#         #set the motors with a starting value
#         if (i==0):
#             a_star.motors(mLeft,sRight)

#         encoders = a_star.read_encoders()

#         encoderL = encoders[0]
#         encoderR = encoders[1]

#         dL = encoderL - oldencoderL
#         dR = encoderR - oldencoderR

#         error = dL - dR
#         #tError += error
#         print(error)

#         sSlave += error/kp #+ ki*tError
#         print(sSlave)
#         print(mLeft)

#         oldencoderL = encoderL
#         oldencoderR = encoderR

#         a_star.motors(mLeft,sSlave)
#         i = 1 + i

#         time.sleep(0.05)

#converting the linear and angular message velocities to x and y
def callback(msg):
    #Only the angular z-axis and linear x- axis velocity are needed
    velXL = msg.linear.x * mTOft
    velZA = msg.angular.z * mTOft

    #Calculated max velocity to be 0.78508 ft/s
    #fitting -400 to 400 in the range of -0.78508 to 0.78508

    spLinear = int(((velXL + 0.78508)*(400 - (-400))/(.78508 - (-.78508))) - 400)
    spAngular = int(((velZA + 0.78508)*(400 - (-400))/(.78508 - (-.78508))) - 400)

    #the angular data is special it has to be converted to values
    #for the left and right motors, this will depend on the sign of the value

    spLeft = spLinear - spAngular
    spRight = spLinear + spAngular

    #Keep the number in an allowable range

    if spLeft > 400:
        spLeft = 400
    if spLeft < -400:
        spLeft = -400
    if spRight > 400:
        spRight = 400
    if spRight < -400:
        spRight = -400

    # print(spLeft)
    # print(spRight)

    # if ((spLeft==spRight) and (spLeft != 0) and (spRight != 0)):
    #     straight(spLeft)
    # else:
    a_star.motors(spLeft,spRight)
    #print("Left Motor:%s" % spLeft)
    #print("Right Motor:%s" % spRight)

    #time.sleep(1)

    #os.system('clear')

#Setting up the subscriber node
def listener():
    rospy.init_node('motor_control', anonymous=True)
    # team_name = rospy.get_param('team')
    # shape_name = rospy.get_param('shape')
    subject = rospy.get_param('subject')
    robot_name = rospy.get_param('robot_name')
    rospy.Subscriber("/%s/%s/cmd_vel" % (subject, robot_name), Twist, callback) #use this one for running the launch file
    #rospy.Subscriber("/cmd_vel", Twist, callback) #use this one for testing the system
    rospy.spin()

if __name__ == '__main__':
    listener()
