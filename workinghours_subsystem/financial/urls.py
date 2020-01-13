from django.urls import path

from financial import financial_api

urlpatterns = [
    path('index/', financial_api.financial_index, name='financial_index'),
]
