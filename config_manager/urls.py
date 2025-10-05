from django.urls import path
from .views import ActiveConfigListView, ConfigUpdateView, ConfigRollbackView 

urlpatterns = [
    path('configs/', ActiveConfigListView.as_view(), name='active-config-list'),
    path('configs/update/', ConfigUpdateView.as_view(), name='config-update'),
    path('configs/rollback/', ConfigRollbackView.as_view(), name='config-rollback'), # <-- Add this line
]