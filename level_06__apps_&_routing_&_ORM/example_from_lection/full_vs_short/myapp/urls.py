from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyAppListView.as_view(), name='myapp'),
    path('2/', views.MyAppListView2.as_view(), name='myapp2'),
]