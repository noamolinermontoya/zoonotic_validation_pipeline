from typing import Dict, List

import pandas as pd

from .config import ValidationConfig
from .models import ValidationError
from .utils import (
    classify_numeric_format_error,
    is_empty,
    is_valid_numeric_text,
    normalize_columns,
    normalize_text,
)


def _append_error(
    errors: List[ValidationError],
    *,
    excel_row,
    field: str,
    value,
    error_code: str,
    message: str,
    sheet_name: str,
    is_cell_level: bool,
    excel_column=None,
) -> None:
    """Append a standardised validation error object to the error list."""
    errors.append(
        ValidationError(
            excel_row=excel_row,
            field=field,
            value=value,
            error_code=error_code,
            message=message,
            sheet_name=sheet_name,
            is_cell_level=is_cell_level,
            excel_column=excel_column,
        )
    )


def build_header_map(df: pd.DataFrame) -> Dict[str, int]:
    """Build a mapping from column name to 1-based Excel column position."""
    return {column: index + 1 for index, column in enumerate(df.columns)}


def validate_required_columns(
    df: pd.DataFrame,
    errors: List[ValidationError],
    config: ValidationConfig,
    sheet_name: str,
) -> None:
    """Validate that all expected columns are present in the input workbook."""
    for column in config.required_columns:
        if column not in df.columns:
            _append_error(
                errors,
                excel_row="N/A",
                field=column,
                value="",
                error_code="E001",
                message=f"Falta la columna obligatoria '{column}' en el Excel.",
                sheet_name=sheet_name,
                is_cell_level=False,
                excel_column=None,
            )


def validate_required_values(
    df: pd.DataFrame,
    errors: List[ValidationError],
    header_map: Dict[str, int],
    config: ValidationConfig,
    sheet_name: str,
) -> None:
    """Validate that required fields are not empty row by row."""
    present_columns = [column for column in config.required_columns if column in df.columns]

    for row_index, row in df.iterrows():
        excel_row = row_index + 2
        for column in present_columns:
            value = row[column]
            if is_empty(value):
                _append_error(
                    errors,
                    excel_row=excel_row,
                    field=column,
                    value=value,
                    error_code="E002",
                    message=f"El campo obligatorio '{column}' está vacío.",
                    sheet_name=sheet_name,
                    is_cell_level=True,
                    excel_column=header_map.get(column),
                )


def validate_exact_text_columns(
    df: pd.DataFrame,
    errors: List[ValidationError],
    header_map: Dict[str, int],
    config: ValidationConfig,
    sheet_name: str,
) -> None:
    """Validate business literals that must match exact fixed text."""
    exact_rules = {
        "repCountry": config.exact_rep_country,
        "lang": config.exact_lang,
    }

    for column, expected_text in exact_rules.items():
        if column not in df.columns:
            continue

        for row_index, row in df.iterrows():
            excel_row = row_index + 2
            value = row[column]
            if is_empty(value):
                continue

            if normalize_text(value) != expected_text:
                _append_error(
                    errors,
                    excel_row=excel_row,
                    field=column,
                    value=value,
                    error_code="E003",
                    message=f"El campo '{column}' debe ser exactamente '{expected_text}'.",
                    sheet_name=sheet_name,
                    is_cell_level=True,
                    excel_column=header_map.get(column),
                )


def validate_expected_year(
    df: pd.DataFrame,
    errors: List[ValidationError],
    header_map: Dict[str, int],
    config: ValidationConfig,
    sheet_name: str,
) -> None:
    """Validate repYear when the year is configured.

    The rule can be disabled by setting expected_year=None in the config.
    """
    if config.expected_year is None or "repYear" not in df.columns:
        return

    for row_index, row in df.iterrows():
        excel_row = row_index + 2
        value = row["repYear"]

        if is_empty(value):
            continue

        try:
            if int(float(value)) != int(config.expected_year):
                raise ValueError
        except Exception:
            _append_error(
                errors,
                excel_row=excel_row,
                field="repYear",
                value=value,
                error_code="E004",
                message=f"El campo 'repYear' debe ser {config.expected_year}.",
                sheet_name=sheet_name,
                is_cell_level=True,
                excel_column=header_map.get("repYear"),
            )


def validate_prohibited_text_values(
    df: pd.DataFrame,
    errors: List[ValidationError],
    header_map: Dict[str, int],
    config: ValidationConfig,
    sheet_name: str,
) -> None:
    """Validate generic text values that are forbidden across the workbook."""
    prohibited_values = {value.lower() for value in config.prohibited_text_values}

    for column in df.columns:
        for row_index, row in df.iterrows():
            excel_row = row_index + 2
            value = row[column]
            if is_empty(value):
                continue

            if normalize_text(value).lower() in prohibited_values:
                _append_error(
                    errors,
                    excel_row=excel_row,
                    field=column,
                    value=value,
                    error_code="E005",
                    message=(
                        f"El valor '{value}' no está permitido en el campo '{column}'."
                    ),
                    sheet_name=sheet_name,
                    is_cell_level=True,
                    excel_column=header_map.get(column),
                )


def validate_numeric_columns(
    df: pd.DataFrame,
    errors: List[ValidationError],
    header_map: Dict[str, int],
    config: ValidationConfig,
    sheet_name: str,
) -> None:
    """Validate numeric business rules with clear and centralised logic."""
    numeric_rules = {
        **{column: True for column in config.numeric_columns_allow_decimals},
        **{column: False for column in config.numeric_columns_integers_only},
    }

    for column, allow_decimal in numeric_rules.items():
        if column not in df.columns:
            continue

        for row_index, row in df.iterrows():
            excel_row = row_index + 2
            value = row[column]

            if is_empty(value):
                continue

            if not is_valid_numeric_text(value, allow_decimal):
                _append_error(
                    errors,
                    excel_row=excel_row,
                    field=column,
                    value=value,
                    error_code="E006",
                    message=classify_numeric_format_error(value, allow_decimal),
                    sheet_name=sheet_name,
                    is_cell_level=True,
                    excel_column=header_map.get(column),
                )


def run_general_validations(
    df: pd.DataFrame,
    sheet_name: str,
    config: ValidationConfig,
) -> pd.DataFrame:
    """Execute the full set of general validations and return a DataFrame.

    The function acts as the validation engine and stays focused on
    identifying issues only. Output generation is handled elsewhere.
    """
    working_df = normalize_columns(df)
    header_map = build_header_map(working_df)
    errors: List[ValidationError] = []

    # Version validation intentionally omitted until the business rule is defined.

    validate_required_columns(working_df, errors, config, sheet_name)
    validate_required_values(working_df, errors, header_map, config, sheet_name)
    validate_exact_text_columns(working_df, errors, header_map, config, sheet_name)
    validate_expected_year(working_df, errors, header_map, config, sheet_name)
    validate_prohibited_text_values(working_df, errors, header_map, config, sheet_name)
    validate_numeric_columns(working_df, errors, header_map, config, sheet_name)

    return pd.DataFrame([error.to_dict() for error in errors])
