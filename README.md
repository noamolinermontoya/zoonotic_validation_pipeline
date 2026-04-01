# Zoonotic Validation Pipeline

Proyecto en Python para validar las **validaciones generales** de un Excel de agentes zoonóticos.

## Qué hace
- Valida columnas obligatorias
- Comprueba `repCountry = ES | Spain`
- Comprueba `lang = EN | English`
- Permite configurar `repYear`
- Valida formato numérico:
  - enteros sin separadores de miles
  - decimales solo con punto (`.`)
- Genera tres outputs:
  - `errores_validaciones_generales.xlsx`
  - `mi_excel_zoonoticos_marcado.xlsx`
  - `informe_errores_validacion.docx`

## Estructura
- `main.py`: punto de entrada
- `zoonotic_validator/config.py`: configuración central
- `zoonotic_validator/models.py`: modelo de error
- `zoonotic_validator/utils.py`: utilidades comunes
- `zoonotic_validator/validators.py`: reglas de validación
- `zoonotic_validator/outputs.py`: generación de ficheros de salida
- `zoonotic_validator/pipeline.py`: ejecución completa del pipeline

## Instalación
```bash
pip install -r requirements.txt
```

## Ejecución
Edita `main.py` si quieres cambiar:
- `input_file`
- `sheet_to_validate`
- nombres de los outputs

Luego ejecuta:

```bash
python main.py
```

## Columnas esperadas
```text
recId, repYear, repCountry, lang, zoonosis_param, matrix, sampStage,
sampOrig, sampType, sampContext, sampler, progSampStrategy, sampUnit,
sampWeight, sampWeightUnit, totUnitsTested, totUnitsPositive, anMethCode
```
