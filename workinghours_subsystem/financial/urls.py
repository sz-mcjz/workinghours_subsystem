from django.urls import path

from financial import financial_api

urlpatterns = [
    # 财务 首页
    path('index/', financial_api.financial_index, name='financial_index'),
    # 财务项目信息接口
    path('projectinfo/', financial_api.financial_projectinfo, name='financial_projectinfo'),
    # 财务工资发放
    path('salarypay/', financial_api.financial_salarypay, name='financial_salarypay'),
    # 财务 审批
    path('approve/', financial_api.financial_approve, name='financial_approve'),
    # 财务 修改记录 midify
    path('modifyrecode/', financial_api.financial_modifyrecode, name='financial_modifyrecode'),
    # 财务与总经共用 统计分析
    path('analysis/', financial_api.financial_analysis, name='financial_analysis'),
    # 项目信息数据接口
    path('data/projectinfo/', financial_api.financial_data_projectinfo, name='financial_data_projectinfo'),
    # 工资发放数据接口
    path('pay/salary/', financial_api.financial_data_paysalary, name='financial_data_paysalary'),
    # 工时审批
    path('hoursapproval/', financial_api.financial_data_hoursapproval, name='financial_data_hoursapproval'),
    # 工时修改记录查询
    path('hoursrecode/', financial_api.financial_data_hoursrecode, name='financial_data_hoursrecode'),
    # 统计分析 页面返回
    path('statisticMonth/', financial_api.statisticMonth, name='statisticMonth'),
    path('statisticSingle/', financial_api.statisticSingle, name='statisticSingle'),
    path('statisticTypeWork/', financial_api.statisticTypeWork, name='statisticTypeWork'),
]
