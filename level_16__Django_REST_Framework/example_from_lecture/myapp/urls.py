from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookView.as_view(), name='book_list'),

    # path('book/add/', views.book_create, name='book_create'),
    # path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    # path('book/<int:pk>/', views.book_detail, name='book_detail'),
    # path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),

    path('book/add-cbv/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/edit-cbv/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/cbv/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:pk>/delete-cbv/', views.BookDeleteView.as_view(), name='book_delete'),

    path('author-list/', views.AuthorListView.as_view(), name='author_list'),
    path('author-edit/<int:pk>/', views.author_edit, name='author_edit'),

    path("edit_all_books/", views.edit_all_books, name="edit_all_books"),

]
