import tf
from geometry_msgs.msg import Pose


def get_wrist_roll(grasp):

    grasp_pose = Pose()
    grasp_pose.position.x = grasp.palm_pose[0]
    grasp_pose.position.y = grasp.palm_pose[1]
    grasp_pose.position.z = grasp.palm_pose[2]
    grasp_pose.orientation.x = grasp.palm_pose[3]
    grasp_pose.orientation.y = grasp.palm_pose[4]
    grasp_pose.orientation.z = grasp.palm_pose[5]
    grasp_pose.orientation.w = grasp.palm_pose[6]

    # Negating the z gives the inverse of the quaternion
    grasp_rpy = tf.transformations.euler_from_quaternion((grasp_pose.orientation.x,
                                                          grasp_pose.orientation.y,
                                                          -grasp_pose.orientation.z,
                                                          grasp_pose.orientation.w))

    wrist_roll = grasp_rpy[2]

    return wrist_roll

