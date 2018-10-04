#!/usr/bin/env python
import rospy, roslib, json, time, tf2_ros
import urllib2
import geometry_msgs.msg

class TeamBroadcaster:
    def __init__(self):
        self.matrix = Homography()
        self.grabbed = False
        team_name = rospy.get_param('~team')
        shape_name = rospy.get_param('~shape')
        rospy.Subscriber('mapper/raw_data/%s/%s' %team_name %shape_name, geometry_msgs.msg.PoseStamped, callback, team_name, shape_name)
        rospy.Subscriber('mapper/homography', Homography, matrix_grabber)
        rospy.spin()

    def matrix_grabber(homography):
        self.matrix = homography
        self.grabbed = True

    def callback(rover,team_name,shape_name):
        if self.grabbed:
            br = tf2_ros.TransformBroadcaster()
            opt_prime = geometry_msgs.msg.TransformStamped()
            opt_prime.header.stamp = rospy.Time.now()
            opt_prime.header.frame_id = 'map'
            opt_prime.child_frame_id = 'odom_%s_%s' %team_name %shape_name

            q11 = self.matrix.q11
            q12 = self.matrix.q12
            q13 = self.matrix.q13
            q21 = self.matrix.q21
            q22 = self.matrix.q22
            q23 = self.matrix.q23
            q31 = self.matrix.q31
            q32 = self.matrix.q32
            q33 = self.matrix.q33
            u = rover.pose.position.x
            v = rover.pose.position.y
            opt_prime.transform.translation.x = ((q11*u+q12*v+q13)/(q31*u+q32*v+q33))
            opt_prime.transform.translation.y = ((q21*u+q22*v+q23)/(q31*u+q32*v+q33))
            opt_prime.transform.rotation.x = rover.pose.orientation.x
            opt_prime.transform.rotation.y = rover.pose.orientation.y
            opt_prime.transform.rotation.z = rover.pose.orientation.z
            opt_prime.transform.rotation.w = rover.pose.orientation.w
            br.sendTransform(opt_prime)
        else: pass

if __name__ == '__main__':
    rospy.init_node('team_tf_broadcaster')
    try:
        tb = TeamBroadcaster()
    except ROSInterruptException:
        pass
