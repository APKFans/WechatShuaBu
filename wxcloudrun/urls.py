"""wxcloudrun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from wxcloudrun import views
from django.conf.urls import url, re_path
from django.views.static import serve
from django.urls import path

from wxcloudrun.views import shua_bu, reply
from wxcloudrun.settings import STATIC_ROOT

urlpatterns = (
    # 刷步
    path('api/shuabu', shua_bu),
    # 消息处理
    path('api/reply', reply),
    # 获取主页
    url(r'(/)?$', views.index),
    # 静态文件
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),  # static文件
)
