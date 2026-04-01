from zoonotic_validator.config import CONFIG
from zoonotic_validator.pipeline import run_validation_pipeline


# ============================================================
# Instalación recomendada si hace falta:
# pip install pandas openpyxl python-docx notebook ipykernel
# ============================================================

input_file = "mi_excel_zoonoticos.xlsx"
sheet_to_validate = 0
errors_output_file = "errores_validaciones_generales.xlsx"
marked_excel_output_file = "mi_excel_zoonoticos_marcado.xlsx"
word_output_file = "informe_errores_validacion.docx"

df_errors = run_validation_pipeline(
    input_file=input_file,
    sheet_name=sheet_to_validate,
    errors_output_file=errors_output_file,
    marked_excel_output_file=marked_excel_output_file,
    word_output_file=word_output_file,
    config=CONFIG,
)

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
