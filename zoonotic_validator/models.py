# models.py --> MODELOS DE ERROR PARA EL PIPELINE DE VALIDACIÓN DE DATOS ZOONÓTICOS
# Este módulo define la clase ValidationError, que representa un error detectado durante la validación de los datos en el Excel.
# Esta clase se utiliza para estandarizar la forma en que se registran los errores, facilitando su manejo, exportación y generación de informes posteriores.

from dataclasses import dataclass, asdict # Importamos dataclass para definir la clase de error de manera clara y estructurada, y asdict para convertir las instancias de error en diccionarios fácilmente exportables.
from typing import Optional, Any, Dict


@dataclass
class ValidationError:
    """Represents a validation issue detected in the Excel file."""

    excel_row: Any # La fila del Excel donde se detectó el error, puede ser un número o cualquier identificador que ayude a localizar el error. Se define como Any para permitir flexibilidad en la forma de identificar la fila (puede ser un número, un string con un identificador, etc.).
    field: str # El nombre del campo o columna relacionado con el error, se define como string para describir claramente qué campo tiene el problema.
    value: Any # El valor que causó el error, se define como Any para permitir cualquier tipo de valor (número, texto, fecha, etc.) que pueda estar presente en el Excel y causar un error de validación.
    error_code: str # Un código único que identifica el tipo de error.
    message: str # Un mensaje descriptivo del error.
    sheet_name: str # El nombre de la hoja del Excel donde se detectó el error.
    is_cell_level: bool # Un indicador de si el error es a nivel de celda o no.
    excel_column: Optional[int] = None # La columna del Excel donde se detectó el error, si aplica. Se define como Optional[int] porque no todos los errores estarán relacionados con una celda específica (por ejemplo, un error de estructura como la falta de una columna no tendrá una columna específica asociada).

    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation error to a plain dictionary for DataFrame export.""" # Esta función convierte la instancia de ValidationError en un diccionario plano, lo que facilita su exportación a formatos como Excel o su inclusión en informes. Utiliza asdict para convertir automáticamente todos los campos de la dataclass en un diccionario.
        return asdict(self)
