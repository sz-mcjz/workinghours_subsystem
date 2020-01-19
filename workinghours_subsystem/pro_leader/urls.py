from django.urls import path

from pro_leader import pro_leader_api

urlpatterns = [
    path('index/', pro_leader_api.pro_leader_index, name='pro_leader_index'),
    path('projects/', pro_leader_api.my_project, name='pro_leader_projects'),
    path('staffmanage/', pro_leader_api.staffmanage, name='pro_leader_staffmanage'),
    path('attendance/', pro_leader_api.attendance, name='pro_leader_attendance'),
    path('attendancerecode/', pro_leader_api.attendancerecode, name='pro_leader_attendancerecode'),
    path('timerecord/', pro_leader_api.timerecord, name='pro_leader_timerecord'),
    path('approve/', pro_leader_api.approve, name='pro_leader_approve'),

    # 我的项目
    path('mine/pro/', pro_leader_api.pro_leader_mine_pro, name='pro_leader_mine_pro'),
    # 新增工人
    path('add/worker/', pro_leader_api.pro_leader_add_worker, name='pro_leader_add_worker'),
    # 修改工人信息
    path('change/worker/', pro_leader_api.pro_leader_change_worker, name='pro_leader_change_worker'),
    # 工人退场或回厂
    path('exitorenter/worker/', pro_leader_api.pro_leader_exitorenter, name='pro_leader_exitorenter'),
    # 查询未录当天信息的工人
    path('notinput/worker/', pro_leader_api.pro_leader_notinput, name='pro_leader_notinput'),
    # 考勤数据录入
    path('attend/worker/', pro_leader_api.pro_leader_attend, name='pro_leader_attend'),
    # 工时信息接口
    path('workhours/info/', pro_leader_api.pro_leader_workhours, name='pro_leader_workhours'),
    # 考勤历史 工时信息申请修改接口
    path('workhours/applymodify/', pro_leader_api.pro_leader_workhoursapplymodify, name='pro_leader_workhoursapplymodify'),
    # 展示修改数据
    path('show/modify/', pro_leader_api.pro_leader_modifier, name='pro_leader_modifier'),
    # 展示我的项目数据
    path('show/project/', pro_leader_api.pro_leader_project, name='pro_leader_project'),
    # 审批信息
    path('approve/info/', pro_leader_api.pro_leader_approve, name='pro_leader_approve'),
]
