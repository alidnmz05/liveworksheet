from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_submissions, name='my_submissions'),
    path('<int:pk>/', views.submission_detail, name='submission_detail'),
    path('worksheet/<uuid:worksheet_pk>/submit/', views.submit_worksheet, name='submit_worksheet'),
]
