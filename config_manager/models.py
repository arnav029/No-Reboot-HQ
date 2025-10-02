from django.db import models

class Configuration(models.Model):
    """
    Stores a specific version of a configuration setting.
    Only one version for a given name can be active at a time.
    """
    name = models.CharField(max_length=100, db_index=True)
    value = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Active: {self.is_active})"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                condition=models.Q(is_active=True),
                name='unique_active_config_for_name'
            )
        ]