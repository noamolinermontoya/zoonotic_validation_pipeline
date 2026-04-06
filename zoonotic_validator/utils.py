# UTILIDADES PARA LA VALIDACIÓN DE DATOS ZOONÓTICOS
# Este módulo contiene funciones de utilidad que son utilizadas en diferentes partes del pipeline de validación de datos zoonóticos. 
# Estas funciones incluyen tareas comunes como 
    # la normalización de texto, 
    # la validación de formatos numéricos, 
    # y la clasificación de errores de formato numérico. 
# Al centralizar estas funciones en un módulo separado, se promueve la reutilización del código y se mejora la mantenibilidad del pipeline en general.

import re
from typing import Any

import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame: # Esta función devuelve una copia del DataFrame con los nombres de las columnas normalizados, es decir, con los espacios en blanco eliminados al principio y al final. Esto ayuda a prevenir falsos negativos en las validaciones causados por espacios accidentales en los encabezados de las columnas del Excel.
    """Return a copy of the DataFrame with stripped column names.

    This prevents false negatives caused by accidental leading or trailing
    spaces in Excel headers.
    """
    normalized_df = df.copy()
    normalized_df.columns = [str(column).strip() for column in normalized_df.columns]
    return normalized_df 


def is_empty(value: Any) -> bool: # Esta función devuelve True si el valor proporcionado se considera vacío, lo que incluye valores nulos (NaN) y cadenas de texto que están vacías o contienen solo espacios en blanco. Esta función es útil para las validaciones que requieren verificar si un campo obligatorio está presente o si un campo opcional tiene un valor significativo.
    """Return True when a cell should be treated as empty."""
    if pd.isna(value):
        return True
    return isinstance(value, str) and value.strip() == ""


def normalize_text(value: Any) -> str: # Esta función convierte un valor a su representación en texto, eliminando los espacios en blanco al principio y al final. Si el valor es None, devuelve una cadena vacía. Esta función es útil para las validaciones que necesitan comparar o analizar el contenido de las celdas como texto, asegurando que los valores se traten de manera consistente independientemente de su tipo original.
    """Convert a value to a trimmed string representation."""
    if value is None:
        return ""
    return str(value).strip()


def is_valid_numeric_text(value: Any, allow_decimal: bool = True) -> bool: # Esta función devuelve True si el valor proporcionado es un texto que representa un número válido según las reglas definidas. Las reglas incluyen la prohibición de comas, la no aceptación de separadores de miles, y la restricción de decimales a un único punto cuando allow_decimal es True. Esta función es útil para validar campos que deben contener números, asegurando que el formato sea correcto y evitando errores comunes relacionados con la representación numérica en texto.
    """Validate the textual format of a numeric cell.

    Rules:
    - commas are never allowed
    - thousand separators are not allowed
    - decimals are only allowed with a single dot when allow_decimal=True
    - integer-only fields must contain digits only

    Examples considered valid:
    - 1000
    - 12.5
    - 0.75

    Examples considered invalid:
    - 1,000
    - 1.000
    - 128,825
    - 1,000.50
    - 1.000,50
    """
    if pd.isna(value):
        return True

    text = str(value).strip()
    if text == "":
        return True

    if "," in text:
        return False

    if not allow_decimal:
        return bool(re.fullmatch(r"\d+", text))

    if not re.fullmatch(r"\d+(\.\d+)?", text):
        return False

    if "." in text:
        integer_part, decimal_part = text.split(".", 1)
        if len(decimal_part) == 3 and len(integer_part) >= 1:
            return False

    return True


# Esta función devuelve un mensaje de error específico para problemas de formato numérico, dependiendo de la naturaleza del error detectado. 
# Analiza el valor proporcionado y determina si contiene comas, si tiene un formato que sugiere el uso incorrecto de puntos como separadores de miles, o si se han incluido decimales en un campo que no los permite. 
# El mensaje devuelto es una explicación clara y orientada al usuario sobre cómo corregir el formato numérico para cumplir con las reglas de validación establecidas.
def classify_numeric_format_error(value: Any, allow_decimal: bool = True) -> str:
    """Return a user-friendly explanation for a numeric format issue."""
    text = normalize_text(value)

    if "," in text:
        return (
            "El valor numérico no puede llevar comas. "
            "Quite los separadores de miles y deje solo dígitos; "
            "si hay decimales, use un punto."
        )

    if "." in text and allow_decimal:
        integer_part, decimal_part = text.split(".", 1)
        if len(decimal_part) == 3 and integer_part.isdigit():
            return (
                "El valor parece usar un punto como separador de miles. "
                "Quite el separador de miles. Solo se admite punto para decimales."
            )

    if "." in text and not allow_decimal:
        return (
            "Este campo debe contener un número entero sin separadores. "
            "No se permiten decimales ni separadores de miles."
        )

    return (
        "El formato numérico no es válido. Use solo dígitos y, "
        "si el campo admite decimales, un único punto decimal."
    )
