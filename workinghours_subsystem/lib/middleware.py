from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from db.models import Staff
from db.tools import UseAes
from workinghours_subsystem.settings import SECRET_KEY


class MiddlewareCheckUser(MiddlewareMixin):
    def process_request(self, request):
        pass