from django.core.management.base import BaseCommand
from goals.services import freeze_weekly_outcomes


class Command(BaseCommand):
    """
    Django management command to freeze last week's goal outcomes.

    This command calls `freeze_weekly_outcomes()` from the `goals.services`
    module to snapshot each user's goal progress for the previous week.
    It can be safely run manually or on a scheduled basis (e.g., via cron or Celery).

    Usage:
        python manage.py freeze_goal_outcomes
        python manage.py freeze_goal_outcomes --dry-run

    Attributes:
        help (str): A short description shown in `python manage.py help`.
    """

    help = "Freeze last week's goal outcomes."

    def add_arguments(self, parser):
        """
        Add optional command-line arguments.

        Args:
            parser (ArgumentParser): The argument parser instance to modify.

        Options:
            --dry-run: Run without saving changes to the database.
        """
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        """
        Execute the management command logic.

        Calls the `freeze_weekly_outcomes()` service function and prints
        a summary of how many outcomes were created or updated for the week.

        Args:
            *args: Positional command arguments.
            **opts: Keyword options, including 'dry_run'.

        Returns:
            None: Outputs results directly to the console.
        """
        result = freeze_weekly_outcomes(dry_run=opts["dry_run"])
        self.stdout.write(self.style.SUCCESS(
            f"Week {result['week_start']}–{result['week_end']} | "
            f"created: {result['created']} | updated: {result['updated']}"
        ))
