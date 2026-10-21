from django.core.management.base import BaseCommand
from agency.views import ensure_templates_for_all_statuses


class Command(BaseCommand):
    help = "Seeds default email templates for all application statuses if they do not exist."

    def handle(self, *args, **options):
        self.stdout.write("Ensuring default email templates exist...")
        try:
            ensure_templates_for_all_statuses()
            self.stdout.write(self.style.SUCCESS("Successfully ensured email templates for all application statuses."))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Error ensuring email templates: {exc}"))
