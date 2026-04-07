# main.py 
# Este script es el punto de entrada para ejecutar el pipeline de validación de datos zoonóticos.
# Configura los nombres de los archivos de entrada y salida, y luego llama a la función principal del pipeline.

from zoonotic_validator.config import CONFIG
from zoonotic_validator.pipeline import run_validation_pipeline


# ============================================================
# Instalación recomendada si hace falta:
# pip install pandas openpyxl python-docx notebook ipykernel
# ============================================================

input_file = "mi_excel_zoonoticos1.xlsx" # Reemplace con el nombre de su archivo de Excel a validar
sheet_to_validate = 0 # Puede ser el nombre de la hoja o su índice (0 para la primera hoja) 
errors_output_file = "errores_validaciones_generales.xlsx" # Nombre del archivo Excel donde se guardarán los errores detectados en las validaciones generales.
marked_excel_output_file = "mi_excel_zoonoticos_marcado.xlsx" # Nombre del archivo Excel que se generará como copia del original, pero con las celdas que contienen errores resaltadas para facilitar su identificación.
word_output_file = "informe_errores_validacion.docx" # Nombre del archivo Word que se generará con un informe claro y estructurado de los errores encontrados, incluyendo un resumen y una tabla detallada de los mismos.

df_errors = run_validation_pipeline(
    input_file=input_file,
    sheet_name=sheet_to_validate,
    errors_output_file=errors_output_file,
    marked_excel_output_file=marked_excel_output_file,
    word_output_file=word_output_file,
    config=CONFIG,
)
# El resultado de esta función es un DataFrame con los errores detectados en las validaciones generales. Si no se han encontrado errores, este DataFrame estará vacío. Luego se imprime un mensaje indicando el resultado de la validación y los archivos generados.

if df_errors.empty:
    print("✅ No se han encontrado errores en las validaciones generales.")
    print(f"📄 Word generado: {word_output_file}")
    print(f"📗 Excel marcado generado: {marked_excel_output_file}")
    print(f"📘 Excel de errores generado: {errors_output_file}")
else:
    print(f"⚠️ Se han encontrado {len(df_errors)} errores.")
    print(df_errors)
    print(f"📘 Excel de errores generado: {errors_output_file}")
    print(f"📗 Excel marcado generado: {marked_excel_output_file}")
    print(f"📄 Word generado: {word_output_file}")
