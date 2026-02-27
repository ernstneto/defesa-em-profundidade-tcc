from django.urls import path
from . import views

urlpatterns = [
    path('', views.comment_list, name='comment_list'),
    path('dashboard/', views.comment_list, name='dashboard'),
    path('search/', views.search_comment, name='search_comment'),
]