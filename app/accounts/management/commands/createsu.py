from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    """Command for creating superuser with password for AWS elastic beanstalk."""

    def handle(self, *args, **options):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser('admin', 'admin', 'admin@admin.com', 'admin', 'admin1212')