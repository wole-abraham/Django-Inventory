from django.urls import path
from . import views

urlpatterns = [
    path('filter-equipment/', views.filter_equipment, name='filter_equipment'),
    path('request-equipment/', views.request_equipment, name='request_equipment'),
    path('return-equipment/', views.return_equipment, name='return_equipment'),
    path('profile/', views.profile, name='profile'),
    path('equipment/', views.equipment, name='equipment'),
    path('equipment/<int:id>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/<int:id>/edit/', views.edit_equipment, name='edit_equipment'),
    path('accessory/<int:id>/', views.accessory, name='accessory'),
    path('accessory/<int:id>/edit/', views.edit_accessory, name='edit_accessory'),
    path('store/returning/', views.store_returning, name='store_returning'),
    path('equipment/<int:id>/return/', views.return_equipment, name='return_equipment'),
    path('return-accessory/<int:id>/', views.return_accessory, name='return_accessory')
]