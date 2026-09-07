#!/usr/bin/env python3
import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import String
import onnxruntime as ort

COLLECT_DURATION   = 3.0  # 采集秒数
MIN_CONF_TO_RECORD = 0.3  # 低于此置信度的帧丢弃

class SoldierDetector:
    def __init__(self):
        rospy.init_node('soldier_detector', anonymous=True)

        model_path = '/home/key/catkin_wslianxi/src/visual_detect/best.onnx'
        self.session    = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name

        self.bridge  = CvBridge()
        self.classes = ['enemy', 'friend', 'hostage']

        self.collecting    = False
        self.collect_start = None
        self.current_zone  = None
        # 投票桶：key=label，value=置信度累计
        self.vote_bucket   = {}

        rospy.Subscriber('/camera/image_raw', Image, self.image_callback)
        rospy.Subscriber('/arrive_zone',      String, self.arrive_callback)

        rospy.loginfo("soldier_detector 节点启动成功！")
        rospy.spin()

    def arrive_callback(self, msg):
        self.current_zone  = msg.data
        self.collecting    = True
        self.collect_start = rospy.Time.now()
        self.vote_bucket   = {}
        rospy.loginfo("到达战区 %s，开始识别（%.1f 秒）..." % (
            self.current_zone, COLLECT_DURATION))

    def image_callback(self, msg):
        if not self.collecting:
            return

        elapsed = (rospy.Time.now() - self.collect_start).to_sec()
        if elapsed > COLLECT_DURATION:
            self._finalize()
            return

        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        label, conf = self._detect(frame)

        rospy.loginfo("[采集 %.1fs] %s (置信度:%.2f)" % (elapsed, label, conf))

        if conf >= MIN_CONF_TO_RECORD:
            self.vote_bucket[label] = self.vote_bucket.get(label, 0.0) + conf

    def _detect(self, frame):
        """整帧检测，返回置信度最高的单个标签"""
        img = cv2.resize(frame, (512, 512))
        img = img[:, :, ::-1].astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))[np.newaxis, :]

        outputs = self.session.run(None, {self.input_name: img})
        output  = outputs[0][0].T  # (N, 4+num_classes)

        best_label, best_conf = 'unknown', 0.0
        for det in output:
            scores   = det[4:]
            class_id = int(np.argmax(scores))
            conf     = float(scores[class_id])
            if conf > best_conf:
                best_conf  = conf
                best_label = self.classes[class_id]

        return best_label, best_conf

    def _finalize(self):
        self.collecting = False
        zone = self.current_zone
        self.current_zone = None

        if not self.vote_bucket:
            rospy.logwarn("战区 %s：采集窗口内无有效帧，识别失败" % zone)
            return

        best_label = max(self.vote_bucket, key=self.vote_bucket.get)

        enemy_count   = 1 if best_label == 'enemy'   else 0
        friend_count  = 1 if best_label == 'friend'  else 0
        hostage_count = 1 if best_label == 'hostage' else 0

        rospy.loginfo("═══ 战区 %s 识别结果：敌军%d人 友军%d人 人质%d人 ═══" % (
            zone, enemy_count, friend_count, hostage_count))

if __name__ == '__main__':
    try:
        SoldierDetector()
    except rospy.ROSInterruptException:
        pass
