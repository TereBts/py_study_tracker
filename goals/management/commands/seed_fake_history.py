from django.core.management.base import BaseCommand
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal, ROUND_HALF_UP
import random

from goals.models import Goal, GoalOutcome


class Command(BaseCommand):
    """
    Django management command to seed fake GoalOutcome history data.

    This command generates historical weekly progress data for active goals,
    simulating realistic study progress for demonstration and chart testing.

    It can optionally remove previously seeded records before re-populating
    and accepts arguments for how many weeks of data to create.

    Usage examples:
        python manage.py seed_fake_history
        python manage.py seed_fake_history --weeks 16
        python manage.py seed_fake_history --clean

    Attributes:
        help (str): Short description shown in the Django 'help' command output.
    """

    help = "Seed fake GoalOutcome history for demo/charts."

    def add_arguments(self, parser):
        """
        Add command-line arguments for customizing seeding behavior.

        Args:
            parser (ArgumentParser): The command argument parser.

        Options:
            --weeks (int): Number of past weeks to seed (default 12).
            --clean (bool): If set, delete previously seeded GoalOutcome rows first.
        """
        parser.add_argument("--weeks", type=int, default=12)
        parser.add_argument(
            "--clean",
            action="store_true",
            help="Delete previously seeded rows first."
        )

    def handle(self, *args, **opts):
        """
        Main command execution entry point.

        Generates synthetic GoalOutcome entries for a configurable number of past weeks.
        Each GoalOutcome includes randomized but plausible 'hours_completed' and
        'lessons_completed' values, as well as completion flags based on goal targets.

        If the '--clean' flag is provided, existing seeded rows (identified by
        notes='seeded') are deleted before new data is generated.

        Args:
            *args: Unused positional arguments.
            **opts: Command options parsed from the CLI (e.g. weeks, clean).

        Returns:
            None: Outputs results directly to the console via stdout.
        """
        weeks = opts["weeks"]
        tz = ZoneInfo("Europe/London")

        # Optionally clear previously seeded rows
        if opts["clean"]:
            deleted, _ = GoalOutcome.objects.filter(notes="seeded").delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} seeded rows."))

        def monday_of(d: date) -> date:
            """Return the Monday of the week for a given date."""
            return d - timedelta(days=d.weekday())

        today = date.today()
        this_monday = monday_of(today)
        goals = Goal.objects.filter(is_active=True).select_related("course")

        for g in goals:
            for i in range(weeks, 0, -1):
                ws = this_monday - timedelta(days=7 * i)
                we = ws + timedelta(days=6)

                # Generate realistic randomised values
                target = Decimal(g.weekly_hours_target or 2.0)
                factor = Decimal(random.uniform(0.6, 1.4))
                hours = (target * factor).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

                if g.weekly_lessons_target:
                    lessons = max(
                        0,
                        int(round(g.weekly_lessons_target * random.uniform(0.6, 1.4))),
                    )
                else:
                    lessons = max(0, int(round(float(hours) / 1.0)))

                # Mark as completed if either target threshold is met or exceeded
                completed = False
                if g.weekly_hours_target and hours >= g.weekly_hours_target:
                    completed = True
                if g.weekly_lessons_target and lessons >= g.weekly_lessons_target:
                    completed = True

                # Create or update the seeded GoalOutcome for this week
                GoalOutcome.objects.update_or_create(
                    goal=g,
                    week_start=ws,
                    defaults={
                        "week_end": we,
                        "hours_completed": hours,
                        "lessons_completed": lessons,
                        "hours_target": g.weekly_hours_target,
                        "lessons_target": g.weekly_lessons_target,
                        "completed": completed,
                        "notes": "seeded",
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded fake history for {goals.count()} goals over {weeks} weeks."
            )
        )
