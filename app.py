from flask import Flask, render_template, Response
import cv2
import numpy as np
from handutils3 import HandShibie
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 初始化摄像头和手势识别
camera = cv2.VideoCapture(0)
hand_shibie = HandShibie()
GESTURE_RPS = {0: "石头", 2: "剪刀", 5: "布"}

def generate_frames():
    while True:
        success, img = camera.read()
        if not success:
            break
        img = cv2.flip(img, 1)  # 镜像翻转
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

        yield (b'--frame\r\n'  #定义了一种边界标识符。这是消息的开始，用于分隔多个数据部分
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n') #frame 变量应该是包含一帧视频数据的字节对象，它是在 generate_frames() 函数中生成的。b'\r\n': 结束当前部分的数据

        #完整的yield 语句构成了一个多部分的MIME消息，它允许浏览器接收和渲染持续的数据流（在这种情况下是视频帧）

@app.route('/') #Flask 的路由装饰器，它告诉 Flask 当访问根 URL (/) 时应该调用 index() 函数。
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)