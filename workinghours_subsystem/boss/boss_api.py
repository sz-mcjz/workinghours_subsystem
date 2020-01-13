from django.shortcuts import render_to_response

from db.models import Staff, Department
from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY


def boss_index(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    print("------------------10",user.telephone)
    data = {
        'username': user.username,
        'icon': user.icon,
        'department': user.department.name,
        'telephone': user.telephone,
    }
    return render_to_response('boss/index.html', context=data)
