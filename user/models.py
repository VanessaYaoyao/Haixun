from django.db import models
from Haixun import settings
root = settings.ROOT
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFill
# Create your models here.
gender_choice = (
    (-1, '保密'),
    (1, "男"),
    (0, "女")
)
type_choice = (
    (1,"普通用户"),
    (2,"认证机构")
)

class Users(models.Model):
    account = models.CharField(max_length=30, verbose_name="账号")
    password = models.CharField(max_length=128, verbose_name="密码")
    email = models.EmailField(verbose_name="邮箱")
    nickname = models.CharField(max_length=30, default='江湖骗子',verbose_name="昵称")
    description = models.CharField(verbose_name="简介", max_length=200, default='这个人很懒，什么都没写')
    age = models.IntegerField(verbose_name='年龄',blank=True,default=0)
    gender = models.IntegerField(choices=gender_choice, verbose_name="性别", default=-1)
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True,default='avatar/default.png',verbose_name='头像')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    user_type = models.IntegerField(choices=type_choice,default=1,verbose_name='用户类型')
    be_like_num = models.IntegerField(verbose_name="获赞数", default=0)
    star_num = models.IntegerField(verbose_name="收藏数", default=0)
    avatar_90x90 = ImageSpecField(
        source="avatar",
        processors=[ResizeToFill(90, 90)],  # 处理后的图像大小
        format='JPEG',  # 处理后的图片格式
        options={'quality': 95}  # 处理后的图片质量
    )

    def sex(self):
        if self.gender == 1:
            return "男"
        elif self.gender == 0:
            return "女"
        else:
            return "保密"
    def userType(self):
        if self.user_type == 1:
            return "普通用户"
        else:
            return "认证机构"

    def __str__(self):
        return self.account

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def avatar_get(self):
        if self.avatar:
            return root + str(self.avatar)
        else:
            return '暂无'

    def avatar_get_90x90(self):
        if self.avatar_90x90:
            return root + self.avatar_90x90
        else:
            return '暂无'


class EmailCode(models.Model):
    email_code = models.CharField(max_length=32)
    email = models.EmailField()
    send_type = models.IntegerField()
    send_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-send_time']


star_type = (
    (1, '新闻'),
    (2, '帖子')
)

class MyStar(models.Model):
    user = models.ForeignKey('Users', on_delete=models.CASCADE, verbose_name='收藏者')
    news_id = models.IntegerField(verbose_name='新闻id',blank=True,default=1)
    post_id = models.IntegerField(verbose_name='帖子id', blank=True,default=1)
    star_type = models.IntegerField(choices=star_type, verbose_name='收藏类型')
    star_time = models.DateTimeField(auto_now_add=True,verbose_name='收藏时间')
    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name