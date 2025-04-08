from django.http import StreamingHttpResponse
from django.views import View
import cv2
import numpy as np
from handutils1 import HandShibie
from PIL import Image, ImageDraw, ImageFont

# 初始化摄像头和手势识别
camera = cv2.VideoCapture(0)
hand_shibie = HandShibie()
GESTURE_RPS = {0: "石头", 2: "剪刀", 5: "布"}

class VideoFeedView(View):
    def generate_frames(self):
        while True:
            success, img = camera.read()
            if not success:
                break
            img = cv2.flip(img, 1)  # 镜像翻转

            # 处理手势识别逻辑
            hand_shibie.process(img)
            position = hand_shibie.find_position(img)

            left_finger = position['Left'].get(8, None)
            if left_finger:
                cv2.circle(img, (left_finger[0], left_finger[1]), 10, (0, 0, 255), cv2.FILLED)

            right_finger = position['Right'].get(8, None)
            if right_finger:
                cv2.circle(img, (right_finger[0], right_finger[1]), 10, (0, 255, 0), cv2.FILLED)

            left_gesture, right_gesture = hand_shibie.detect_gesture(position)

            # 使用 Pillow 绘制中文
            pil_img = Image.fromarray(img)
            draw = ImageDraw.Draw(pil_img)

            # 指定要使用的中文字体路径和大小
            font_path = r"C:\Windows\Fonts\msyh.ttc"  # 替换为您本地的中文字体路径
            font = ImageFont.truetype(font_path, 40)

            # 绘制手势信息
            if right_gesture is not None:
                right_text = f"右手: {GESTURE_RPS.get(right_gesture, '未知')}"
                draw.text((10, 100), right_text, font=font, fill=(255, 255, 255))
            if left_gesture is not None:
                left_text = f"左手: {GESTURE_RPS.get(left_gesture, '未知')}"
                draw.text((10, 50), left_text, font=font, fill=(255, 255, 255))

            img = np.array(pil_img)
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'  
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def get(self, request):
        return StreamingHttpResponse(self.generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')