#!/usr/bin/env python
# Modified from RethinkRobotics website

import argparse
import struct
import sys
import copy

import rospy
import rospkg

from gazebo_msgs.srv import (
    SpawnModel,
    DeleteModel,
    GetModelState,
    GetLinkState,
)
from gazebo_msgs.msg import (
    LinkState,
)
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Quaternion,
)
from std_msgs.msg import (
    Header,
    Empty,
)

#from baxter_core_msgs.srv import (
#    SolvePositionIK,
#    SolvePositionIKRequest,
#)

#import baxter_interface

#SPAWN WALL AT 1.1525 z to be above table or 0.3755 to be below
def load_gazebo_models(table_pose=Pose(position=Point(x=1, y=0.0, z=0.0)),
                       table_reference_frame="world",
                       block1_pose=Pose(position=Point(x=0.8, y=-0.0065, z=0.7825)),
                       block2_pose=Pose(position=Point(x=0.5, y=-0.2965, z=0.7825)),
                       block3_pose=Pose(position=Point(x=0.5, y=0.1265, z=0.7825)),
                       block_reference_frame="world"):
    # Get Models' Path
    model_path = rospkg.RosPack().get_path('baxter_sim_examples')+"/models/"
    # Load Table SDF
    table_xml = ''
    with open (model_path + "cafe_table/model.urdf", "r") as table_file:
        table_xml=table_file.read().replace('\n', '')
    block1_xml = ''
    with open (model_path + "block/model.urdf", "r") as block_file:
        block_xml=block_file.read().replace('\n', '')
    block2_xml = ''
    with open (model_path + "button/model.urdf", "r") as button_file:
        button_xml=button_file.read().replace('\n', '')
    block3_xml = ''
    with open (model_path + "button/model.urdf", "r") as button_file:
        button_xml=button_file.read().replace('\n', '')
        
        
    # Spawn Table SDF
    rospy.wait_for_service('/gazebo/spawn_sdf_model')

    try:
        spawn_sdf = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)
        resp_sdf = spawn_sdf("cafe_table", table_xml, "/",
                             table_pose, table_reference_frame)
    except rospy.ServiceException, e:
        rospy.logerr("Spawn SDF service call failed: {0}".format(e))
    
    
    #rospy.wait_for_service('/gazebo/spawn_urdf_model')
    #try:
    #    spawn_urdf = rospy.ServiceProxy('/gazebo/spawn_sdf_model', SpawnModel)
    #    resp_urdf = spawn_sdf("grey_wall", grey_wall_xml, "/",
    #                           grey_wall_pose, grey_wall_reference_frame)
    #except rospy.ServiceException, e:
    #    rospy.logerr("Spawn SDF service call failed: {0}".format(e))
    
    
    # Spawn Block URDF
    rospy.wait_for_service('/gazebo/spawn_urdf_model')
    try:
        spawn_urdf = rospy.ServiceProxy('/gazebo/spawn_urdf_model', SpawnModel)
        resp_urdf = spawn_urdf("block1", block_xml, "/",
                               block1_pose, block_reference_frame)
    except rospy.ServiceException, e:
        rospy.logerr("Spawn URDF service call failed: {0}".format(e))
    rospy.wait_for_service('/gazebo/spawn_urdf_model')

    try:
        spawn_urdf = rospy.ServiceProxy('/gazebo/spawn_urdf_model', SpawnModel)
        resp_urdf = spawn_urdf("block2", button_xml, "/",
                               block2_pose, block_reference_frame)
    except rospy.ServiceException, e:
        rospy.logerr("Spawn URDF service call failed: {0}".format(e))
    rospy.wait_for_service('/gazebo/spawn_urdf_model')

    try:
        spawn_urdf = rospy.ServiceProxy('/gazebo/spawn_urdf_model', SpawnModel)
        resp_urdf = spawn_urdf("block3", button_xml, "/",
                               block3_pose, block_reference_frame)
    except rospy.ServiceException, e:
        rospy.logerr("Spawn URDF service call failed: {0}".format(e))


