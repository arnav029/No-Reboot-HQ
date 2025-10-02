# config_manager/serializers.py

from rest_framework import serializers
from .models import Configuration

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ['id', 'name', 'value', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']