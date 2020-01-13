from django.urls import path

from boss import boss_api

urlpatterns = [
    path('index/', boss_api.boss_index, name='boss_index'),
]
