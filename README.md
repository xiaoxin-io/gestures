手势识别项目
项目介绍
这是一个基于 Flask 和 Django 的手势识别项目，使用 OpenCV 和 Mediapipe 实现了实时手势识别功能。项目支持识别“石头”、“剪刀”、“布”三种手势，并通过摄像头实时显示手势识别结果。
功能特点
实时手势识别：通过摄像头实时识别手势。
中文显示：支持在视频流中显示中文手势信息。
多手势支持：支持识别“石头”、“剪刀”、“布”三种手势。
视频流显示：通过 Flask 或 Django 提供视频流服务，可在浏览器中查看实时视频。
技术栈
后端：Flask、Django
手势识别：OpenCV、Mediapipe
图像处理：Pillow
前端：HTML
安装步骤
环境准备
确保已安装 Python 3.8 或更高版本。
安装必要的 Python 包：
pip install flask opencv-python mediapipe numpy pillow

Flask 版本
克隆项目代码：
git clone https://github.com/xiaoxin-io/gestures.git
cd gestures
运行 Flask 应用：
bash
复制
python app.py
打开浏览器，访问 http://127.0.0.1:8000 查看效果。

Django 版本
克隆项目代码：
git clone https://github.com/xiaoxin-io/gestures.git
cd gestures

安装 Django：
pip install django
运行 Django 应用：
python manage.py runserver
打开浏览器，访问 http://127.0.0.1:8000 查看效果。
项目结构
project-folder/
│
├── app.py                # Flask 应用入口
├── app2.py               # Django 视图文件
├── handutils3.py         # 手势识别工具类
├── index.html            # Flask 版本的前端页面
├── urls.py               # Django 的 URL 配置
├── video_feed.html       # Django 版本的视频流页面
└── README.md             # 项目说明文档
注意事项
确保摄像头正常工作。
根据实际情况调整 font_path，指定正确的中文字体路径。
如果使用 Django 版本，请确保 urls.py 中的路由配置正确。
