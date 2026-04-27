from django.urls import path
from . import views

urlpatterns = [
    path('', views.workbook_list, name='workbook_list'),
    path('create/', views.workbook_create, name='workbook_create'),
    path('<uuid:pk>/', views.workbook_detail, name='workbook_detail'),
    path('<uuid:pk>/pages/<int:page_pk>/remove/', views.workbook_remove_page, name='workbook_remove_page'),
]
