# models.py --> MODELOS DE ERROR PARA EL PIPELINE DE VALIDACIÓN DE DATOS ZOONÓTICOS
# Este módulo define la clase ValidationError, que representa un error detectado durante la validación de los datos en el Excel.
# Esta clase se utiliza para estandarizar la forma en que se registran los errores, facilitando su manejo, exportación y generación de informes posteriores.

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
