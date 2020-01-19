from django.db import models

"""
公司员工相关表
"""


# 部门
class Department(models.Model):
    department_id = models.AutoField(primary_key=True)  # 部门id
    name = models.CharField(max_length=125)  # 部门名

    class Meta:
        db_table = 'mcjz_department'


# 员工
class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)  # 员工id
    username = models.CharField(max_length=125)  # 员工姓名
    id_card = models.CharField(max_length=18)  # 员工编号
    department = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='staff_department_id')  # 部门
    telephone = models.CharField(max_length=11)  # 手机号码
    password = models.CharField(max_length=125)  # 密码
    icon = models.CharField(max_length=255)  # 头像

    class Meta:
        db_table = 'mcjz_staff'


"""
项目相关表
"""


# 项目表
class Project(models.Model):
    project_id = models.AutoField(primary_key=True)  # 项目id
    project_name = models.CharField(max_length=255, unique=True)  # 项目名
    project_leader = models.ForeignKey('Staff', on_delete=models.DO_NOTHING, related_name='project_staff_id')
    start_timer = models.DateField(auto_now_add=True)  # 开始时间
    overtime = models.CharField(max_length=30)  # 结束时间
    note = models.TextField()  # 备注

    class Meta:
        db_table = 'mcjz_project'


""""
项目上工人相关表
"""


# 工人工种类型
class WorkerType(models.Model):
    worker_type_id = models.AutoField(primary_key=True)  # 工种id
    type_name = models.CharField(max_length=125)  # 工种类型

    class Meta:
        db_table = 'mcjz_worker_type'


# 工人信息表
class WorkerInfo(models.Model):
    worker_id = models.AutoField(primary_key=True)  # 员工id
    project_name = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='info_project_id')  # 所属项目
    worker = models.CharField(max_length=100)  # 工人姓名
    id_number = models.CharField(max_length=30)  # 身份证号码
    phone_nmber = models.CharField(max_length=20)  # 手机号
    work_type = models.ForeignKey('WorkerType', on_delete=models.DO_NOTHING, related_name='info_worker_type_id')  # 工种类型
    status = models.IntegerField(default=1)  # 员工状态
    entry_data = models.DateField(auto_now_add=True)  # 入场时间
    leave_data = models.DateField(null=True)  # 离场时间
    das_salary = models.IntegerField()  # 日薪标准

    class Meta:
        db_table = 'mcjz_worker_info'


# 审批表记录表
class ApproveRecode(models.Model):
    record_id = models.AutoField(primary_key=True)  # 记录id
    worker_info_id = models.ForeignKey("WorkerInfo", on_delete=models.CASCADE,
                                       related_name='info_change_worker_id')  # 员工信息关联
    submit_date = models.DateField(auto_now_add=True)  # 审核提交日期
    column = models.CharField(max_length=30)  # 修改的字段
    data_date = models.DateField()  # 数据日期
    manager = models.CharField(max_length=30)  # 提交人
    original_data = models.CharField(max_length=200)  # 原始值
    change_data = models.CharField(max_length=200)  # 修改值
    note = models.TextField()  # 提交人备注
    status = models.IntegerField(default=0)  # 提交的审批申请状态  0 是未审批 1 是审批通过 2 审批未通过
    approver = models.CharField(max_length=30)  # 审批人
    approver_note = models.TextField() # 审批人备注   老板不同意，为什么
    working_hours = models.ForeignKey("WorkerHours",null=True,on_delete=models.CASCADE,related_name="worker_hours")
class Meta:
    db_table = 'mcjz_approve_recode'


# 工时信息表
class WorkerHours(models.Model):
    working_hours_id = models.AutoField(primary_key=True)  # 工时id
    worker_info_id = models.ForeignKey("WorkerInfo", on_delete=models.CASCADE,
                                       related_name='worker_hours_worker_id')  # 工人信息关联
    write_data = models.DateField()  # 填写时间
    writer = models.CharField(max_length=125)  # 填报人
    pname = models.CharField(max_length=125)  # 项目名称
    work_day = models.DecimalField(max_digits=16, decimal_places=2)  # 正常工日 (单位：天)
    overtime = models.DecimalField(max_digits=16, decimal_places=2)  # 加班工日(单位：天)
    day_salary = models.DecimalField(max_digits=16, decimal_places=2)  # 当日工资
    over_salary = models.DecimalField(max_digits=16, decimal_places=2)  # 加班工资
    salary = models.DecimalField(max_digits=16, decimal_places=2)  # 发放工资
    note = models.TextField()  # 备注
    project_id = models.ForeignKey("Project", on_delete=models.DO_NOTHING,null=True,
                                       related_name='wh_project_id')

    class Meta:
        db_table = 'mcjz_worker_hours'


# 信息修改表(记录提交到修改审批完成的工时，财务修改的个人工资标准)
class WorkerHoursChange(models.Model):
    record_id = models.AutoField(primary_key=True)  # 工时修改id
    worker_info_id = models.ForeignKey("WorkerInfo", on_delete=models.CASCADE,
                                       related_name='record_worker_id')  # 工人信息关联
    change_date = models.DateField(auto_now_add=True)  # 修改时间
    column = models.CharField(max_length=30)  # 字段  比如说修改了工资
    data_date = models.DateField()  # 上一次修改该字段的时间
    manager = models.CharField(max_length=30)  # 修改人
    original_data = models.CharField(max_length=200)  # 原始值
    change_data = models.CharField(max_length=200)  # 修改值
    note = models.TextField()  # 备注
    status = models.IntegerField(default=0,null=True)  # 提交的审批申请状态  0 是未审批 1 是审批通过 2 审批未通过
    approver = models.CharField(max_length=30,null=True)  # 审批人
    approver_note = models.TextField(null=True)  # 审批人备注   老板不同意，为什么
    working_hours = models.ForeignKey("WorkerHours", null=True, on_delete=models.CASCADE, related_name="worker_hours_change")

    class Meta:
        db_table = 'mcjz_hours_change'
