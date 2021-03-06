#!/usr/bin/env python
import rospy, roslib, numpy
from sensor_msgs.msg import PointCloud
from geometry_msgs.msg import PoseStamped, Point32
from romi_soccer.msg import Homography

class RomiFinder:
    def __init__(self):
        # Initializes a boolean to flag whether the homography matrix has been grabbed yet
        self.grabbed = False
        self.q11 = 0
        self.q12 = 0
        self.q13 = 0
        self.q21 = 0
        self.q22 = 0
        self.q23 = 0
        self.q31 = 0
        self.q32 = 0
        self.q33 = 0
        self.cloud_num = rospy.get_param('~number')
        object = rospy.get_param('~object')
        subject = rospy.get_param('~subject')
        self.subject_robot = rospy.get_param('~subject_robot')
        self.pub = rospy.Publisher('/%s/%s/cloudy_meatballs' % (subject,self.subject_robot),PointCloud,queue_size=10)
        rospy.Subscriber('/mapper/homography',Homography, self.matCallback)
        if rospy.has_param('~robot_name'):
            robot_name = rospy.get_param('~robot_name')
            rospy.Subscriber('/%s/%s/raw_pose' % (object,robot_name),PoseStamped, self.callback)
        else:
            rospy.Subscriber('/%s/raw_pose' % object,PoseStamped, self.callback)
        rospy.spin()

    def matCallback(self,matrix):
        self.q11 = matrix.q11
        self.q12 = matrix.q12
        self.q13 = matrix.q13
        self.q21 = matrix.q21
        self.q22 = matrix.q22
        self.q23 = matrix.q23
        self.q31 = matrix.q31
        self.q32 = matrix.q32
        self.q33 = matrix.q33
        self.grabbed = True

    def callback(self,data):
        if (self.grabbed):
            cloud = PointCloud()
            cloud.header.stamp = rospy.Time.now()
            cloud.header.frame_id = 'sensor_frame_%s' % self.subject_robot
            cloud.points = [Point32()] * 7

            u = data.pose.position.x
            v = data.pose.position.y
            x = ((self.q11*u+self.q12*v+self.q13)/(self.q31*u+self.q32*v+self.q33))
            # x = 0.006095*u
            y = ((self.q21*u+self.q22*v+self.q23)/(self.q31*u+self.q32*v+self.q33))
            cloud.points[self.cloud_num] = Point32(x,y,0)
            self.pub.publish(cloud)
        else: rospy.loginfo('Waiting for homography calibration...')
