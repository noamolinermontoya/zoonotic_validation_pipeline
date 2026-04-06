# pipeline.py --> FUNCIONES PRINCIPALES DEL PIPELINE DE VALIDACIÓN DE DATOS ZOONÓTICOS
# Este módulo contiene las funciones principales que coordinan la ejecución del pipeline de validación de datos zoonóticos. 
# Incluye la función run_validation_pipeline, que es el punto de entrada para ejecutar todo: el proceso de validación, desde la carga del Excel, pasando por la ejecución de las validaciones, hasta la generación de los archivos de salida con los resultados.

import pandas as pd

from .config import ValidationConfig
from .outputs import create_marked_excel, create_word_report, save_errors_to_excel
from .validators import run_general_validations


def load_excel(input_file: str, sheet_name=0):
    """Load the Excel file and return the DataFrame plus the resolved sheet name."""
    dataframe = pd.read_excel(input_file, sheet_name=sheet_name)
    if isinstance(sheet_name, int):
        workbook = pd.ExcelFile(input_file)
        actual_sheet_name = workbook.sheet_names[sheet_name]
    else:
        actual_sheet_name = sheet_name
    return dataframe, actual_sheet_name


def run_validation_pipeline(
    input_file: str,
    sheet_name,
    errors_output_file: str,
    marked_excel_output_file: str,
    word_output_file: str,
    config: ValidationConfig,
):
    """Execute the complete validation pipeline end to end.

    This is the single function that coordinates:
    1. Excel loading
    2. Validation execution
    3. Output generation
    """
    dataframe, actual_sheet_name = load_excel(input_file, sheet_name=sheet_name)
    errors_df = run_general_validations(
        dataframe,
        sheet_name=actual_sheet_name,
        config=config,
    )

    save_errors_to_excel(errors_df, errors_output_file)
    create_marked_excel(
        input_file=input_file,
        sheet_name=sheet_name,
        errors_df=errors_df,
        output_file=marked_excel_output_file,
    )
    create_word_report(errors_df, word_output_file)

    return errors_df
