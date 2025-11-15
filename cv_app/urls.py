from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cv/create/', views.cv_create, name='cv_create'),
    path('cv/<int:cv_id>/edit/', views.cv_edit, name='cv_edit'),
    path('cv/<int:cv_id>/preview/', views.cv_preview, name='cv_preview'),
    path('cv/<int:cv_id>/delete/', views.cv_delete, name='cv_delete'),
]
