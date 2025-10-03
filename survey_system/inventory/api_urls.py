from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    UserViewSet, EquipmentsInSurveyViewSet, AccessoryViewSet,
    PersonnelViewSet, ChainmanViewSet, EquipmentHistoryViewSet,
    AccessoryHistoryViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'equipment', EquipmentsInSurveyViewSet)
router.register(r'accessories', AccessoryViewSet)
router.register(r'personnel', PersonnelViewSet)
router.register(r'chainmen', ChainmanViewSet)
router.register(r'equipment-history', EquipmentHistoryViewSet)
router.register(r'accessory-history', AccessoryHistoryViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
