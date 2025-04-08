from django.urls import path
from .views.app import index  # 导入你的视图函数
from .views.app import video_feed  # 如果有视频流视图

urlpatterns = [
    path('', index, name='index'),  # 主页路由
    path('video_feed/', video_feed, name='video_feed'),  # 视频流路由
]