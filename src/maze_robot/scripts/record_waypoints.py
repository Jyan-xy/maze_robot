#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import sys
import tty
import termios
from geometry_msgs.msg import PoseWithCovarianceStamped

current_pose = None
waypoints = []

def amcl_callback(msg):
    global current_pose
    current_pose = msg.pose.pose

def get_key():
    """读取单个键盘输入"""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return key

def main():
    rospy.init_node('record_waypoints')
    rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, amcl_callback)
    rospy.sleep(1.0)

    print("=== 航点记录工具 ===")
    print("  's' : 记录当前位置")
    print("  'q' : 退出并保存所有航点")
    print("==================")

    while not rospy.is_shutdown():
        key = get_key()

        if key == 's':
            if current_pose is None:
                print("⚠️  尚未收到 amcl_pose，请确认小车定位正常")
                continue
            x  = current_pose.position.x
            y  = current_pose.position.y
            oz = current_pose.orientation.z
            ow = current_pose.orientation.w
            waypoints.append((x, y, oz, ow))
            print("✅ 记录第 %d 个点: x=%.4f, y=%.4f, oz=%.4f, ow=%.4f"
                  % (len(waypoints), x, y, oz, ow))

        elif key == 'q':
            break

    # 退出时打印可直接复制进导航脚本的格式
    print("\n=== 记录完成，共 %d 个点 ===" % len(waypoints))
    print("复制以下内容到导航脚本的 WAYPOINTS：\n")
    print("WAYPOINTS = [")
    for (x, y, oz, ow) in waypoints:
        print("    (%.4f, %.4f, %.4f, %.4f)," % (x, y, oz, ow))
    print("]")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
