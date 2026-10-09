from django.urls import path
from . import views

urlpatterns = [
    path('', views.library_index, name='library_index'),
    path('publish/<uuid:worksheet_pk>/', views.library_publish, name='library_publish'),
    path('<int:pk>/like/', views.library_like, name='library_like'),
    path('<int:pk>/save/', views.library_save, name='library_save'),
]
