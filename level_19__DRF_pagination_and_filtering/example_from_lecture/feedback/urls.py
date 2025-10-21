from django.urls import path
from . import views

urlpatterns = [
    # path('', views.feedback_view, name='feedback'),
    path('', views.FeedbackFormView.as_view(), name='feedback'),
]
