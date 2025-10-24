from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import EquipmentsInSurvey, Accessory, Personnel, Chainman, EquipmentHistory, AccessoryHistory
from .serializers import (
    EquipmentsInSurveySerializer, AccessorySerializer, PersonnelSerializer,
    ChainmanSerializer, EquipmentHistorySerializer, AccessoryHistorySerializer,
    UserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class EquipmentsInSurveyViewSet(viewsets.ModelViewSet):
    queryset = EquipmentsInSurvey.objects.all()
    serializer_class = EquipmentsInSurveySerializer
    
    @action(detail=False, methods=['get'])
    def in_store(self, request):
        """Get all equipment currently in store"""
        equipment = EquipmentsInSurvey.objects.filter(status='In Store')
        serializer = self.get_serializer(equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_field(self, request):
        """Get all equipment currently in field"""
        equipment = EquipmentsInSurvey.objects.filter(status__in=['In Field', 'With Chief Surveyor'])
        serializer = self.get_serializer(equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def returning(self, request):
        """Get all equipment currently returning"""
        equipment = EquipmentsInSurvey.objects.filter(status='Returning')
        serializer = self.get_serializer(equipment, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def accessories(self, request, pk=None):
        """Get all accessories for a specific equipment"""
        equipment = self.get_object()
        accessories = equipment.accessories.all()
        serializer = AccessorySerializer(accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get history for a specific equipment"""
        equipment = self.get_object()
        history = equipment.history.all().order_by('-changed_at')
        serializer = EquipmentHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history_summary(self, request, pk=None):
        """Get history summary with counts for a specific equipment"""
        equipment = self.get_object()
        summary = equipment.get_history_summary()
        
        # Serialize the last action if it exists
        last_action_data = None
        if summary['last_action']:
            last_action_data = EquipmentHistorySerializer(summary['last_action']).data
        
        created_date_data = None
        if summary['created_date']:
            created_date_data = EquipmentHistorySerializer(summary['created_date']).data
        
        return Response({
            'equipment_id': equipment.id,
            'equipment_name': equipment.name,
            'serial_number': equipment.serial_number,
            'total_history_entries': summary['total_entries'],
            'returns_to_store': summary['returns_to_store'],
            'total_releases': summary['releases'],
            'last_action': last_action_data,
            'created': created_date_data,
        })


class AccessoryViewSet(viewsets.ModelViewSet):
    queryset = Accessory.objects.all()
    serializer_class = AccessorySerializer
    
    @action(detail=False, methods=['get'])
    def in_store(self, request):
        """Get all accessories currently in store"""
        accessories = Accessory.objects.filter(return_status__in=['In Store', 'Returned'])
        serializer = self.get_serializer(accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_use(self, request):
        """Get all accessories currently in use"""
        accessories = Accessory.objects.filter(return_status__in=['In Use', 'With Chief Surveyor'])
        serializer = self.get_serializer(accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def returning(self, request):
        """Get all accessories currently returning"""
        accessories = Accessory.objects.filter(return_status='Returning')
        serializer = self.get_serializer(accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def standalone(self, request):
        """Get all standalone accessories (not linked to equipment)"""
        accessories = Accessory.objects.filter(equipment__isnull=True)
        serializer = self.get_serializer(accessories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get history for a specific accessory"""
        accessory = self.get_object()
        history = accessory.history.all().order_by('-changed_at')
        serializer = AccessoryHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def history_summary(self, request, pk=None):
        """Get history summary with counts for a specific accessory"""
        accessory = self.get_object()
        summary = accessory.get_history_summary()
        
        # Serialize the last action if it exists
        last_action_data = None
        if summary['last_action']:
            last_action_data = AccessoryHistorySerializer(summary['last_action']).data
        
        created_date_data = None
        if summary['created_date']:
            created_date_data = AccessoryHistorySerializer(summary['created_date']).data
        
        return Response({
            'accessory_id': accessory.id,
            'accessory_name': accessory.name,
            'serial_number': accessory.serial_number,
            'equipment': str(accessory.equipment) if accessory.equipment else 'Standalone',
            'total_history_entries': summary['total_entries'],
            'returns_to_store': summary['returns_to_store'],
            'total_releases': summary['releases'],
            'last_action': last_action_data,
            'created': created_date_data,
        })


class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Personnel.objects.all()
    serializer_class = PersonnelSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active personnel"""
        personnel = Personnel.objects.filter(is_active=True)
        serializer = self.get_serializer(personnel, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def chainmen(self, request, pk=None):
        """Get all chainmen assigned to a specific personnel"""
        personnel = self.get_object()
        chainmen = personnel.chainmen.all()
        serializer = ChainmanSerializer(chainmen, many=True)
        return Response(serializer.data)


class ChainmanViewSet(viewsets.ModelViewSet):
    queryset = Chainman.objects.all()
    serializer_class = ChainmanSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active chainmen"""
        chainmen = Chainman.objects.filter(is_active=True)
        serializer = self.get_serializer(chainmen, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unassigned(self, request):
        """Get all unassigned chainmen"""
        chainmen = Chainman.objects.filter(assigned_to__isnull=True, is_active=True)
        serializer = self.get_serializer(chainmen, many=True)
        return Response(serializer.data)


class EquipmentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EquipmentHistory.objects.all().order_by('-changed_at')
    serializer_class = EquipmentHistorySerializer
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent equipment history (last 50 entries)"""
        history = EquipmentHistory.objects.all().order_by('-changed_at')[:50]
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)


class AccessoryHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccessoryHistory.objects.all().order_by('-changed_at')
    serializer_class = AccessoryHistorySerializer
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent accessory history (last 50 entries)"""
        history = AccessoryHistory.objects.all().order_by('-changed_at')[:50]
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
