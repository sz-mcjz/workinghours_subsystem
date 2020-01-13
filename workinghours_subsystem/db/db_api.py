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
