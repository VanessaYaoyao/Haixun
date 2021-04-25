from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.contrib.auth.hashers import make_password,check_password
from django.core.mail import send_mail
from Haixun.settings import EMAIL_FROM
from rest_framework.decorators import api_view
from .decorator import login_check
from PIL import Image
from rest_framework.authtoken.models import Token
from django.contrib import auth
# Create your views here.
import simplejson,random,re,jwt,datetime,os
SECRET_KEY = "ruabbit"  # 区别于settings里面的密钥
# pytz.timezone('PRC')
dic_payload = {
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # 过期时间
    'iat': datetime.datetime.utcnow(),  # 开始时间
    'iss': 'rua',  # 签名
    'data': {  # 内容
        "userid": 0,
    },
}

def register(request):
    dic = {}
    if request.method == 'POST':
        try:
            req = simplejson.loads(request.body)
            email = req['email']
            account = req['account']
            password = req['password']
            email_code = req['email_code']
        except:
            dic['code'] = 996
            dic['msg'] = "参数不符合规则(无法获取)"
            return JsonResponse(dic)
        tmp_email = EmailCode.objects.filter(email=email,send_type=1)
        if tmp_email:
            correct_code = tmp_email.first().email_code
        else:
            correct_code = None
        tmp_user = Users.objects.filter(account=account)
        tmp_user_for_email = Users.objects.filter(email=email)
        tmp_email_correct = EmailCode.objects.filter(email_code=correct_code,send_type=1)
        if tmp_user:
            dic['code'] = 1104
            dic['msg'] = "账号已被占用"
            return JsonResponse(dic,safe=False)
        elif tmp_user_for_email:
            dic['code'] = 1109
            dic['msg'] = "邮箱已被注册"
            return JsonResponse(dic,safe=False)
        elif not re.match('^[1-2][0-9]{10}$', account):
            dic['code'] = 1105
            dic['msg'] = "账号不符合规范"
            return JsonResponse(dic,safe=False)
        elif not re.match('^\w{6,20}$', password):
            dic['code'] = 1106
            dic['msg'] = "密码长度为6-20位，不得含有特殊字符"
            return JsonResponse(dic,safe=False)
        elif not re.match('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email):
            dic['code'] = 1107
            dic['msg'] = "邮箱不符合规范"
            return JsonResponse(dic,safe=False)
        elif not tmp_email_correct:
            dic['code'] = 1108
            dic['msg'] = "未发送验证码"
            return JsonResponse(dic,safe=False)
        elif not tmp_email_correct.first().email == email:
            dic['code'] = 1102
            dic['msg'] = "邮箱不匹配"
            return JsonResponse(dic,safe=False)
        elif not email_code == correct_code:
            dic['code'] = 1103
            dic['msg'] = "验证码错误"
            return JsonResponse(dic,safe=False)
        else:
            tmp_user_2 = Users.objects.create(account=account, password=make_password(password), email=email)
            tmp_email_2 = EmailCode.objects.filter(email=email)
            tmp_email_2.delete()
            # userid = tmp_user_2.id
            # dic_payload['data']['userid'] = userid
            # token = jwt.encode(dic_payload, SECRET_KEY, algorithm='HS256')
            dic['code'] = 1000
            dic['msg'] = '一切正常'
            # dic['data']['token'] = token
            return JsonResponse(dic,safe=False)
    else:
        dic['code'] = 999
        dic['msg'] = "错误的请求方式"
        return JsonResponse(dic,safe=False)

def login(request):
    dic = {
        "code": 0000,
        "msg": "缺省值",
        "data": {
            "token": "",
        }
    }
    if request.method == 'POST':
        try:
            req = simplejson.loads(request.body)
            account = req['account']
            password = req['password']
        except:
            dic['code'] = 996
            dic['msg'] = "参数不符合规则(无法获取)"
            return JsonResponse(dic,safe=False)
        check_user = Users.objects.filter(account=account)
        if check_user:
            user = check_user.first()
            user_id = user.id
            user_pwd = user.password
            if check_password(password,user_pwd):
                dic_payload['data']['userid'] = user_id
                token = jwt.encode(payload=dic_payload, key=SECRET_KEY, algorithm='HS256')
                dic['code'] = 1000
                dic['msg'] = '一切正常'
                dic['data']['token'] = str(token)[2:-1]
                return JsonResponse(dic)
            else:
                dic['code'] = 1112
                dic['msg'] = '用户名或密码错误'
                return JsonResponse(dic,safe=False)
        else:
            dic['code'] = 1112
            dic['msg'] = '用户名或密码错误'
            return JsonResponse(dic,safe=False)
    else:
        dic['code'] = 999
        dic['msg'] = "错误的请求方式"
        return JsonResponse(dic,safe=False)

def getRandomData():
    result = str(random.randint(100000, 999999))
    return result

def send_email_code(email, send_type):
    code = getRandomData()
    email_record = EmailCode()
    # 将给用户发的信息保存在数据库中
    email_record.email_code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    send_title = ''
    send_body = ''
    # 如果为注册类型
    if send_type == 1:
        send_title = "海讯验证码"
        send_body = "【海讯】您的注册验证码为：{0}，感谢您的使用。".format(code)
        send_mail(send_title, send_body, EMAIL_FROM, [email])
    if send_type == 2:
        send_title = "海讯验证码"
        send_body = "【海讯】您的重置密码验证码为：{0}，感谢您的使用。".format(code)
        send_mail(send_title, send_body, EMAIL_FROM, [email])

def send_email(request):
    dic = {}
    try:
        req = simplejson.loads(request.body)
        email = req['email']
        send_type = req['type']
    except:
        dic['code'] = 996
        dic['msg'] = "参数不符合规则(无法获取)"
        return JsonResponse(dic, safe=False)
    if re.match('\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*', email):
        if send_type == 1:
            send_email_code(email,1)
            dic['code'] = 200
            dic['msg'] = "一切正常"
            return JsonResponse(dic)
        elif send_type == 2:
            send_email_code(email,2)
            dic['code'] = 200
            dic['msg'] = "一切正常"
            return JsonResponse(dic)
        else:
            dic['code'] = 996
            dic['msg'] = "参数不符合规则(无法获取)"
            return JsonResponse(dic, safe=False)
    else:
        dic['code'] = 996
        dic['msg'] = "邮箱格式错误"
        return JsonResponse(dic)

@api_view(['POST'])
def change_pwd(request):
    dic={
        "data":{}
    }
    try:
        req = simplejson.loads(request.body)
        email = req['email']
        new_password = req['new_password']
        email_code = req['email_code']
    except:
        dic['code'] = 996
        dic['msg'] = "参数不符合规则(无法获取)"
        return JsonResponse(dic)
    if not re.match('^\w{6,20}$', new_password):
        dic['code'] = 1106
        dic['msg'] = "密码长度为6-20位，不得含有特殊字符"
        return JsonResponse(dic, safe=False)
    tmp_email = EmailCode.objects.filter(email=email,send_type=2)
    if tmp_email:
        correct_code = tmp_email.first().email_code
    else:
        correct_code = None
    tmp_user = Users.objects.filter(email=email)
    if tmp_user:
        if email_code == correct_code:
            user = tmp_user.first()
            user.password = make_password(new_password)
            user.save()
            userid = user.id
            dic_payload['data']['userid'] = userid
            token = jwt.encode(dic_payload, SECRET_KEY, algorithm='HS256')
            dic['code'] = 200
            dic['msg'] = '一切正常'
            dic['data']['token'] = str(token)[2:-1]
            return JsonResponse(dic)
        else:
            dic["code"] = 1103
            dic['msg'] = "验证码错误"
            return JsonResponse(dic)
    else:
        dic["code"] = 1113
        dic['msg'] = "用户不存在"
        return JsonResponse(dic)

@api_view(['GET'])
@login_check('GET')
def self_info(request):
    dic = {
        "code": 0000,
        "msg": "缺省值",
        "data":{}
    }
    user = request.tuser
    # serializer = UsersSerializer(user, many=True, context={"request": request})
    dic['data']['account'] = user.account
    dic['data']['nickname'] = user.nickname
    dic['data']['description'] = user.description
    dic['data']['gender']= user.sex()
    dic['data']['type']= user.userType()
    dic['data']['age'] = user.age
    dic['data']['email'] = user.email
    dic['data']['avatar'] = user.avatar_get()
    dic['data']['star_num'] = user.star_num
    dic['data']['be_like_num'] = user.be_like_num
    dic['code'] = 200
    dic['msg'] = '一切正常'
    return JsonResponse(dic)

@api_view(['POST'])
@login_check('POST')
def change_info(request):
    dic ={}
    user = request.tuser
    try:
        req = simplejson.loads(request.body)
        nickname = req['nickname']
        description = req['description']
        gender = req['gender']
        age = req['age']
    except:
        dic['code'] = 996
        dic['msg'] = "参数不符合规则(无法获取)"
        return JsonResponse(dic)
    if age<0 or age>120:
        dic['code'] = 500
        dic['msg'] = '年龄不合规范'
        return JsonResponse(dic)
    elif len(description)>20 :
        dic['code']= 501
        dic['msg'] = '长度不得大于20'
        return JsonResponse(dic)
    elif gender not in (0,1,-1):
        dic['code']=502
        dic['msg']='性别参数错误'
        return JsonResponse(dic)
    elif len(nickname)>10:
        dic['code']=503
        dic['msg']='长度不得大于10'
        return JsonResponse(dic)
    else:
        for i in nickname:
            if i == '\n':
                nickname = nickname.replace(i,'')
        for i in description:
            if i == '\n':
                description = description.replace(i,'')
        user.description=description
        user.nickname=nickname
        user.age=age
        user.gender = gender
        user.save()
        dic['code']=200
        dic['msg']='修改成功'
        return JsonResponse(dic)

@api_view(['POST'])
@login_check('POST')
def change_avatar(request):
    user = request.tuser
    dic = {}
    try:
        img=request.FILES.get('avatar')
    except:
        dic['code']=996
        dic['msg']="参数不符合规则(无法获取)"
        return JsonResponse(dic)
    if img:
        try:
            img_p = Image.open(img)
        except:
            dic['code'] = 997
            dic['msg'] = "图片不符合规则"
            return JsonResponse(dic)
        name = os.path.splitext(img.name)[0]
        suffix = os.path.splitext(img.name)[1]
        if not suffix:
            dic['code'] = 997
            dic['msg'] = "图片不符合规则"
            return JsonResponse(dic)
        elif not (suffix.lower() == '.jpeg' or suffix.lower() == ".png" or suffix.lower() == ".jpg"):
            dic['code'] = 997
            dic['msg'] = "图片不符合规则(jpeg/png/jpg)"
            return JsonResponse(dic)
        elif img.size >= 10000000:
            dic['code'] = 997
            dic['msg'] = "图片不符合规则(大于10mb)"
            return JsonResponse(dic)
        elif img_p.format != 'JPEG' and img_p.format != 'PNG':
            dic['code'] = 997
            dic['msg'] = "图片不符合规则(不是图片)"
            return JsonResponse(dic)
        else:
            fullname = str(datetime.datetime.now()) + suffix
            img.name = fullname
            user.avatar = img
            user.save()

            dic['code'] = 1000
            dic['msg'] = '一切正常'
            return JsonResponse(dic)

