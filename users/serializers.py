from rest_framework import serializers
from .models import AuthUser, Trip, TripSchedule

class AuthUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AuthUser
        fields = ('id', 'username', 'password')

class TripSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Trip
        fields = '__all__'

class TripScheduleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TripSchedule
        fields = '__all__'