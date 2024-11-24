from django.urls import path
from . import views

urlpatterns = [
    path('filter-equipment/', views.filter_equipment, name='filter_equipment'),
    path('request-equipment/', views.request_equipment, name='request_equipment'),
    path('return-equipment/', views.return_equipment, name='return_equipment'),
    path('profile/', views.profile, name='profile'),


]