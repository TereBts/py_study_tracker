from django.core.management.base import BaseCommand
from goals.services import freeze_weekly_outcomes

class Command(BaseCommand):
    help = "Freeze last week's goal outcomes."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        result = freeze_weekly_outcomes(dry_run=opts["dry_run"])
        self.stdout.write(self.style.SUCCESS(
            f"Week {result['week_start']}–{result['week_end']} | created: {result['created']} | updated: {result['updated']}"
        ))
