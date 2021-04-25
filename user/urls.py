from django.urls import path
from . import views
urlpatterns = [
    path('reglog/login', views.login),
    path('reglog/send_email', views.send_email),
    path('reglog/register', views.register),
    path('reglog/change_pwd', views.change_pwd),

    path('self/info', views.self_info),
    path('self/change_info',views.change_info),
    path('self/change_avatar',views.change_avatar),

]
