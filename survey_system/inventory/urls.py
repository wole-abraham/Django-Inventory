from django.urls import path
from . import views

urlpatterns = [
    # path('filter-equipment/', views.filter_equipment, name='filter_equipment'),
    path('request-equipment/', views.request_equipment, name='request_equipment'),
    path('return-equipment/', views.return_equipment, name='return_equipment'),
    path('profile/', views.profile, name='profile'),
    path('equipment/', views.equipment, name='equipment'),
    path('equipment/<int:id>/', views.equipment_detail, name='equipment_detail'),
    path('accessory_detail/<int:id>/', views.accessory_detail, name='accessory_detail'),
    path('equipment/<int:id>/edit/', views.edit_equipment, name='edit_equipment'),
    path('accessory/<int:id>/', views.accessory, name='accessory'),
    path('accessory/<int:id>/edit/', views.edit_accessory, name='edit_accessory'),
    path('store/returning/', views.store_returning, name='store_returning'),
    path('equipment/<int:id>/return/', views.return_equipment, name='return_equipment'),
    path('return-accessory/<int:id>/', views.return_accessory, name='return_accessory'),
    path('release-accessory/', views.release_accessory, name='release_accessory'),
    path('admin-release-accessory', views.admin_release_accessory, name="admin_release_accessory"),
    path('add-equipment/', views.add_equipment, name='add_equipment'),
    # path('equipment/<int:id>/history/', views.equipment_history, name='equipment_history'),
    # path('accessory/<int:id>/history/', views.accessory_history, name='accessory_history'),
    # path('history/', views.all_history, name='all_history'),
    path('remove_from_equipment/<int:id>', views.remove_from_equipment, name="remove_from_equipment"),
    path('delivery/', views.delivery, name='delivery'),
    path('cancel-delivery/<int:id>', views.cancel_delivery, name='cancel_delivery'),
    path('receive-delivery/<int:id>', views.delivery_received, name='receive_delivery'),
]