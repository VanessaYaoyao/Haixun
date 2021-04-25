from django.urls import path
from . import views
urlpatterns = [
    path('news/news_list', views.news_list),
    path('news/<str:id>/detail',views.news_detail),
    path('news/release_news', views.release_news),
]
