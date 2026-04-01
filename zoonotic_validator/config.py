from dataclasses import dataclass, field
from typing import List, Optional


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
    expected_year: Optional[int] = 2025
    prohibited_text_values: List[str] = field(default_factory=lambda: ["Unspecified"])
    numeric_columns_allow_decimals: List[str] = field(default_factory=lambda: ["sampWeight"])
    numeric_columns_integers_only: List[str] = field(default_factory=lambda: [
        "totUnitsTested",
        "totUnitsPositive",
    ])
    recid_pattern_hint: str = "CCAA_AGENTE_001"


CONFIG = ValidationConfig()
