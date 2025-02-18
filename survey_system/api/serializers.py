from rest_framework import serializers
from inventory.models import EquipmentsInSurvey

class EquipmentsInSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentsInSurvey
        fields = '__all__'

