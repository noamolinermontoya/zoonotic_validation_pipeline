# config.py --> CONFIGURACIÓN CENTRALIZADA PARA EL PIPELINE DE VALIDACIÓN DE DATOS ZOONÓTICOS
# Este módulo define la clase ValidationConfig, que centraliza la configuración de las reglas de validación para el pipeline. 
# Esto permite mantener las reglas de negocio en un solo lugar, facilitando su mantenimiento y actualización a lo largo del tiempo.

from dataclasses import dataclass, field # Importamos dataclass y field para definir la clase de configuración de manera clara y estructurada.
from typing import List, Optional # Importamos List y Optional para definir los tipos de las variables de configuración, lo que mejora la legibilidad y el mantenimiento del código.

@dataclass(frozen=True)
class ValidationConfig:
    """Central business configuration for the validation pipeline.

    Any rule expected to change over time should ideally live here instead
    of being hardcoded inside multiple functions.
    """

    required_columns: List[str] = field(default_factory=lambda: [
        "recId",
        "repYear",
        "repCountry",
        "lang",
        "zoonosis_param",
        "matrix",
        "sampStage",
        "sampOrig",
        "sampType",
        "sampContext",
        "sampler",
        "progSampStrategy",
        "sampUnit",
        "sampWeight",
        "sampWeightUnit",
        "totUnitsTested",
        "totUnitsPositive",
        "anMethCode",
    ])
    exact_rep_country: str = "ES | Spain"
    exact_lang: str = "EN | English"
    expected_year: Optional[int] = 2025 # El año esperado para el campo repYear, se puede actualizar según las necesidades de validación. Si se establece como None, no se aplicará una validación específica para el año.
    prohibited_text_values: List[str] = field(default_factory=lambda: ["Unspecified"]) # Lista de valores de texto que no están permitidos en los campos de texto, se puede ampliar según las necesidades de validación.
    numeric_columns_allow_decimals: List[str] = field(default_factory=lambda: ["sampWeight"]) # Lista de columnas numéricas que permiten decimales, se puede actualizar según las necesidades de validación. Las columnas que no estén en esta lista se validarán como enteros sin decimales.
    numeric_columns_integers_only: List[str] = field(default_factory=lambda: [
        "totUnitsTested",
        "totUnitsPositive",
    ])
    recid_pattern_hint: str = "CCAA_AGENTE_001" #Un patrón de ejemplo para el campo recId, consta de tres partes separadas por guiones bajos: una parte que representa la comunidad autónoma (CCAA), seguida de una parte que representa el agente zoonótico (AGENTE), y finalmente un número secuencial (001). Este patrón puede ser utilizado como referencia para validar el formato del campo recId en el Excel, asegurando que siga una estructura coherente y predecible. Se puede actualizar o ampliar este patrón según las necesidades específicas de validación.


CONFIG = ValidationConfig() # Creamos una instancia de la configuración que se puede importar y utilizar en todo el pipeline para acceder a las reglas de validación centralizadas.
