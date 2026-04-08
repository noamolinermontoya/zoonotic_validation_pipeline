# pipeline.py --> FUNCIONES PRINCIPALES DEL PIPELINE DE VALIDACIÓN DE DATOS ZOONÓTICOS
# Este módulo contiene las funciones principales que coordinan la ejecución del pipeline de validación de datos zoonóticos. 
# Incluye la función run_validation_pipeline, que es el punto de entrada para ejecutar todo: el proceso de validación, desde la carga del Excel, pasando por la ejecución de las validaciones, hasta la generación de los archivos de salida con los resultados.

import pandas as pd
import re
from openpyxl import load_workbook

from .config import ValidationConfig # Importamos la clase ValidationConfig para acceder a la configuración centralizada de las validaciones, lo que permite que el pipeline se ejecute de manera consistente y flexible según las reglas definidas en la configuración.
from .models import ValidationError # Importamos la clase ValidationError para estandarizar la forma en que se registran los errores detectados durante las validaciones, lo que facilita su manejo y exportación a los archivos de salida.
from .outputs import create_marked_excel, create_word_report, save_errors_to_excel
from .validators import run_general_validations

# Esta función carga el archivo Excel, ejecuta las validaciones generales, y luego genera los archivos de salida correspondientes: un Excel con los errores detectados, una copia del Excel original con las celdas que contienen errores resaltadas, y un informe en Word que resume los errores encontrados. El resultado de esta función es un DataFrame con los errores detectados en las validaciones generales, que se puede utilizar para revisar los resultados o para otros fines posteriores.
def load_excel(input_file: str, sheet_name=0):
    """Load the Excel file and return the DataFrame plus the resolved sheet name."""
    dataframe = pd.read_excel(input_file, sheet_name=sheet_name)
    if isinstance(sheet_name, int):
        workbook = pd.ExcelFile(input_file)
        actual_sheet_name = workbook.sheet_names[sheet_name]
    else:
        actual_sheet_name = sheet_name
    return dataframe, actual_sheet_name


def extract_year_from_mapping_options(input_file: str) -> int:
    """Extract the year from cell A1 (possibly merged) of the 'Mapping_Options' sheet (first sheet).
    
    The cell contains text like: "EFSA's Manual Mapping Tool (version 4.0 2025 data submission)"
    Handles merged cells by reading with openpyxl.
    
    Returns the year as an integer, or None if not found or invalid.
    """
    try:
        # Si es archivo .xlsx, usar openpyxl para manejar celdas fusionadas
        if input_file.lower().endswith('.xlsx'):
            try:
                workbook = load_workbook(input_file)
                first_sheet = workbook.active
                cell_value = first_sheet['A1'].value
            except Exception:
                cell_value = None
        else:
            cell_value = None
        
        # Si no se leyó con openpyxl, intentar con pandas (lee toda la primera fila)
        if cell_value is None:
            mapping_sheet = pd.read_excel(input_file, sheet_name=0, header=None, nrows=1)
            
            # Buscamos el texto del año en cualquier celda de la primera fila
            for cell in mapping_sheet.values[0]:
                if pd.notna(cell):
                    cell_value = str(cell)
                    if 'data' in cell_value.lower() or 'submission' in cell_value.lower():
                        break
        
        if cell_value is not None:
            cell_text = str(cell_value)
            
            # Reemplazar saltos de línea y espacios múltiples
            cell_text_clean = " ".join(cell_text.split())
            
            # Buscar un patrón como "4.0 XXXX data" donde XXXX es el año (4 dígitos)
            match = re.search(r'4\.0\s+(\d{4})\s+data', cell_text_clean, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                return year
            
            # Si no encuentra el patrón exacto, intenta buscar cualquier año entre 1900 y 2100
            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', cell_text_clean)
            if year_match:
                year = int(year_match.group(1))
                return year
    except (IndexError, ValueError, TypeError):
        pass
    
    return None
# ============================================================
# Esta función es el punto de entrada para ejecutar todo el pipeline de validación de datos zoonóticos. Coordina la carga del Excel, la ejecución de las validaciones generales, y la generación de los archivos de salida con los resultados. El resultado de esta función es un DataFrame con los errores detectados en las validaciones generales, que se puede utilizar para revisar los resultados o para otros fines posteriores.
def run_validation_pipeline( 
    input_file: str, # El nombre del archivo Excel que se va a validar. Este archivo debe estar en el mismo directorio que el script o se debe proporcionar la ruta completa.
    sheet_name, # El nombre o índice de la hoja del Excel que se va a validar. Puede ser un número (0 para la primera hoja) o el nombre exacto de la hoja.
    errors_output_file: str, # El nombre del archivo Excel donde se guardarán los errores detectados en las validaciones generales. Este archivo contendrá una tabla con todos los errores encontrados, incluyendo detalles como la fila, columna, tipo de error, mensaje descriptivo, etc.
    marked_excel_output_file: str, # El nombre del archivo Excel donde se guardará una copia del original con las celdas que contienen errores resaltadas.
    word_output_file: str, # El nombre del archivo Word donde se guardará el informe de resumen de los errores detectados.
    config: ValidationConfig, # La configuración de validación que se utilizará para ejecutar las validaciones generales. Esta configuración incluye las reglas de validación, los nombres de las columnas esperadas, y otros parámetros necesarios para aplicar las validaciones de manera consistente.
):
    """Execute the complete validation pipeline end to end.

    This is the single function that coordinates:
    1. Excel loading
    2. Year extraction from Mapping_Options sheet
    3. Validation execution
    4. Output generation
    """
    # Extraer el año de la primera hoja (Mapping_Options)
    extracted_year = extract_year_from_mapping_options(input_file)
    
    # Crear una nueva instancia de config con el año extraído
    if extracted_year is not None:
        # Crear un nuevo config con el año extraído
        config_with_year = ValidationConfig(
            required_columns=config.required_columns,
            exact_rep_country=config.exact_rep_country,
            exact_lang=config.exact_lang,
            expected_year=extracted_year,  # Usar el año extraído
            prohibited_text_values=config.prohibited_text_values,
            numeric_columns_allow_decimals=config.numeric_columns_allow_decimals,
            numeric_columns_integers_only=config.numeric_columns_integers_only,
            recid_pattern_hint=config.recid_pattern_hint,
        )
    else:
        config_with_year = config
    
    dataframe, actual_sheet_name = load_excel(input_file, sheet_name=sheet_name)
    errors_df = run_general_validations(
        dataframe,
        sheet_name=actual_sheet_name,
        config=config_with_year,
    )
# Después de ejecutar las validaciones generales, se generan los archivos de salida correspondientes: un Excel con los errores detectados, una copia del Excel original con las celdas que contienen errores resaltadas, y un informe en Word que resume los errores encontrados. El resultado de esta función es un DataFrame con los errores detectados en las validaciones generales, que se puede utilizar para revisar los resultados o para otros fines posteriores.
    save_errors_to_excel(errors_df, errors_output_file)
    create_marked_excel(
        input_file=input_file, 
        sheet_name=sheet_name, 
        errors_df=errors_df,
        output_file=marked_excel_output_file,
    )
    create_word_report(errors_df, word_output_file, input_file=input_file)

    return errors_df
