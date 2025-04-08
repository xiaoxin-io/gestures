import cv2
import threading
import mediapipe as mp
import os
import tempfile
import tkinter as tk
from PIL import Image, ImageTk


class HandShibie:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, minTrackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        self.current_left_gesture = None  # 当前左手手势
        self.current_right_gesture = None  # 当前右手手势

        # 创建手部检测模型
        self.hand_shibie = mp.solutions.hands.Hands(static_image_mode=mode,
                                                    max_num_hands=maxHands,
                                                    min_detection_confidence=detectionCon,
                                                    min_tracking_confidence=minTrackCon)
        self.drawer = mp.solutions.drawing_utils  # 画图工具
        # 手势映射
        self.current_gesture = None  # 当前正在播放的手势
        self.video_thread = None  # 视频播放线程
        self.stop_video_flag = False  # 停止视频播放标志

    def process(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # RGB格式
        self.hands_data = self.hand_shibie.process(img_rgb)  # 处理图像
        if draw and self.hands_data.multi_hand_landmarks:  # 绘制手部关节
            for handlms in self.hands_data.multi_hand_landmarks:
                self.drawer.draw_landmarks(img, handlms, mp.solutions.hands.HAND_CONNECTIONS)

    def find_position(self, img):
        """ 获取手部位置 """
        hand_position = {'Left': {}, 'Right': {}}
        h, w, _ = img.shape

        if self.hands_data.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(self.hands_data.multi_hand_landmarks):
                label = self.hands_data.multi_handedness[i].classification[0].label
                hand_lms = hand_landmarks.landmark
                for id, lm in enumerate(hand_lms):
                    x, y = int(lm.x * w), int(lm.y * h)
                    hand_position[label][id] = [x, y]
        return hand_position


    def detect_gesture(self, hand_landmarks):
        """ 检测手势并返回识别结果 """
        left_gesture, right_gesture = None, None

        right_hand = hand_landmarks.get('Right', {})
        if 4 in right_hand:
            right_gesture = self.process_gesture(right_hand, "Right")

        left_hand = hand_landmarks.get('Left', {})
        if 4 in left_hand:
            left_gesture = self.process_gesture(left_hand, "Left")

        return left_gesture, right_gesture

    def process_gesture(self, hand, hand_side):
        """ 处理单只手的手势识别逻辑 """
        if not hand or 4 not in hand:
            return None

        # 提取关键点
        thumb_tip = hand[4]  # 拇指尖
        index_tip = hand[8]  # 食指尖
        middle_tip = hand[12]  # 中指尖
        ring_tip = hand[16]  # 无名指尖

        # 识别手势
        gesture = None
        if index_tip[1] > thumb_tip[1] and middle_tip[1] > thumb_tip[1]:
            gesture = 0  # 石头
        elif index_tip[1] < thumb_tip[1] and middle_tip[1] < thumb_tip[1] and ring_tip[1] < thumb_tip[1]:
            gesture = 5  # 布
        elif index_tip[1] < thumb_tip[1] and middle_tip[1] < thumb_tip[1] and ring_tip[1] > thumb_tip[1]:
            gesture = 2  # 剪刀
        elif index_tip[1] > thumb_tip[1] and middle_tip[1] < thumb_tip[1]:
            gesture = 'middle_finger'  # 中指

        # 根据手势触发视频播放
        self.trigger_video(gesture, hand_side)
        return gesture

    def trigger_video(self, gesture, hand_side):
        """ 触发视频播放 """
        # 左手或右手分别管理
        if hand_side == "Left" and gesture != self.current_left_gesture:
            self.play_gesture_video(gesture, "Left")
            self.current_left_gesture = gesture
        elif hand_side == "Right" and gesture != self.current_right_gesture:
            self.play_gesture_video(gesture, "Right")
            self.current_right_gesture = gesture

    def play_gesture_video(self, gesture, hand_side):
        """ 根据手势播放对应视频 """
        # 手势与视频映射
        video_mapping = {
            0: 'D:\\AI\\gestures\\images\\00.mp4',  # 石头
            5: 'D:\\AI\\gestures\\images\\11.mp4',  # 布
            2: 'D:\\AI\\gestures\\images\\22.mp4',  # 剪刀
        }

        if gesture in video_mapping:
            video_path = video_mapping[gesture]
            self.play_video(video_path)
        else:
            print(f"{hand_side} 手未识别到有效手势或无需播放视频。")

    def play_video(self, video_path):
        """播放视频"""
        def video_thread():
            cap = cv2.VideoCapture(video_path)
            window_name = "gestures"

            # 创建窗口并设置为可调整大小
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 400, 600)  # 设置窗口大小
            cv2.moveWindow(window_name, 400, 100)  # 设置窗口位置

            while cap.isOpened():
                if self.stop_video_flag:  # 检测是否需要停止播放
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                # 如果视频分辨率不匹配，调整帧的大小
                frame = cv2.resize(frame, (800, 600))  # 调整帧为固定尺寸
                cv2.imshow(window_name, frame)

                if cv2.waitKey(30) & 0xFF == ord('q'):  # 按 Q 键退出
                    break

            cap.release()
            cv2.destroyAllWindows()

        # 停止之前的视频播放
        self.stop_video()
        self.stop_video_flag = False

        # 创建新线程播放视频
        self.video_thread = threading.Thread(target=video_thread, daemon=True)
        self.video_thread.start()

    def stop_video(self):
        """停止当前播放的视频"""
        self.stop_video_flag = True
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join()
