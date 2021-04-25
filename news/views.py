from django.shortcuts import render
from .models import *
from user.models import *
from django.http import JsonResponse
from rest_framework.decorators import api_view
from user.decorator import login_check
# Create your views here.
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ManyToManyField
def to_dict(obj, fields=None, exclude=None):
    data = {}
    for f in obj._meta.concrete_fields + obj._meta.many_to_many:
        value = f.value_from_object(obj)
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if isinstance(f, ManyToManyField):
            value = [i.id for i in value] if obj.pk else None
        if isinstance(f, DateTimeField):
            value = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
        data[f.name] = value
    return data
def news_list(request):
    dic = {}
    try:
        data=list(News.objects.all().values('id','writer_id','title'))
        for i in data:
            i['writer_nickname']=Users.objects.get(id=i['writer_id']).nickname
            i['writer_avatar'] = str(Users.objects.get(id=i['writer_id']).avatar_get())
            i['banner']=str(News.objects.get(id=i['id']).banner_get())
        dic['code']=200
        dic['msg']='获取成功'
        dic['data']=data
        return JsonResponse(dic)
    except:
        dic['code'] = 500
        dic['msg'] = '请求方式错误'
        return JsonResponse(dic)
@api_view(['GET'])
@login_check('GET')
def news_detail(request,id):
    dic={}
    try:
        id = int(id)
    except:
        dic['code'] = 500
        dic['msg'] = '请求参数错误'
        return JsonResponse(dic)
    new_check = News.objects.filter(id=id)
    if not new_check:
        dic['code']=404
        dic['msg']='请求数据不存在'
        return JsonResponse(dic)

    the_new=News.objects.get(id=id)
    data = to_dict(the_new,fields=['id','writer','title','content','release_time','star_num','click_num'])
    the_new.click_num += 1
    the_new.save()
    user = request.tuser
    if user:
        star_check = MyStar.objects.filter(user=user,star_type=1,news_id=id)
        if star_check:
            data['is_star']=1
        else:
            data['is_star'] = 0
    data['writer_nickname']=Users.objects.get(id=data['writer']).nickname
    data['writer_avatar'] = str(Users.objects.get(id=data['writer']).avatar_get())
    dic['data']=data
    dic['code']=200
    dic['msg']='获取成功'
    return JsonResponse(dic)


@api_view(['POST'])
@login_check('POST')
def release_news(request):
    dic={}
    try:
        title = request.POST.get('title')
        content = request.POST.get('content')
        banner = request.FILES.get('banner',None)
        user = request.tuser
        if user.user_type == 1:
            dic['code']=501
            dic['msg']='非认证机构不能发布新闻'
            return JsonResponse(dic)
        News.objects.create(content=content,title=title,banner=banner,writer=user)
        dic['code']=200
        dic['msg']='发布成功'
        return JsonResponse(dic)
    except:
        dic['code']=500
        dic['msg']='请求方式错误'
        return JsonResponse(dic)