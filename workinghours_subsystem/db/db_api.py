from django.http import JsonResponse, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.urls import reverse

from db.models import Staff
from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY


def login(request, **kwargs):
    if request.method == 'GET':
        return render_to_response('login.html', context=kwargs)
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        print(username, password)
        user = Staff.objects.filter(telephone=username).first()
        print(user.department.department_id)
        print(user.password, user.telephone)
        if user and user.password == password:
            if user.department.department_id == 1:
                request.session[user.staff_id] = user.telephone
                resp = redirect(reverse('boss_index'))
                resp.set_cookie('uuid', UseAes(SECRET_KEY).encrypt(user.telephone), expires=60 * 60 * 24 * 14)
                return resp
            elif user.department.department_id == 3:
                request.session[user.staff_id] = user.telephone
                resp = redirect(reverse('financial_index'))
                resp.set_cookie('uuid', UseAes(SECRET_KEY).encrypt(user.telephone), expires=60 * 60 * 24 * 14)
                return resp
            elif user.department.department_id == 7:
                request.session[user.staff_id] = user.telephone
                resp = redirect(reverse('pro_leader_index'))
                resp.set_cookie('uuid', UseAes(SECRET_KEY).encrypt(user.telephone), expires=60 * 60 * 24 * 14)
                return resp
            else:
                return HttpResponse('权限不足，请返回')
        else:
            return render_to_response('login.html', context={'msg': '用户名或密码错误'})


def logout(request):
    if request.method == 'GET':
        request.session.flush()
        res = redirect(reverse('login'))
        res.delete_cookie('uuid')
        return res


def profile(request):
    if request.method == 'GET':
        phone = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
        print(phone)
        user = Staff.objects.get(telephone=phone)
        data = {
            'icon': user.icon,
            'username': user.username,
            'id_card': user.id_card,
            'telephone': phone,
            'password': user.password,
            'department': user.department.name,
        }
        return render_to_response('profile.html', context=data)
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        phone = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
        user = Staff.objects.get(telephone=phone)
        if old_password and password and new_password:
            if user.password == old_password:
                if len(password) < 4:
                    return JsonResponse(data={"msg": "新密码不能小于4位。"}, json_dumps_params={'ensure_ascii': False})
                else:
                    if new_password == password:
                        obj = Staff.objects.get(telephone=user.telephone)
                        obj.password = password
                        obj.save()
                        return JsonResponse(data={'msg': '修改成功。','department_id':user.department_id}, json_dumps_params={'ensure_ascii': False})
                    else:
                        return JsonResponse(data={'msg': '设置的两次新密码不一致。'}, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse(data={"msg": "密码错误。"}, json_dumps_params={'ensure_ascii': False})
        else:
            return JsonResponse(data={'msg': '内容不能为空。'}, json_dumps_params={'ensure_ascii': False})
