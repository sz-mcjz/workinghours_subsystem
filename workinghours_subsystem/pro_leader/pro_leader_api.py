import datetime
import json

from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render_to_response

from db.models import Staff, Project, WorkerInfo, WorkerType, WorkerHours, WorkerHoursChange, ApproveRecode
from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY


# Leader 首页
def pro_leader_index(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if (not user) or (user.department_id != 7):
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    data = {
        'username': user.username,
        'icon': user.icon,
        'department': user.department.name,
        'telephone': user.telephone,
    }
    return render_to_response('pro_leader/index.html', context=data)


# Leader 新增员工
def pro_leader_add_worker(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'GET':
        worker_type = list(WorkerType.objects.all().values())
        data = {
            'code': 1,
            'msg': '数据请求成功',
            'data': {
                'worker_type': worker_type,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})

    elif request.method == 'POST':
        worker_name = request.POST.get('worker_name')
        worker_pro_name_id = request.POST.get('pro_name_id')
        worker_id_card = request.POST.get('id_card')
        worker_telephone = request.POST.get('telephone')
        worker_type_id = request.POST.get('type_id')
        worker_das_salary = request.POST.get('das_salary')

        new_worker = WorkerInfo()
        new_worker.worker = worker_name
        new_worker.project_name = Project.objects.get(project_id=worker_pro_name_id)
        new_worker.id_number = worker_id_card
        new_worker.phone_nmber = worker_telephone
        new_worker.work_type = WorkerType.objects.get(worker_type_id=worker_type_id)
        new_worker.das_salary = worker_das_salary
        new_worker.save()
        return JsonResponse({'code': 1, 'msg': '新增员工成功'})


# Leader 我的项目
def pro_leader_mine_pro(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'GET':
        mine_pro = [mine_pro for mine_pro in
                    Project.objects.filter(project_leader=Staff.objects.get(telephone=uuid)).values()]
        data = {
            'code': 1,
            'msg': '请求成功',
            'data': {
                'mine_pro': mine_pro,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})
    elif request.method == 'POST':
        pro_id = request.POST.get('pro_id')
        page = int(request.POST.get('page', 1))
        _pro_worker = sorted(list(WorkerInfo.objects.filter(project_name_id=pro_id).values()),
                             key=lambda x: x['status'], reverse=True)
        paginator = Paginator(_pro_worker, 15, 2)
        page_num = paginator.num_pages
        _pro_worker = [obj for obj in paginator.page(page)]
        for worker in _pro_worker:
            worker['pro_name'] = Project.objects.get(project_id=worker['project_name_id']).project_name
            worker['worker_type'] = WorkerType.objects.get(worker_type_id=worker['work_type_id']).type_name
            if worker['status'] == 1:
                worker['status'] = '在场'
            else:
                worker['status'] = '离场'
            if worker['leave_data'] is None:
                worker['leave_data'] = '--'
        data = {
            'code': 1,
            'msg': '请求成功',
            'data': {
                'workers': _pro_worker,
                'page_num': page_num,
                'nowpage': page,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})


def pro_leader_exitorenter(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'GET':
        return JsonResponse(data="data", json_dumps_params={'ensure_ascii': False})
    elif request.method == 'POST':
        workerid = request.POST.get("workerid")
        worker = WorkerInfo.objects.get(worker_id=workerid)
        if worker.status == 1:
            worker.status = 0
        elif worker.status == 0:
            worker.status = 1
        worker.save()

        return JsonResponse(data={"code": 1, "msg": "操作成功"}, json_dumps_params={'ensure_ascii': False})


# 工人资料修改
def pro_leader_change_worker(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == "GET":
        return JsonResponse(data="data", json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        workerid = request.POST.get("workerid")
        workername = request.POST.get("workername")
        workeridcard = request.POST.get("workeridcard")
        workertelephone = request.POST.get("workertelephone")
        workertype = request.POST.get("workertype")

        worke = WorkerInfo.objects.get(worker_id=workerid)
        if worke:
            worke.worker = workername
            worke.id_number = workeridcard
            worke.phone_nmber = workertelephone
            worke.work_type_id = workertype
            worke.save()
            return JsonResponse(data={"code": 1, "msg": "修改成功"}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(data={"code": 0, "msg": "修改失败"}, json_dumps_params={'ensure_ascii': False})


# 工人工时录入
def pro_leader_notinput(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == "GET":
        pro_id = request.GET.get('pro_id')
        now_time = datetime.datetime.now()
        # 取时间等于今天的 项目名字为 XXX 的 工人id，因为明天他也要可以填写
        previnfo = list([i['worker_info_id_id'] for i in WorkerHours.objects.filter(pname=Project.objects.get(
            project_id=pro_id).project_name, write_data=now_time, salary=0).values(
            "worker_info_id_id")])

        page = int(request.GET.get('page', 1))
        # 排除掉以上工人的 id，读取且状态为1的工人
        _pro_worker = list(
            WorkerInfo.objects.filter(~Q(worker_id__in=previnfo), project_name_id=pro_id, status=1).values())

        paginator = Paginator(_pro_worker, 15, 2)
        page_num = paginator.num_pages
        _pro_worker = [obj for obj in paginator.page(page)]
        for worker in _pro_worker:
            worker['pro_name'] = Project.objects.get(project_id=worker['project_name_id']).project_name
            worker['worker_type'] = WorkerType.objects.get(worker_type_id=worker['work_type_id']).type_name
            if worker['status'] == 1:
                worker['status'] = '在场'
            else:
                worker['status'] = '离场'
            if worker['leave_data'] is None:
                worker['leave_data'] = '--'
        data = {
            'code': 1,
            'msg': '请求成功',
            'data': {
                'workers': _pro_worker,
                'page_num': page_num,
                'nowpage': page,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        return JsonResponse(data="", json_dumps_params={'ensure_ascii': False})


# Leader 工人考勤
def pro_leader_attend(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'POST':
        # 填报人 查询
        leader = Staff.objects.get(telephone=uuid)
        attend_data = request.POST.get('attendance_data')
        pro_id = request.POST.get('pro_id')
        attend_data = json.loads(attend_data)
        print(attend_data)
        if len(attend_data) == 0:
            return JsonResponse({'code': 0, 'msg': '录入列表为空', "data": pro_id}, json_dumps_params={'ensure_ascii': False})

        pro_id = request.POST.get('pro_id')
        for v in attend_data:
            try:
                workerhours = WorkerHours()
                workerhours.worker_info_id_id = v['id']
                workerhours.write_data = datetime.datetime.now()
                workerhours.writer = leader.username
                workerhours.pname = Project.objects.get(project_id=pro_id).project_name
                workerhours.work_day = float(v['normal'])
                workerhours.overtime = float(v['extra'])
                workerhours.day_salary = float(v['normal']) * float(
                    WorkerInfo.objects.get(worker_id=v['id']).das_salary)
                workerhours.over_salary = float(v['extra']) * float(
                    WorkerInfo.objects.get(worker_id=v['id']).das_salary)
                workerhours.salary = 0
                workerhours.note = v['note']
                workerhours.project_id_id = pro_id
                workerhours.save()
            except:
                return JsonResponse({'code': 0, 'msg': '有部分考勤数据录入失败'}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse({'code': 1, 'msg': '考勤数据录入成功', 'data': {'pro_id': pro_id}},
                            json_dumps_params={'ensure_ascii': False})


# 考勤历史数据  显示页面为 timerecord/
def pro_leader_workhours(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})
    if request.method == "GET":
        lastdate = WorkerHours.objects.filter(writer=user.username).values("write_data").last()
        date = request.GET.get("date")
        if not date:
            date = lastdate['write_data']

        hourinfo = WorkerHours.objects.filter(write_data=date, writer=user.username)

        hourinfo2 = []
        for v in hourinfo:
            # 需要优化
            v.worker_name = v.worker_info_id.worker
            v.worker_type = v.worker_info_id.work_type.type_name
            dic = v.__dict__
            dic.pop('_state')
            hourinfo2.append(dic)
        data = {
            "code": 0,
            "msg": "操作成功",
            "data": hourinfo2,
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})
    elif request.method == 'POST':
        return JsonResponse(data={"code": 0, "msg": ""}, json_dumps_params={'ensure_ascii': False})


def pro_leader_project(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == "GET":
        project_id = request.GET.get("pro_id")
        user = Staff.objects.get(telephone=uuid)
        if not project_id:
            name = user.project_staff_id.all()  # 反省查询项目对象
            project_id = name[0].project_id
            project_name = name[0].project_name
        else:
            project_name = Project.objects.get(project_id=project_id).project_name
        # project_id = name[0].project_id  # 取项目ID
        # project_name = name[0].project_name  # 取项目ID

        result = WorkerHours.objects.filter(pname=project_name).values('worker_info_id_id').annotate(Sum('day_salary'))
        result1 = WorkerHours.objects.filter(pname=project_name).values('worker_info_id_id').annotate(
            Sum('over_salary'))
        result2 = WorkerHours.objects.filter(pname=project_name).values('worker_info_id_id').annotate(Sum('salary'))
        result3 = WorkerHours.objects.filter(pname=project_name).values('worker_info_id_id').annotate(Sum('work_day'))
        result4 = WorkerHours.objects.filter(pname=project_name).values('worker_info_id_id').annotate(Sum('overtime'))

        workers = list(WorkerInfo.objects.filter(project_name_id=project_id).values())

        for i, w in enumerate(workers):
            w['work_type'] = WorkerType.objects.get(worker_type_id=w['work_type_id']).type_name
            if w['status'] == 1:
                w['status'] = '在场'
            else:
                w['status'] = '离场'
            if result3:
                w['day_salary'] = result[i]['day_salary__sum']
                w['over_salary'] = result1[i]['over_salary__sum']
                w['all_salary'] = w['day_salary'] + w['over_salary']
                w['salary'] = result2[i]['salary__sum']
                w['work_day'] = result3[i]['work_day__sum']
                w['overtime'] = result4[i]['overtime__sum']
                w['all_day'] = w['work_day'] + w['overtime']

            else:
                w['day_salary'] = "--"
                w['over_salary'] = "--"
                w['all_salary'] = "--"
                w['salary'] = "--"
                w['work_day'] = "--"
                w['overtime'] = "--"
                w['all_day'] = "--"

        data = {
            'code': 1,
            'msg': '请求成功',
            'data': {
                'workers': workers,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})


# 审批信息
def pro_leader_approve(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    user = Staff.objects.get(telephone=uuid).username
    info = ApproveRecode.objects.filter(manager=user)
    info2 = []
    for i in info:
        i.name = i.worker_info_id.worker
        i.project_name = i.worker_info_id.project_name.project_name
        dic = i.__dict__
        dic.pop('_state')
        if dic['status'] == 0:
            dic['status'] = '未审核'
        if dic['status'] == 1:
            dic['status'] = '通过'
        if dic['status'] == 2:
            dic['status'] = '未通过'
        info2.append(dic)
    info2 = sorted(info2, key=lambda x: x['status'])
    data = {
        'code': 1,
        'msg': '请求成功',
        'data': {
            'info': info2,
        }
    }
    return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})


def pro_leader_modifier(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    modifier = list(WorkerHoursChange.objects.filter(manager=user.username).values())
    for m in modifier:
        m['worker_name'] = WorkerInfo.objects.get(worker_id=m['worker_info_id_id']).worker
    data = {
        'code': 1,
        'msg': '请求成功',
        'data': {
            'modifier': modifier,
        }
    }
    return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})


# 工时信息申请修改
def pro_leader_workhoursapplymodify(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})
    if request.method == "GET":
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        # 需要申请修改的 工人 id
        worker_id = request.POST.get("worker_id")
        # 需要申请修改的 记录 id
        work_hour_id = request.POST.get("work_hour_id")
        nomal = request.POST.get("nomal")
        overtime = request.POST.get("overtime")
        note = request.POST.get("note")

        # 查询原来的记录
        wh = WorkerHours.objects.get(working_hours_id=work_hour_id)
        # 审批记录表新建数据
        if not (wh.work_day == float(nomal)):
            try:
                ar = ApproveRecode()
                ar.worker_info_id_id = worker_id
                ar.submit_date = datetime.datetime.now()  # 申请时间为今天
                ar.column = "非加班工日"  # work_day 是非加班工时
                ar.manager = user.username
                ar.original_data = wh.work_day  # 原始数据为刚刚查出来的数据
                ar.change_data = nomal  # 新数据为刚刚获取的
                ar.note = note
                ar.status = 0  # 默认为还未审批
                ar.approver = ""  # 默认同意申请的人为空
                ar.approver_note = ""  # 默认评语为空
                ar.worker_info_id_id = worker_id  # 所修改的人的id为穿传进来的id
                ar.data_date = datetime.datetime.now()
                ar.working_hours_id = wh.working_hours_id  # 记录的id
                ar.save()
            except:
                return JsonResponse(data={"code": 0, "msg": "申请失败"}, json_dumps_params={'ensure_ascii': False})
        if not (wh.overtime == float(overtime)):
            try:
                ar = ApproveRecode()
                ar.worker_info_id_id = worker_id
                ar.submit_date = datetime.datetime.now()  # 申请时间为今天
                ar.column = "加班工日"  # work_day 是非加班工时
                ar.manager = user.username
                ar.original_data = wh.overtime  # 原始数据为刚刚查出来的数据
                ar.change_data = overtime  # 新数据为刚刚获取的
                ar.note = note
                ar.status = 0  # 默认为还未审批
                ar.approver = ""  # 默认同意申请的人为空
                ar.approver_note = ""  # 默认评语为空
                ar.worker_info_id_id = worker_id  # 所修改的人的id为穿传进来的id
                ar.data_date = datetime.datetime.now()
                ar.working_hours_id = wh.working_hours_id  # 记录的id
                ar.save()
            except:
                return JsonResponse(data={"code": 0, "msg": "申请失败"}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(data={"code": 0, "msg": "申请成功"}, json_dumps_params={'ensure_ascii': False})


def my_project(request):
    return render_to_response('pro_leader/my_project.html')


def staffmanage(request):
    return render_to_response("pro_leader/staff_manage.html")


def attendance(request):
    time = datetime.datetime.now().date()
    return render_to_response("pro_leader/attendance.html", {'nowtime': time})


def attendancerecode(request):
    return render_to_response("pro_leader/attendance_record.html")


def approve(request):
    return render_to_response("pro_leader/approve.html")


def timerecord(request):
    return render_to_response("pro_leader/time_record.html")
