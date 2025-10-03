from rest_framework import serializers
from .models import EquipmentsInSurvey, Accessory, Personnel, Chainman, EquipmentHistory, AccessoryHistory
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser']


class EquipmentsInSurveySerializer(serializers.ModelSerializer):
    chief_surveyor_detail = UserSerializer(source='chief_surveyor', read_only=True)
    
    class Meta:
        model = EquipmentsInSurvey
        fields = [
            'id', 'name', 'date_of_receiving_from_supplier', 'supplier', 'owner',
            'serial_number', 'condition', 'chief_surveyor', 'chief_surveyor_detail',
            'surveyor_responsible', 'quantity', 'project', 'section',
            'date_receiving_from_department', 'status', 'delivery_status',
            'return_comment', 'return_date'
        ]
        read_only_fields = ['id']


class AccessorySerializer(serializers.ModelSerializer):
    equipment_detail = EquipmentsInSurveySerializer(source='equipment', read_only=True)
    chief_surveyor_detail = UserSerializer(source='chief_surveyor', read_only=True)
    returned_by_detail = UserSerializer(source='returned_by', read_only=True)
    
    class Meta:
        model = Accessory
        fields = [
            'id', 'name', 'manufacturer', 'serial_number', 'equipment', 'equipment_detail',
            'chief_surveyor', 'chief_surveyor_detail', 'surveyor_responsible',
            'condition', 'status', 'return_status', 'comment', 'date_returned',
            'returned_by', 'returned_by_detail', 'delivery_status'
        ]
        read_only_fields = ['id']


class PersonnelSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Personnel
        fields = [
            'id', 'user', 'user_detail', 'employee_id', 'position',
            'department', 'phone_number', 'date_joined', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined']


class ChainmanSerializer(serializers.ModelSerializer):
    assigned_to_detail = PersonnelSerializer(source='assigned_to', read_only=True)
    
    class Meta:
        model = Chainman
        fields = [
            'id', 'name', 'employee_id', 'phone_number', 'assigned_to',
            'assigned_to_detail', 'date_assigned', 'is_active'
        ]
        read_only_fields = ['id', 'date_assigned']


class EquipmentHistorySerializer(serializers.ModelSerializer):
    equipment_detail = EquipmentsInSurveySerializer(source='equipment', read_only=True)
    previous_chief_surveyor_detail = UserSerializer(source='previous_chief_surveyor', read_only=True)
    new_chief_surveyor_detail = UserSerializer(source='new_chief_surveyor', read_only=True)
    changed_by_detail = UserSerializer(source='changed_by', read_only=True)
    
    class Meta:
        model = EquipmentHistory
        fields = [
            'id', 'equipment', 'equipment_detail', 'action', 'previous_status',
            'new_status', 'previous_chief_surveyor', 'previous_chief_surveyor_detail',
            'new_chief_surveyor', 'new_chief_surveyor_detail', 'comment',
            'changed_by', 'changed_by_detail', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_at']


class AccessoryHistorySerializer(serializers.ModelSerializer):
    accessory_detail = AccessorySerializer(source='accessory', read_only=True)
    previous_chief_surveyor_detail = UserSerializer(source='previous_chief_surveyor', read_only=True)
    new_chief_surveyor_detail = UserSerializer(source='new_chief_surveyor', read_only=True)
    changed_by_detail = UserSerializer(source='changed_by', read_only=True)
    
    class Meta:
        model = AccessoryHistory
        fields = [
            'id', 'accessory', 'accessory_detail', 'action', 'previous_status',
            'new_status', 'previous_return_status', 'new_return_status',
            'previous_chief_surveyor', 'previous_chief_surveyor_detail',
            'new_chief_surveyor', 'new_chief_surveyor_detail', 'comment',
            'changed_by', 'changed_by_detail', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_at']
