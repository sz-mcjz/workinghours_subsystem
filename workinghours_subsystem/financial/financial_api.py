import datetime
import json
from functools import reduce

from django.core.paginator import Paginator
import calendar
from django.db import connection
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response

from db.models import *
from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY


def financial_index(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    if (not user) or (user.department_id != 1 and user.department_id != 3):
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    data = {
        'username': user.username,
        'icon': user.icon,
        'department': user.department.name,
        'telephone': user.telephone,
    }
    return render_to_response('financial/index.html', context=data)


def financial_data_projectinfo(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'GET':
        mine_pro = list(Project.objects.all().values())

        data = {
            'code': 1,
            'msg': '请求成功',
            'data': {
                'mine_pro': mine_pro,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})
    elif request.method == 'POST':
        project_id = request.POST.get("pro_id")

        project_name = ''
        if not project_id:
            project = Project.objects.all().first()
            project_id = project.project_id
            project_name = project.project_name
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


# 工资发放遍所有 项目员工
def financial_data_paysalary(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})
    if request.method == "GET":
        pro_id = request.GET.get("pro_id")
        workers = WorkerInfo.objects.filter(project_name_id=pro_id)
        workers1 = []
        for v in workers:
            v.worker_type = v.work_type.type_name
            v.pro_name = v.project_name.project_name
            dic = v.__dict__
            dic.pop('_state')
            workers1.append(dic)
        data = {
            "code": 0,
            "msg": "操作成功",
            'data': {
                "workers": workers1,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})

    elif request.method == "POST":
        # 工资发放操作
        attend_data = request.POST.get('attendance_data')
        pro_id = request.POST.get('pro_id')
        attend_data = json.loads(attend_data)
        # 录入工资的人
        finan = Staff.objects.get(telephone=uuid)
        if len(attend_data) == 0:
            return JsonResponse({'code': 0, 'msg': '录入列表为空', "data": pro_id}, json_dumps_params={'ensure_ascii': False})

        for v in attend_data:
            try:
                workerhours = WorkerHours()
                workerhours.worker_info_id_id = v['id']
                workerhours.write_data = datetime.datetime.now()
                workerhours.writer = finan.username
                workerhours.pname = Project.objects.get(project_id=pro_id).project_name
                workerhours.work_day = 0
                workerhours.overtime = 0
                workerhours.day_salary = 0
                workerhours.over_salary = 0
                workerhours.salary = v['salary']
                workerhours.note = v['note']
                workerhours.project_id_id = pro_id
                workerhours.save()
            except:
                return JsonResponse({'code': 0, 'msg': '有部分数据录入失败'}, json_dumps_params={'ensure_ascii': False})

        return JsonResponse(data={"code": 1, "msg": "工资发放录入成功", 'data': {'pro_id': pro_id}},
                            json_dumps_params={'ensure_ascii': False})


# 工时审批
def financial_data_hoursapproval(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == "GET":
        modifier = ApproveRecode.objects.all()
        modifier1 = []
        for v in modifier:
            v.worker_name = v.worker_info_id.worker
            dic = v.__dict__
            dic.pop('_state')
            modifier1.append(dic)
        modifier1 = sorted(modifier1, key=lambda x: x['status'])
        data = {
            'code': 1,
            'msg': '请求成功',
            'data': {
                'modifier': modifier1,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        type = request.POST.get("type")
        recode_id = request.POST.get("recode_id")
        note = request.POST.get("note")
        ar = ApproveRecode.objects.get(record_id=recode_id)
        if not ar:
            return JsonResponse(data={"code": 0, "msg": "记录为空"}, json_dumps_params={'ensure_ascii': False})
        try:
            if type == "disagree":
                ar.approver = user.username
                ar.approver_note = note
                ar.status = 2  # 2是拒绝 0是未审核 1是同意
                ar.save()
            elif type == "agree":
                ar.approver = user.username
                ar.approver_note = note
                ar.status = 1  # 2是拒绝 0是未审核 1是同意
                if ar.column == "加班工日":
                    ar.working_hours.overtime = ar.change_data
                elif ar.column == "非加班工日":
                    ar.working_hours.work_day = ar.change_data
                whc = WorkerHoursChange()
                whc.change_date = datetime.datetime.now()
                whc.column = ar.column
                whc.data_date = ar.data_date
                whc.manager = ar.manager
                whc.original_data = ar.original_data
                whc.change_data = ar.change_data
                whc.note = ar.note
                whc.worker_info_id_id = ar.worker_info_id_id
                whc.working_hours_id = ar.working_hours_id
                whc.approver = ar.approver
                whc.approver_note = ar.approver_note
                whc.status = ar.status
                whc.save()
                ar.working_hours.save()
                ar.save()
        except:
            return JsonResponse(data={"code": 0, "msg": "操作失败"}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse(data={"code": 1, "msg": "操作成功"}, json_dumps_params={'ensure_ascii': False})


def financial_data_hoursrecode(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.get(telephone=uuid)
    if not user:
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == "GET":
        modifier = WorkerHoursChange.objects.all()
        modifier1 = []
        for v in modifier:
            v.worker_name = v.worker_info_id.worker

            dic = v.__dict__
            dic.pop('_state')
            modifier1.append(dic)
        data = {
            'code': 1,
            'msg': '请求成功',
            'data': {
                'modifier': modifier1,
            }
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})


'''-----------------------------------以下为统计分析模块--------------------------------'''


def statisticMonth(request):
    if request.method == "GET":

        # 查询当月的（不是近一个月）  人数 总工日 非加班工日 加班工日 总工资 非加班工资 加班工资 已发工资
        # 需要排除状态为 0 （退场） 的工人
        sql = """SELECT tm1.project_name,
                case  when tm1.zrs is null then 0 else tm1.zrs end zrs,
                case when (tm2.fjbgr+tm2.jbgr) is null then 0 else (tm2.fjbgr+tm2.jbgr) end zgr,
                case when tm2.fjbgr is null then 0 else tm2.fjbgr end fjbgr,
                case when tm2.jbgr is null then 0 else tm2.jbgr end jbgr,
                case when (tm2.fjbgz+tm2.jbgz) is null then 0 else (tm2.fjbgz+tm2.jbgz) end zgz,
                case when tm2.fjbgz is null then 0 else tm2.fjbgz end fjbgz,
                case when tm2.jbgz is null then 0 else tm2.jbgz end jbgz,
                case when tm2.yfgz is null then 0 else tm2.yfgz end yfgz
                FROM
                (
                select project_name,count(worker_id) zrs
                from mcjz_project a left join mcjz_worker_info b on a.project_id=b.project_name_id where b.status=1
                group by project_id ) tm1
                LEFT JOIN (
                SELECT pname,sum(work_day) fjbgr,sum(overtime) jbgr,sum(day_salary) fjbgz,sum(over_salary) jbgz,sum(salary) yfgz
                FROM mcjz_worker_hours where MONTH(write_data) = MONTH(NOW())
                GROUP BY pname ) tm2
                on  tm1.project_name = tm2.pname"""
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        result = [list(i) for i in result]

        cursor.close()
        return JsonResponse(data={"code": 1, "msg": "查询成功", "data": result}, json_dumps_params={'ensure_ascii': False})

    elif request.method == "POST":
        return render_to_response('analysis/statisticMonth.html')


# 对lis去重
def list_dict_removeal(_list):
    data_list = _list
    res = lambda x, y: x if y in x else x + [y]
    return reduce(res, [[], ] + data_list)


def domonth(result2):
    date = None
    if not result2:
        date = datetime.datetime.now()
    else:
        date = result2[0][0]
    day_list = calendar.monthcalendar(date.year, date.month)
    day_list = list(set([y for x in day_list for y in x]))[1:]  # 所有天数列表
    lis = []
    for i in day_list:
        lis.append({"daynum": i, "data": [0.00, 0.00, 0.00]})
    if result2:
        for index, i in enumerate(lis):
            for j in result2:
                if i['daynum'] == j[0].day:
                    lis[index] = {'daynum': j[0].day, "data": j[1:]}
    daylis = []
    z = []
    f = []
    j = []
    for v in lis:
        daylis.append(str(v["daynum"]) + "号")
        z.append(v['data'][0])
        f.append(v['data'][1])
        j.append(v['data'][2])

    return {"name": daylis, "total": z, "normal": f, "over": j}


def statisticSingle(request):
    if request.method == "GET":
        pro_id = request.GET.get("pro_id")
        pro = Project.objects.get(project_id=pro_id)
        if not pro:
            return JsonResponse(data={"code": 0, "msg": "未存在的项目"}, json_dumps_params={'ensure_ascii': False})
        # 查询单项目情况 指定 pro_Id 的但项目统计
        sql = """select 
                case  when tm1.zrs is null then 0 else tm1.zrs end zrs,
                case when (tm2.fjbgr+tm2.jbgr) is null then 0 else (tm2.fjbgr+tm2.jbgr) end zgr,
                case when tm2.fjbgr is null then 0 else tm2.fjbgr end fjbgr,
                case when tm2.jbgr is null then 0 else tm2.jbgr end jbgr,
                case when (tm2.fjbgz+tm2.jbgz) is null then 0 else (tm2.fjbgz+tm2.jbgz) end zgz,
                case when tm2.fjbgz is null then 0 else tm2.fjbgz end fjbgz,
                case when tm2.jbgz is null then 0 else tm2.jbgz end jbgz,
                case when tm2.yfgz is null then 0 else tm2.yfgz end yfgz,
                tm1.project_name
                from (select project_name,count(worker_id) zrs from mcjz_project a inner join mcjz_worker_info b on a.project_id=b.project_name_id and project_id=""" + str(
            pro.project_id) + """ where b.status=1 group by project_id) tm1 
                left join (SELECT pname,sum(work_day) fjbgr,sum(overtime) jbgr,sum(day_salary) fjbgz,sum(over_salary) jbgz,sum(salary) yfgz
                FROM mcjz_worker_hours GROUP BY pname) tm2 on tm1.project_name = tm2.pname"""
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        result1 = [list(i) for i in result]
        # 查询工资统计  按项目查询 按工时录入日期分组 统计总工日，加班工日和非加班工日,未填写日期不会显示
        sql = """
        SELECT write_data daynum,sum(day_salary)+sum(over_salary) zgz,sum(day_salary),sum(over_salary)
        FROM mcjz_worker_hours where pname='""" + pro.project_name + """' and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        result2 = [list(i) for i in result]

        result2 = domonth(result2)

        # ************人数统计
        # -- 请假的sql 发工资和工时都为0，上班的是有工时的
        # sql = """
        # SELECT write_data daynum,count(worker_info_id_id)
        # FROM mcjz_worker_hours a LEFT JOIN mcjz_worker_info b on a.worker_info_id_id=b.worker_id and status=1
        # where pname='蛇口项目一' and work_day=0 and overtime=0 and salary=0 and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data
        # """
        # 正常上班工日sql
        # sql = """
        # SELECT write_data daynum,count(worker_info_id_id)
        # FROM mcjz_worker_hours a LEFT JOIN mcjz_worker_info b on a.worker_info_id_id=b.worker_id and status=1
        # where pname='蛇口项目一' and work_day!=0 and overtime!=0 and salary=0 and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data
        # """
        # 两个结合起来sql
        sql = """
        (select tmp2.daynum,
        ifnull(gzrs,0)+ifnull(qjrs,0),
        ifnull(gzrs,0),
        ifnull(qjrs,0)
        from
        (SELECT write_data daynum,pname,count(worker_info_id_id) qjrs
        FROM mcjz_worker_hours a LEFT JOIN mcjz_worker_info b on a.worker_info_id_id=b.worker_id and status=1 
        where pname='""" + pro.project_name + """' and work_day=0 and overtime=0 and salary=0 and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data) tmp1
        right join
        (SELECT write_data daynum,pname,count(worker_info_id_id) gzrs
        FROM mcjz_worker_hours a LEFT JOIN mcjz_worker_info b on a.worker_info_id_id=b.worker_id and status=1  
        where pname='""" + pro.project_name + """' and work_day!=0 and overtime!=0 and salary=0 and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data) tmp2
        on tmp1.daynum = tmp2.daynum)
        union
        (select tmp2.daynum,
        ifnull(gzrs,0)+ifnull(qjrs,0),
        ifnull(gzrs,0),
        ifnull(qjrs,0)
        from
        (SELECT write_data daynum,pname,count(worker_info_id_id) qjrs
        FROM mcjz_worker_hours a LEFT JOIN mcjz_worker_info b on a.worker_info_id_id=b.worker_id and status=1 
        where pname='""" + pro.project_name + """' and work_day=0 and overtime=0 and salary=0 and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data) tmp1
        left join
        (SELECT write_data daynum,pname,count(worker_info_id_id) gzrs
        FROM mcjz_worker_hours a LEFT JOIN mcjz_worker_info b on a.worker_info_id_id=b.worker_id and status=1  
        where pname='""" + pro.project_name + """' and work_day!=0 and overtime!=0 and salary=0 and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data) tmp2
        on tmp1.daynum = tmp2.daynum)
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        result4 = [list(i) for i in result]
        result4 = domonth(result4)  # 同样加到domonth中过滤
        print(result4)
        # ***************查询工日统计  按项目查询 录入日期分组 统计查询总工日 非加班工日和加班工日
        sql = """
            SELECT write_data daynum,sum(work_day)+sum(overtime),sum(work_day),sum(overtime)
            FROM mcjz_worker_hours where pname='""" + pro.project_name + """' and DATE_FORMAT(write_data, '%Y%m')=DATE_FORMAT( CURDATE(),'%Y%m') GROUP BY write_data
            """
        cursor.execute(sql)
        result = cursor.fetchall()
        result3 = [list(i) for i in result]

        result3 = domonth(result3)

        data = {
            "code": 1,
            "msg": "查询成功",
            "data": {
                "pro_name": result1[0].pop(),
                "name1": ['项目总人数', '项目总工日', '项目非加班工日', '项目加班工日', '项目总工资', '项目总非加班工资', '项目总加班工资', '项目总已发工资'],
                "data0": result1[0],
                "name2": ["工资统计图", "工日统计图", "工人统计图"],
                "dataname": [['总工资', '非加班工资', '加班工资'], ['总工日', '非加班工日', '加班工日'], ['总人数', '工作人数', '请假人数']],
                "data": [result2,  # 工资统计
                         result3,  # 工日统计
                         result4,  # 工人统计
                         ],
            },
        }
        return JsonResponse(data=data, json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        return render_to_response('analysis/statisticSingle.html')


def statisticTypeWork(request):
    if request.method == "GET":
        wt = list(Project.objects.all().values())
        # 查询单个任务的工种记录 select type_name,count(work_type_id) from mcjz_worker_type a left join mcjz_worker_info b on b.work_type_id=a.worker_type_id and b.project_name_id=1 group by type_name
        # sql = "select type_name,count(work_type_id) from mcjz_worker_type a left join mcjz_worker_info b on b.work_type_id=a.worker_type_id and b.project_name_id=1 group by type_name"
        # 查询所有任务工种记录总和  select type_name,count(work_type_id) from mcjz_worker_type a left join mcjz_worker_info b on b.work_type_id=a.worker_type_id group by type_name
        # 按工种查询  select project_name,count(work_type_id) from mcjz_project a left join mcjz_worker_info b on a.project_id=b.project_name_id and work_type_id=1 group by project_id
        cursor = connection.cursor()
        data = []
        project_name = []
        for w in wt:
            project_name.append(w['project_name'])
            sql = "select type_name,count(work_type_id) from mcjz_worker_type a left join mcjz_worker_info b on b.work_type_id=a.worker_type_id and b.status=1 and b.project_name_id=" + str(
                w['project_id']) + " group by type_name"
            cursor.execute(sql)
            result = cursor.fetchall()
            result = [list(i) for i in result]
            data.append([[i[0] for i in result], [i[1] for i in result]])

        # 总人数追加
        sql = "select type_name,count(work_type_id) from mcjz_worker_type a left join mcjz_worker_info b on b.work_type_id=a.worker_type_id and b.status=1 group by type_name"
        cursor.execute(sql)
        result = cursor.fetchall()
        result = [list(i) for i in result]
        data.append([[i[0] for i in result], [i[1] for i in result]])
        project_name.append('所有项目总工种数')
        project_name.append("所有项目工种综合统计")
        # print(result)
        cursor.close()
        return JsonResponse(data={"code": 1, "msg": "查询成功",
                                  "data": {"project_name": project_name, "data": data}},
                            json_dumps_params={'ensure_ascii': False})
    elif request.method == "POST":
        return render_to_response('analysis/statisticTypeWork.html')


def financial_projectinfo(request):
    return render_to_response('financial/project_info.html')


def financial_salarypay(request):
    return render_to_response('financial/salary_pay.html')


def financial_approve(request):
    return render_to_response('financial/hours_approval.html')


def financial_modifyrecode(request):
    return render_to_response('financial/modify_recode.html')


def financial_analysis(request):
    return render_to_response('financial/analysis.html')
