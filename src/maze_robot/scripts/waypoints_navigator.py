#!/usr/bin/env python3
import rospy
import actionlib
import math
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
from std_msgs.msg import String


    
    

WAYPOINTS = [
    (-2.1828, 0.1349, -0.6991, 0.7150),
    (-2.1791, -0.2968, -0.6932, 0.7207),
    (-2.1484, -0.9062, -0.6859, 0.7277),
    (-2.1781, -1.7127, -0.7110, 0.7032),
    (-2.1727, -1.7358, -0.0330, 0.9995),
    (-1.7709, -1.7324, 0.0050, 1.0000),
    (-1.7264, -1.7320, 0.4967, 0.8679),
    (-1.7147, -0.8262, 0.7093, 0.7049),
    (-1.1111, -0.7787, 0.0097, 1.0000),  # 索引8 识别区1    
    (-1.6961, -0.7918, 0.8489, 0.5285),
    (-1.7156, -0.3721, 0.7261, 0.6875),
    (-1.7036, 1.0834, 0.7127, 0.7015),
    (-1.4815, 1.2270, 0.0490, 0.9988),
    (-0.4525, 1.2707, 0.0251, 0.9997),
    (0.5805, 1.2529, -0.0087, 1.0000),
    (0.6953, 1.2439, -0.5070, 0.8620),
    (0.7408, 0.6308, -0.7226, 0.6913),
    (0.8084, -0.2163, -0.9460, 0.3242),
    (-0.2003, -0.3230, -0.8510, 0.5252),
    (-0.1983, -1.7307, -0.2466, 0.9691),
    (2.2979, -1.7258, 0.7163, 0.6978),
    (2.2552, -0.4850, 0.6814, 0.7319),
    (2.2753, 0.3036, 0.9995, 0.0322),
    (1.6316, 0.2558, -1.0000, 0.0015),   # 索引23 识别区2
    (2.2545, 0.2707, 0.6818, 0.7315),
    (2.2882, 0.6824, 0.6651, 0.7467),
    (2.2817, 1.5200, 0.7194, 0.6946),
    (2.2731, 1.6826, 0.9685, 0.2491),
    (0.6324, 1.7131, -0.9997, 0.0249),
    (-0.1997, 1.7516, -0.9999, 0.0129),
    (-2.0810, 1.7331, -0.9998, 0.0173),
]

DETECT_INDICES = {8: "zone1", 23: "zone2"}  # 识别区索引

current_x = 0.0
current_y = 0.0

def odom_callback(msg):
    global current_x, current_y
    current_x = msg.pose.pose.position.x
    current_y = msg.pose.pose.position.y

def distance_to(x, y):
    return math.sqrt((x - current_x)**2 + (y - current_y)**2)

def send_goal(client, x, y, oz, ow):
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = "map"
    goal.target_pose.header.stamp = rospy.Time.now()
    goal.target_pose.pose.position.x = x
    goal.target_pose.pose.position.y = y
    goal.target_pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=oz, w=ow)
    rospy.loginfo("导航到 (%.4f, %.4f)" % (x, y))
    client.send_goal(goal)

def main():
    global current_x, current_y
    rospy.init_node('waypoint_navigator')
    rospy.Subscriber('/odom', Odometry, odom_callback)

    arrive_pub = rospy.Publisher('/arrive_zone', String, queue_size=1)

    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    rospy.loginfo("等待 move_base...")
    client.wait_for_server()
    rospy.loginfo("连接成功，开始导航")
    rate = rospy.Rate(10)

    for i, (x, y, oz, ow) in enumerate(WAYPOINTS):
        rospy.loginfo("=== 第 %d/%d 个点 ===" % (i+1, len(WAYPOINTS)))
        send_goal(client, x, y, oz, ow)

        start_time = rospy.Time.now()

        while not rospy.is_shutdown():
            dist = distance_to(x, y)
            state = client.get_state()
            elapsed = (rospy.Time.now() - start_time).to_sec()

            if state == 3:
                rospy.loginfo("到达！")
                # 如果是识别区，发布信号
                if i in DETECT_INDICES:
                    rospy.sleep(0.5)  # 等机器人完全停稳
                    zone_name = DETECT_INDICES[i]
                    arrive_pub.publish(zone_name)
                    rospy.loginfo("已发布 /arrive_zone: %s，等待识别完成..." % zone_name)
                    rospy.sleep(2.0)  # 给识别节点时间处理
                break
            if state in [4, 5]:
                rospy.logwarn("导航失败，状态码: %d，跳过" % state)
                break
            if elapsed > 2.0 and dist < 0.15:
                rospy.loginfo("接近目标(%.2fm)，切换下一个点" % dist)
                # 如果是识别区，同样触发
                if i in DETECT_INDICES:
                    rospy.sleep(0.5)
                    zone_name = DETECT_INDICES[i]
                    arrive_pub.publish(zone_name)
                    rospy.loginfo("已发布 /arrive_zone: %s，等待识别完成..." % zone_name)
                    rospy.sleep(2.0)
                break

            rate.sleep()

    rospy.loginfo("全部完成！")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
