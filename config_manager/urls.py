from django.urls import path
from .views import ActiveConfigListView, ConfigUpdateView

urlpatterns = [
    path('configs/', ActiveConfigListView.as_view(), name='active-config-list'),
    path('configs/update/', ConfigUpdateView.as_view(), name='config-update'),
]