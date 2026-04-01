import re
from typing import Any

import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with stripped column names.

    This prevents false negatives caused by accidental leading or trailing
    spaces in Excel headers.
    """
    normalized_df = df.copy()
    normalized_df.columns = [str(column).strip() for column in normalized_df.columns]
    return normalized_df


def is_empty(value: Any) -> bool:
    """Return True when a cell should be treated as empty."""
    if pd.isna(value):
        return True
    return isinstance(value, str) and value.strip() == ""


def normalize_text(value: Any) -> str:
    """Convert a value to a trimmed string representation."""
    if value is None:
        return ""
    return str(value).strip()


def is_valid_numeric_text(value: Any, allow_decimal: bool = True) -> bool:
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
