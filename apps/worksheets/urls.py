from django.urls import path
from . import views

urlpatterns = [
    path('', views.worksheet_list, name='worksheet_list'),
    path('create/', views.worksheet_create, name='worksheet_create'),
    path('<uuid:pk>/editor/', views.worksheet_editor, name='worksheet_editor'),
    path('<uuid:pk>/', views.worksheet_detail, name='worksheet_detail'),
    path('<uuid:pk>/play/', views.worksheet_play, name='worksheet_play'),
    path('<uuid:pk>/delete/', views.worksheet_delete, name='worksheet_delete'),
    # Page API
    path('<uuid:worksheet_pk>/pages/add/', views.api_page_add, name='api_page_add'),
    path('pages/<int:page_pk>/upload/', views.api_page_upload_bg, name='api_page_upload_bg'),
    # Question API
    path('pages/<int:page_pk>/questions/save/', views.api_question_save, name='api_question_save'),
    path('questions/<int:question_pk>/delete/', views.api_question_delete, name='api_question_delete'),
    # Media API
    path('pages/<int:page_pk>/embed/', views.api_media_embed_save, name='api_media_embed_save'),
]
