from typing import Any

from typing_extensions import TypedDict


class RowData(TypedDict):
    row_index: int
    data: dict[str, Any]
    submitted_at: str | None


class SyncResult(TypedDict):
    spreadsheet_id: str
    rows_synced: int
    rows_created: int
    rows_updated: int
    errors: list[str]
