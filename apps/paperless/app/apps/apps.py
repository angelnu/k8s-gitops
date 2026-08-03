from django.apps import AppConfig
from django.db.models.signals import m2m_changed, post_migrate


class CasaConfig(AppConfig):
    name = "casa"
    verbose_name = "Casa provisioning"

    def ready(self):
        from django.contrib.auth.models import User

        from .catchall_workflow import provision_catchall_workflow
        from .groups import provision_groups
        from .superadmins import provision_extra_superadmins
        from .superuser_sync import sync_superuser

        post_migrate.connect(provision_groups, sender=self)
        post_migrate.connect(provision_extra_superadmins, sender=self)
        post_migrate.connect(provision_catchall_workflow, sender=self)
        m2m_changed.connect(sync_superuser, sender=User.groups.through)
