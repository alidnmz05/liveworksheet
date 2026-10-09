from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.library'
    label = 'library'

    def ready(self):
        from django.db.models.signals import post_save
        from apps.worksheets.models import Worksheet

        def auto_create_library_item(sender, instance, **kwargs):
            if instance.is_public:
                from apps.library.models import LibraryItem
                LibraryItem.objects.get_or_create(worksheet=instance)

        post_save.connect(auto_create_library_item, sender=Worksheet, weak=False,
                          dispatch_uid='auto_library_item')