def delete_gazebo_models():
    # This will be called on ROS Exit, deleting Gazebo models
    # Do not wait for the Gazebo Delete Model service, since
    # Gazebo should already be running. If the service is not
    # available since Gazebo has been killed, it is fine to error out
    try:
        delete_model = rospy.ServiceProxy('/gazebo/delete_model', DeleteModel)
        resp_delete = delete_model("cafe_table")
        resp_delete = delete_model("block")
        resp_delete = delete_model("button")
    except rospy.ServiceException, e:
        rospy.loginfo("Delete Model service call failed: {0}".format(e))

def main():

    rospy.init_node("search_and_rescue")
    load_gazebo_models()
    #rospy.wait_for_message("/robot/sim/started", Empty)    

    pub_cafe_table_pose = rospy.Publisher('cafe_table_pose', Pose, queue_size = 10)
    pub_grey_wall_pose = rospy.Publisher('grey_wall_pose', Pose, queue_size = 10)
    pub_block1_pose = rospy.Publisher('block1_pose', Pose, queue_size = 10)
    pub_block2_pose = rospy.Publisher('block2_pose', Pose, queue_size = 10)
    pub_block3_pose = rospy.Publisher('block3_pose', Pose, queue_size = 10)


    while not rospy.is_shutdown():
		
        rate = rospy.Rate(10) # 10hz
		
        #Get cafe_table pose
        rospy.wait_for_service('/gazebo/get_model_state')
    
        try:
            #ms means model_state
            cafe_table_ms = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            resp_cafe_table_ms = cafe_table_ms("cafe_table", "");
            pose_cafe_table = resp_cafe_table_ms.pose
            pub_cafe_table_pose.publish(pose_cafe_table)
        except rospy.ServiceException, e:
            rospy.logerr("get_model_state for cafe_table service call failed: {0}".format(e))
			
        #Get grey_wall pose
        rospy.wait_for_service('/gazebo/get_link_state')
    
        try:
            #ms means model_state
            grey_wall_ms = rospy.ServiceProxy('/gazebo/get_link_state', GetLinkState)
            resp_grey_wall_ms = grey_wall_ms("grey_wall_link", "");
            pose_grey_wall = resp_grey_wall_ms.link_state.pose
            pub_grey_wall_pose.publish(pose_grey_wall)
        except rospy.ServiceException, e:
            rospy.logerr("get_model_state for grey_wall service call failed: {0}".format(e))
			
        #Get block1 pose
        rospy.wait_for_service('/gazebo/get_model_state')
    
        try:
            #ms means model_state
            block1_ms = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            resp_block1_ms = block1_ms("block1", "");
            pose_block1 = resp_block1_ms.pose
            pub_block1_pose.publish(pose_block1)
        except rospy.ServiceException, e:
            rospy.logerr("get_model_state for block1 service call failed: {0}".format(e))
			
        #Get block2 pose
        rospy.wait_for_service('/gazebo/get_model_state')
    
        try:
            #ms means model_state
            block2_ms = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            resp_block2_ms = block2_ms("block2", "");
            pose_block2 = resp_block2_ms.pose
            pub_block2_pose.publish(pose_block2)
        except rospy.ServiceException, e:
            rospy.logerr("get_model_state for block2 service call failed: {0}".format(e))
			
        #Get block3 pose
        rospy.wait_for_service('/gazebo/get_model_state')
    
        try:
            #ms means model_state
            block3_ms = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
            resp_block3_ms = block3_ms("block3", "");
            pose_block3 = resp_block3_ms.pose
            pub_block3_pose.publish(pose_block3)
        except rospy.ServiceException, e:
            rospy.logerr("get_model_state for block3 service call failed: {0}".format(e))
        
    rate.sleep()

    return 0

if __name__ == '__main__':
    sys.exit(main())
