# login_check('PUT', 'GET', 'POST')
import jwt
from django.http import JsonResponse
from rest_framework.decorators import api_view

from .models import Users

SECRET_KEY = "ruabbit"  # 区别于settings里面的密钥

def login_check(*methods):  # *methods 装饰器参数 ('PUT', 'GET', 'POST')
    def __login_check(func):  # func 被装饰的函数 users
        def wrapper(request, *args, **kwargs):
            # 通过 request 检查token request.***
            # 校验不通过 return JsonResponse()
            token = request.META.get('HTTP_AUTHORIZATION')
            if request.method not in methods:  # 'GET', 'POST'
                return func(request, *args, **kwargs)  # 不需要处理的情况  当前模型、不在需要装饰列表中
            if not token:
                result = {
                    'code': 995,
                    'msg': 'token未携带'
                }
                return JsonResponse(result)

            try:
                res = jwt.decode(token, SECRET_KEY, issuer='rua', algorithms=['HS256'])
            except jwt.ExpiredSignatureError as e:
                # token过期了
                result = {
                    'code': 1114,
                    'msg': 'token过期'
                }
                return JsonResponse(result)
            except Exception as e:
                result = {
                    'code': 994,
                    'msg': 'token无法解密'
                }
                return JsonResponse(result)

            userid = res['data']['userid']

            try:
                user = Users.objects.get(id=userid)
            except Exception as e:
                user = None

            if not user:
                result = {
                    'code': 1113,
                    'msg': '用户不存在'
                }
                return JsonResponse(result)
            # user 查询出来

            # 将查询成功的 user 赋值给 request
            request.tuser = user
            return func(request, *args, **kwargs)

        return wrapper

    return __login_check


def __login_check(func):
    def wrapper():
        return func()

    return wrapper
