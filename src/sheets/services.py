from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from googleapiclient.discovery import Resource

    from .models import Spreadsheet
    from .types import SyncResult

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Lazy-initialised Google Sheets client.

    The underlying API client is only built on the first call to
    ``_get_service()``, which means this class can be instantiated freely
    in tests without requiring real credentials.
    """

    _service: Resource | None = None

    def _get_service(self) -> Resource:
        if self._service is None:
            from django.conf import settings
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build

            credentials_file = getattr(settings, "GOOGLE_CREDENTIALS_FILE", "")
            if not credentials_file:
                raise ValueError(
                    "GOOGLE_CREDENTIALS_FILE setting is not configured. "
                    "Set it to the path of a service account JSON file."
                )

            scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
            creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
            self._service = build("sheets", "v4", credentials=creds)

        return self._service

    def get_sheet_data(self, spreadsheet_id: str, sheet_name: str) -> list[list[Any]]:
        service = self._get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=sheet_name)
            .execute()
        )
        return result.get("values", [])

    def sync_spreadsheet(self, spreadsheet: Spreadsheet) -> SyncResult:
        from django.utils import timezone

        from .models import FormResponse

        result: SyncResult = {
            "spreadsheet_id": spreadsheet.spreadsheet_id,
            "rows_synced": 0,
            "rows_created": 0,
            "rows_updated": 0,
            "errors": [],
        }

        try:
            rows = self.get_sheet_data(spreadsheet.spreadsheet_id, spreadsheet.sheet_name)
            if not rows:
                return result

            headers = rows[0]
            data_rows = rows[1:]

            for i, row in enumerate(data_rows, start=2):
                # Pad short rows so every header has a value
                padded = row + [""] * max(0, len(headers) - len(row))
                row_data = dict(zip(headers, padded))

                _, created = FormResponse.objects.update_or_create(
                    spreadsheet=spreadsheet,
                    row_index=i,
                    defaults={"data": row_data, "submitted_at": None},
                )

                result["rows_synced"] += 1
                if created:
                    result["rows_created"] += 1
                else:
                    result["rows_updated"] += 1

            spreadsheet.last_synced_at = timezone.now()
            spreadsheet.save(update_fields=["last_synced_at"])

        except Exception as exc:
            logger.exception(
                "Error syncing spreadsheet %s", spreadsheet.spreadsheet_id
            )
            result["errors"].append(str(exc))

        return result
