from django.urls import path, include

# 本路由禁止修改！！！
urlpatterns = [
    # boss api 子路由
    path('boss/', include('boss.urls')),
    # leader api 子路由
    path('leader/', include('boss.urls')),
    # financial api 子路由
    path('financial/', include('boss.urls')),
]
