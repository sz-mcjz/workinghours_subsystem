from django.urls import path

from boss import boss_api

urlpatterns = [
    # BOSS 首页
    path('index/', boss_api.boss_index, name='boss_index'),
    # BOSS 创建项目
    path('create/pro/', boss_api.boss_create_project, name='boss_create_pro'),
    # BOSS 删除项目
    path('delete/pro/', boss_api.boss_delete_pro, name='boss_delete_pro'),
    # BOSS 修改项目
    path('modify/pro/', boss_api.boss_modify_pro, name='boss_modify_pro'),

    path('createItem/', boss_api.createItem, name='createItem'),
    path('personAdmin/', boss_api.personAdmin, name='personAdmin'),
    path('salaryAdmin/', boss_api.salaryAdmin, name='salaryAdmin'),
]
