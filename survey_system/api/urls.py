from django.urls import path
from .views import EquipmentsListCreate

urlpatterns = [
    path('equipments', EquipmentsListCreate.as_view(), name='equipment-status')
    
]