from django.urls import path, include

# 本路由禁止修改！！！
import db
from db import db_api

urlpatterns = [
    # 默认路由
    path('', db_api.login, name='login'),
    # 退出系统
    path('logout/', db_api.logout, name='logout'),
    # 修改密码
    path('profile/', db_api.profile, name='profile'),
    # boss api 子路由
    path('boss/', include('boss.urls')),
    # leader api 子路由
    path('leader/', include('pro_leader.urls')),
    # financial api 子路由
    path('financial/', include('financial.urls')),
]
