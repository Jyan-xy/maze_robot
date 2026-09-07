cmake_minimum_required(VERSION 3.0.2)
project(visual_detect)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  sensor_msgs
  cv_bridge
)

catkin_package()

install(PROGRAMS
  detect_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
