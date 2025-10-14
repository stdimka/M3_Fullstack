from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductView.as_view(), name='shop'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
