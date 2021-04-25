from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
# Create your models here.
class News(models.Model):
    writer = models.ForeignKey('user.Users', on_delete=models.CASCADE, verbose_name="作者")
    title = models.CharField(max_length=30, verbose_name="标题")
    content = RichTextUploadingField(verbose_name='内容', blank=True)
    release_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    star_num = models.IntegerField(default=0,verbose_name='收藏数')
    click_num = models.IntegerField(default=0,verbose_name='点击量')
    banner = models.ImageField(default='avatar/default.png',upload_to='news/banner',verbose_name='轮播图')
    class Meta:
        verbose_name = '新闻信息'
        verbose_name_plural = verbose_name
        ordering=['-release_time']
    def banner_get(self):
        if self.banner:
            return 'media/' + str(self.banner)
        else:
            return '暂无'

