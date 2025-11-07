"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, main='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), main='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

from django.views import generic

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('library.urls')),

    # path('', views.HomeView.as_view(), name="home"),
    path('', generic.TemplateView.as_view(
        template_name="index.html",
        extra_context={
            "page_title": "О нас",
            "author": "Компания My Company",
        }
    ), name="home"),
    path("github/", generic.RedirectView.as_view(url="https://github.com/", permanent=False)),
]
