from django.urls import path
from django.views import generic

from . import views


urlpatterns = [
    path('', views.BookListView.as_view(), name="books"),
    path("<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("add/", views.BookCreateView.as_view(), name="book-add"),
    path("<int:pk>/edit/", views.BookUpdateView.as_view(), name="book-edit"),
    path("<int:pk>/delete/", views.BookDeleteView.as_view(), name="book-delete"),

    path("contact/", views.ContactFormView.as_view(), name="contact"),
    path("contact/success/", generic.TemplateView.as_view(
        template_name="library/contact_success.html"
    ), name="contact-success"),

]
