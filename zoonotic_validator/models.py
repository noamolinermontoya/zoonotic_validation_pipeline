from dataclasses import dataclass, asdict
from typing import Optional, Any, Dict


@dataclass
class ValidationError:
    """Represents a validation issue detected in the Excel file."""

    excel_row: Any
    field: str
    value: Any
    error_code: str
    message: str
    sheet_name: str
    is_cell_level: bool
    excel_column: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation error to a plain dictionary for DataFrame export."""
        return asdict(self)
