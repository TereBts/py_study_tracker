from django.core.management.base import BaseCommand
from datetime import date, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal, ROUND_HALF_UP
import random

from goals.models import Goal, GoalOutcome

class Command(BaseCommand):
    help = "Seed fake GoalOutcome history for demo/charts."

    def add_arguments(self, parser):
        """
        Method to add command-line arguments to the management command.
        """
        parser.add_argument("--weeks", type=int, default=12)
        parser.add_argument("--clean", action="store_true", help="Delete previously seeded rows first.")

    def handle(self, *args, **opts):
        weeks = opts["weeks"]
        tz = ZoneInfo("Europe/London")

        if opts["clean"]:
            deleted, _ = GoalOutcome.objects.filter(notes="seeded").delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} seeded rows."))

        def monday_of(d: date) -> date:
            return d - timedelta(days=d.weekday())

        today = date.today()
        this_monday = monday_of(today)
        goals = Goal.objects.filter(is_active=True).select_related("course")

        for g in goals:
            for i in range(weeks, 0, -1):
                ws = this_monday - timedelta(days=7*i)
                we = ws + timedelta(days=6)

                target = Decimal(g.weekly_hours_target or 2.0)
                factor = Decimal(random.uniform(0.6, 1.4))
                hours = (target * factor).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

                if g.weekly_lessons_target:
                    lessons = max(0, int(round(g.weekly_lessons_target * random.uniform(0.6, 1.4))))
                else:
                    lessons = max(0, int(round(float(hours) / 1.0)))

                completed = False
                if g.weekly_hours_target and hours >= g.weekly_hours_target:
                    completed = True
                if g.weekly_lessons_target and lessons >= g.weekly_lessons_target:
                    completed = True

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
                    }
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded fake history for {goals.count()} goals over {weeks} weeks."))
