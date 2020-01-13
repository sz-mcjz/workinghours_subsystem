from django.shortcuts import render_to_response

from db.models import Staff
from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY


def financial_index(request):
    uuid = UseAes(SECRET_KEY).decodebytes(request.COOKIES.get('uuid'))
    user = Staff.objects.filter(telephone=uuid).first()
    data = {
        'username': user.username,
        'icon': user.icon,
        'department': user.department.name,
    }
    return render_to_response('financial/index.html', context=data)
