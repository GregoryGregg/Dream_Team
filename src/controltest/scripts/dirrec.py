#!/usr/bin/env python
#import sys
#sys.path.insert(0, '/home/pi/pololu-rpi-slave-arduino-library-2.0.0/pi')
import rospy
from a_star import AStar
from controltest.msg import RoverDirections

#Testing to see what direction is set
def callback(directions):
	a_star = AStar()
	if directions.forward:
		a_star.motors(200,200)
	elif directions.back:
		a_star.motors(-200,-200)
	elif directions.left:
		a_star.motors(200,-200)
	elif directions.right:
		a_star.motors(-200,200)
	else:
		a_star.motors(0,0)

def main():
	rospy.init_node('Receiver')
	rospy.Subscriber('/directions_rover', RoverDirections, callback)
	rospy.spin()

if __name__ == '__main__':
	main()

