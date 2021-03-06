from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render_to_response

from db.models import Staff, Department, Project
from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY,LEADER


def boss_index(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    if (not user) or (user.department_id != 1):
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    data = {
        'username': user.username,
        'icon': user.icon,
        'department': user.department.name,
        'telephone': user.telephone,
    }
    return render_to_response('boss/index.html', context=data)


# boss创建任务，首先需要遍历出任务执行的人
def boss_create_project(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    if (not user) or (user.department_id != 1):
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'GET':
        # uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
        pro_leader = [staff for staff in Staff.objects.filter(~Q(staff_id=user.staff_id),department__department_id__in=LEADER).values()]
        all_pro = [pro for pro in Project.objects.all().values()]
        for pro in all_pro:
            pro['pro_leader_name'] = Staff.objects.get(staff_id=pro['project_leader_id']).username
            pro['pro_leader_telephone'] = Staff.objects.get(staff_id=pro['project_leader_id']).telephone
        data = {
            'pro_leader': pro_leader,
            'all_pro': all_pro,
        }
        return JsonResponse({'code': 1, 'msg': '请求成功', 'data': data}, json_dumps_params={'ensure_ascii': False})
    elif request.method == 'POST':
        try:
            pro_name = request.POST.get('pro_name')
            pro_leader = request.POST.get('pro_leader')
            overtime = request.POST.get('overtime')
            remarks = request.POST.get('remarks')
            new_pro = Project()
            new_pro.project_name = pro_name
            new_pro.project_leader = Staff.objects.get(staff_id=pro_leader)
            new_pro.overtime = overtime
            new_pro.note = remarks
            new_pro.save()
        except:
            return JsonResponse({'code': 0, 'msg': '创建任务失败'}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse({'code': 1, 'msg': '创建任务成功'})


# boss 删除任务
def boss_delete_pro(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    if (not user) or (user.department_id != 1):
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'POST':
        try:
            pro_id = request.POST.get('pro_id')
            _pro = Project.objects.filter(project_id=pro_id).first()
            _pro.delete()
        except:
            return JsonResponse({'code': 0, 'msg': '删除任务失败'}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse({'code': 1, 'msg': '项目删除成功'})


# boss 修改项目
def boss_modify_pro(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    if (not user) or (user.department_id != 1):
        return JsonResponse(data={"code": 0, "msg": "违规操作"}, json_dumps_params={'ensure_ascii': False})

    if request.method == 'POST':
        try:
            pro_id = request.POST.get('pro_id')
            pro_name = request.POST.get('pro_name')
            pro_leader = request.POST.get('pro_leader')
            print(pro_id, pro_name, pro_leader)
            mod_pro = Project.objects.get(project_id=pro_id)
            mod_pro.project_name = pro_name
            mod_pro.project_leader = Staff.objects.get(staff_id=pro_leader)
            mod_pro.save()
        except:
            return JsonResponse({'code': 0, 'msg': '修改失败'}, json_dumps_params={'ensure_ascii': False})
        return JsonResponse({'code': 1, 'msg': '修改成功'}, json_dumps_params={'ensure_ascii': False})


def createItem(request):
    if request.method == "POST":
        return render_to_response("boss/createItem.html")


def personAdmin(request):
    return render_to_response("boss/personAdmin.html")


def salaryAdmin(request):
    return render_to_response("boss/salaryAdmin.html")
