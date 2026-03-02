from django.core.management.base import BaseCommand

from sheets.models import Spreadsheet
from sheets.services import GoogleSheetsService


class Command(BaseCommand):
    help = "Sync data from Google Sheets into the local database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--spreadsheet-id",
            type=str,
            dest="spreadsheet_id",
            help="Sync only the spreadsheet with this Google Sheets ID",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            dest="all",
            help="Sync all active spreadsheets (default behaviour if no flag given)",
        )

    def handle(self, *args, **options):
        service = GoogleSheetsService()

        if options["spreadsheet_id"]:
            try:
                queryset = [
                    Spreadsheet.objects.get(spreadsheet_id=options["spreadsheet_id"])
                ]
            except Spreadsheet.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        f"Spreadsheet not found: {options['spreadsheet_id']}"
                    )
                )
                return
        else:
            queryset = list(Spreadsheet.objects.filter(is_active=True))

        if not queryset:
            self.stdout.write("No active spreadsheets to sync.")
            return

        for spreadsheet in queryset:
            self.stdout.write(f"Syncing '{spreadsheet.title}'…")
            result = service.sync_spreadsheet(spreadsheet)

            if result["errors"]:
                self.stderr.write(
                    self.style.ERROR(f"  Error: {result['errors'][0]}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Done: {result['rows_synced']} rows "
                        f"({result['rows_created']} new, "
                        f"{result['rows_updated']} updated)"
                    )
                )
