# config_manager/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from .models import Configuration
from .serializers import ConfigurationSerializer
from .kafka_producer import publish_config_update

class ActiveConfigListView(generics.ListAPIView):
    """
    API view to retrieve a list of all ACTIVE configurations.
    This is the primary endpoint for client services to fetch their initial config.
    """
    queryset = Configuration.objects.filter(is_active=True)
    serializer_class = ConfigurationSerializer

class ConfigUpdateView(generics.GenericAPIView):
    """
    API view to create or update a configuration.
    This implements our versioning logic.
    """
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        config_name = serializer.validated_data['name']
        config_value = serializer.validated_data['value']

        # CORE LOGIC:
        # 1. Deactivate any existing active config with the same name.
        Configuration.objects.filter(name=config_name, is_active=True).update(is_active=False)

        # 2. Create the new active configuration.
        new_config = Configuration.objects.create(
            name=config_name,
            value=config_value,
            is_active=True
        )
        publish_config_update(config_name, config_value)

        
        # Return the newly created config object
        return Response(self.get_serializer(new_config).data, status=status.HTTP_201_CREATED)