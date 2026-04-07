# main.py 
# Este script es el punto de entrada para ejecutar el pipeline de validación de datos zoonóticos.
# Configura los nombres de los archivos de entrada y salida, y luego llama a la función principal del pipeline.

import os
import shutil
from datetime import datetime

from zoonotic_validator.config import CONFIG
from zoonotic_validator.pipeline import run_validation_pipeline


# ============================================================
# Instalación recomendada si hace falta:
# pip install pandas openpyxl python-docx notebook ipykernel
# ============================================================

script_dir = os.path.dirname(__file__)
input_file = os.path.join(script_dir, "mi_excel_zoonoticos.xlsx")  # Reemplace con el nombre de su archivo de Excel a validar
sheet_to_validate = 0  # Puede ser el nombre de la hoja o su índice (0 para la primera hoja)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = os.path.join(script_dir, f"resultados_{timestamp}")

errors_output_file = os.path.join(output_folder, "errores_validaciones_generales.xlsx")
marked_excel_output_file = os.path.join(output_folder, "mi_excel_zoonoticos_marcado.xlsx")
word_output_file = os.path.join(output_folder, "informe_errores_validacion.docx")

# Crear la carpeta antes del pipeline (las funciones de salida la necesitan)
# Si hay error, se borrará automáticamente
os.makedirs(output_folder, exist_ok=True)

try:
    df_errors = run_validation_pipeline(
        input_file=input_file,
        sheet_name=sheet_to_validate,
        errors_output_file=errors_output_file,
        marked_excel_output_file=marked_excel_output_file,
        word_output_file=word_output_file,
        config=CONFIG,
    )
except Exception:
    # Si hay error, borra la carpeta de resultados
    shutil.rmtree(output_folder, ignore_errors=True)
    raise

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
