from django.shortcuts import render
from rest_framework import generics
from inventory.models  import EquipmentsInSurvey
from .serializers import EquipmentsInSurveySerializer


class EquipmentsListCreate(generics.ListCreateAPIView):
    queryset = EquipmentsInSurvey.objects.all()
    serializer_class = EquipmentsInSurveySerializer



