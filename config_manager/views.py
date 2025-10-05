# config_manager/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from .models import Configuration
from .serializers import ConfigurationSerializer
from .kafka_producer import publish_config_update
from django.db import transaction
from rest_framework.views import APIView

class ConfigRollbackView(APIView):
    """
    API view to roll back a configuration to a specific historical version.
    """
    def post(self, request, *args, **kwargs):
        config_name = request.data.get('name')
        version_id = request.data.get('version_id')

        if not config_name or not version_id:
            return Response(
                {"error": "Both 'name' and 'version_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                target_version = Configuration.objects.get(id=version_id, name=config_name)

                current_active = Configuration.objects.filter(name=config_name, is_active=True).first()
                if current_active:
                    current_active.is_active = False
                    current_active.save()

                target_version.is_active = True
                target_version.save()
                
                publish_config_update(target_version.name, target_version.value)

            serializer = ConfigurationSerializer(target_version)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Configuration.DoesNotExist:
            return Response(
                {"error": f"Version with id={version_id} for name='{config_name}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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

        config_name = request.data.get('name')
        config_value = request.data.get('value')


        Configuration.objects.filter(name=config_name, is_active=True).update(is_active=False)

        new_config = Configuration.objects.create(
            name=config_name,
            value=config_value,
            is_active=True
        )
        publish_config_update(config_name, config_value)

        
        return Response(self.get_serializer(new_config).data, status=status.HTTP_201_CREATED)