from django.urls import path, include
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_index, name='home'),
    path('about/', views.about, name='about'),
    path('article/<int:id>/', views.article, name='article'),
]
