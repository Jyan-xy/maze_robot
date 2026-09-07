# maze_robot
一个可以在迷宫中行走的机器人 预先设定好轨迹点 根据轨迹点走。
机器人模型取自Autolabor教程机器人模型为参考基础，进行了一部分原创：（1）外观重新设计——将原单层黄色圆柱底盘改为双层圆柱结构（下层黑色大底盘 + 上层蓝色小平台），激光雷达改为红色，深度相机改为白色，驱动轮改为红色，支撑轮改为黑色，整体视觉效果更鲜明；（2）结构尺寸重新调优——底盘半径/高度、轮距等物理参数根据迷宫场景需求重新标定；（3）质量参数全面重新设定，保证物理仿真稳定性；（4）自主设计完整机器人 XACRO 模型，包含底盘（base_link &base_top）、驱动轮（left/right_wheel）、支撑轮（front/back_wheel）、激光雷达支架（support/laser）、深度相机等刚体结构；编写全部 XACRO 模型文件（base_inertia.xacro、laser_inertia.xacro、camera_inertia.xacro、controller.xacro、sensor.xacro、kinect.xacro），为每个连杆添加惯性矩阵与碰撞属性；配置差分驱动控制器（libgazebo_ros_diff_drive）和激光雷达 Gazebo 插件，参数全部自主调优
本作品所有源码存放于提交压缩包的 src/ 目录下，主要路径如下：
src/maze_robot/  	ROS功能包（导航与建模）
src\maze_robot\CMakeLists.txt  	编译配置文件
src\maze_robot\package.xml 	功能包描述文件

src/maze_robot/config/ 	存放RViz可视化配置文件
src\maze_robot\config\my_maze_map.rviz 	加载迷宫地图场景的RViz预设配置
src\maze_robot\config\robot.rviz 	机器人本体、传感器、话题显示的RViz预设配置

src/maze_robot/launch/  	ROS启动文件夹
src\maze_robot\launch\amcl.launch 	启动 AMCL 粒子滤波定位
src\maze_robot\launch\compete_gazebo.launch 	在Gazebo 物理仿真环境启动机器人
src\maze_robot\launch\compete_rviz.launch 	在RViz中启动
src\maze_robot\launch\compete_server.launch 	地图服务
src\maze_robot\launch\gmapping.launch 	启动 GMapping 算法
src\maze_robot\launch\map_saver.launch 	保存地图
src\maze_robot\launch\move_base.launch 	导航核心
src\maze_robot\launch\robot_gazebo.launch 	在Gazebo 空世界启动机器人

src/maze_robot/map/ 	存放 ROS 标准静态地图文件
src/maze_robot/map/my_maze_map.pgm 	地图图像文件
src/maze_robot/map/my_maze_map.yaml 	地图配置文件

src\maze_robot\models Gazebo 	仿真专用三维模型文件夹
src\maze_robot\models\enemy_model\materials\scripts\enemy.material 	敌军模型
src\maze_robot\models\friend1_model\materials\scripts\friend1.material 	友军模型

src\maze_robot\models\friend2_model\materials\scripts\friend2.material 	友军模型
src\maze_robot\models\hostage_model\materials\scripts\hostage.material 	人质模型

src\maze_robot\param 	存放 YAML 参数配置文件
src\maze_robot\param\costmap_common_params.yaml 	代价地图通用参数
src\maze_robot\param\global_costmap_params.yaml 	全局代价地图
src\maze_robot\param\local_costmap_params.yaml 	局部代价地图
src\maze_robot\param\teb_local_planner_params.yaml 	TEB 局部路径规划器参数
src/maze_robot/scripts 	存放 Python 可执行脚本（ROS 功能节点）
src/maze_robot/scripts/waypoints_navigator.py 	路径点录制
src/maze_robot/scripts/record_waypoints.py 	航点巡航

src/maze_robot/worlds/my_maze_map.world 	存放 Gazebo 仿真世界文件

src/maze_robot/xacro/ 	存放 Xacro 机器人描述文件
src\maze_robot\xacro\base_inertia.xacro 	底座模型与物理参数
src\maze_robot\xacro\camera_inertia.xacro 	相机模型与物理参数
src\maze_robot\xacro\controller.xacro 	机器人运动控制器
src\maze_robot\xacro\inertia.xacro 	封装惯性矩阵算法
src\maze_robot\xacro\kinect.xacro Kinect 	深度相机模型
src\maze_robot\xacro\laser_inertia.xacro 	激光雷达模型与物理参数
src\maze_robot\xacro\robot_gazebo.xacro 	给模型添加 Gazebo 仿真插件
src\maze_robot\xacro\sensor.xacro 	所有传感器汇总文件

src/visual_detect/ 	视觉功能包
src/visual_detect/detect_node.py 	视觉检测 ROS 节点
src/visual_detect/models/best.onnx 	训练好的图像识别模型
src\visual_detect\CMakeLists.txt 	编译配置文件
