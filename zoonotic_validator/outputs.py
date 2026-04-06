# outputs.py --> GENERACIÓN DE FICHEROS DE SALIDA PARA EL PIPELINE DE VALIDACIÓN DE DATOS ZOONÓTICOS
# Este módulo contiene funciones para generar los archivos de salida del pipeline de validación de datos zoonóticos, incluyendo:
    # - Un Excel con los errores detectados.
    # - Una copia del Excel original con las celdas que contienen errores resaltadas.
    # - Un informe en Word que resume los errores encontrados y proporciona detalles para su revisión.

from collections import Counter
from pathlib import Path

import pandas as pd
from docx import Document
from docx.shared import Inches
from openpyxl import load_workbook
from openpyxl.styles import PatternFill


ERROR_FILL = PatternFill(fill_type="solid", fgColor="FFF2CC")


def save_errors_to_excel(errors_df: pd.DataFrame, output_file: str) -> None:
    """Save the error table as a simple Excel file."""
    errors_df.to_excel(output_file, index=False)


def create_marked_excel(
    input_file: str,
    sheet_name,
    errors_df: pd.DataFrame,
    output_file: str,
) -> None:
    """Create a copy of the original workbook and highlight invalid cells.

    Only cell-level errors can be highlighted because structural errors
    such as missing columns do not point to a specific existing cell.
    """
    workbook = load_workbook(input_file)
    worksheet = workbook[workbook.sheetnames[sheet_name] if isinstance(sheet_name, int) else sheet_name]

    if not errors_df.empty:
        cell_level_errors = errors_df[errors_df["is_cell_level"] == True]
        for _, error in cell_level_errors.iterrows():
            if pd.notna(error.get("excel_column")) and pd.notna(error.get("excel_row")):
                worksheet.cell(
                    row=int(error["excel_row"]),
                    column=int(error["excel_column"]),
                ).fill = ERROR_FILL

    workbook.save(output_file)


def create_word_report(errors_df: pd.DataFrame, output_file: str) -> None:
    """Generate a clear Word report with summary and detailed tables."""
    document = Document()
    document.add_heading("Informe de validación del Excel", level=1)

    if errors_df.empty:
        document.add_paragraph("No se han detectado errores en las validaciones generales.")
        document.save(output_file)
        return

    document.add_paragraph(
        "Se han detectado incidencias en la revisión general del fichero. "
        "A continuación se muestra un resumen y el detalle de lo que conviene revisar."
    )

    document.add_heading("Resumen", level=2)
    summary_table = document.add_table(rows=1, cols=2)
    summary_table.style = "Table Grid"
    header_cells = summary_table.rows[0].cells
    header_cells[0].text = "Concepto"
    header_cells[1].text = "Valor"

    row = summary_table.add_row().cells
    row[0].text = "Número total de incidencias"
    row[1].text = str(len(errors_df))

    structural_count = int((errors_df["is_cell_level"] == False).sum())
    cell_count = int((errors_df["is_cell_level"] == True).sum())

    row = summary_table.add_row().cells
    row[0].text = "Incidencias estructurales"
    row[1].text = str(structural_count)

    row = summary_table.add_row().cells
    row[0].text = "Incidencias en celdas concretas"
    row[1].text = str(cell_count)

    document.add_heading("Resumen por tipo de error", level=2)
    grouped = Counter(errors_df["error_code"])
    grouped_table = document.add_table(rows=1, cols=2)
    grouped_table.style = "Table Grid"
    grouped_header = grouped_table.rows[0].cells
    grouped_header[0].text = "Código"
    grouped_header[1].text = "Número de casos"

    for code, count in sorted(grouped.items()):
        row = grouped_table.add_row().cells
        row[0].text = str(code)
        row[1].text = str(count)

    document.add_heading("Detalle de incidencias", level=2)
    detail_table = document.add_table(rows=1, cols=6)
    detail_table.style = "Table Grid"
    detail_header = detail_table.rows[0].cells
    detail_header[0].text = "Fila Excel"
    detail_header[1].text = "Campo"
    detail_header[2].text = "Valor detectado"
    detail_header[3].text = "Código"
    detail_header[4].text = "Incidencia"
    detail_header[5].text = "Qué revisar"

    for _, error in errors_df.iterrows():
        row = detail_table.add_row().cells
        row[0].text = str(error["excel_row"])
        row[1].text = str(error["field"])
        row[2].text = "" if pd.isna(error["value"]) else str(error["value"])
        row[3].text = str(error["error_code"])
        row[4].text = str(error["message"])
        row[5].text = (
            "Revise la columna y corrija el valor indicado."
            if bool(error["is_cell_level"])
            else "Revise la estructura general del fichero o las columnas esperadas."
        )

    document.save(output_file)
