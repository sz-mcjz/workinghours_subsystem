from django.urls import path

from pro_leader import pro_leader_api

urlpatterns = [
    path('index/', pro_leader_api.pro_leader_index, name='pro_leader_index'),
]
